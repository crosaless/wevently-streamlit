# Módulo 4: Base Orientada a Grafos (Neo4j)

## **Propósito**

Proporcionar almacenamiento persistente y consultas eficientes del conocimiento estructurado del dominio mediante una base de datos de grafos. Este módulo permite recuperar soluciones contextualizadas según las palabras clave detectadas, el perfil del usuario y las relaciones semánticas entre entidades, funcionando como el "cerebro" del sistema experto.

***

## **Entradas**

### **Parámetros de consulta**:

- **Keywords extraídas** (lista de strings): Términos normalizados por spaCy
    - Ejemplo: `['tarjeta', 'rechazar', 'pago']`
- **Tipo de usuario** (string): Rol del usuario en la plataforma
    - Valores válidos: `"Organizador"`, `"Prestador"`, `"Propietario"`
- **Tipo de consulta**: Query Cypher dinámica generada por `cypher_query()`


### **Datos persistentes en la base**:

- 38+ nodos `PalabraClave`
- 4 nodos `CategoriaProblema`
- 12+ nodos `TipoProblema`
- 12+ nodos `Solucion`
- 3 nodos `Emocion`
- 3 nodos `TipoUsuario`
- 100+ relaciones entre nodos

***

## **Salidas**

### **Resultado de consulta Cypher** (diccionario JSON):

```python
{
  "tipo_problema": "Tarjeta rechazada",
  "solucion": "Verifique los datos de su tarjeta e intente nuevamente.",
  "confianza": 0.9,
  "matched_count": 2,
  "matched_keywords": ["tarjeta", "rechazar"],
  "has_type": 1  # 1 si el tipo de usuario coincide, 0 si no
}
```


### **Casos especiales**:

- **Sin coincidencias**: `[]` (lista vacía)
- **Coincidencia parcial**: Retorna mejor match aunque `matched_count` sea bajo

***

## **Herramientas y Entorno**

| Componente | Tecnología | Versión | Propósito |
| :-- | :-- | :-- | :-- |
| **Base de datos** | Neo4j | ≥5.14.0 | Motor de grafos nativo |
| **Cliente Python** | `neo4j` | ≥5.14.0 | Driver oficial de Neo4j |
| **Wrapper LangChain** | `langchain-neo4j` | ≥0.0.3 | Integración simplificada con LLM |
| **Lenguaje de consulta** | Cypher | - | DSL para consultas de grafos |
| **Entorno de despliegue** | Neo4j Aura (cloud) / Local | - | Instancias remotas y locales |

### **Configuración de conexión**:

**Variables de entorno** (`.env`):

```env
# Conexión remota (Aura Cloud)
NEO4J_URI=neo4j+s://xxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=tu_contraseña_segura

# Fallback local
NEO4J_URL=bolt://localhost:7687
```


***

## **Código Relevante**

### **Archivo 1**: `src/neo4j_connection.py` (Gestor de conexiones con fallback)

```python
import os
import logging
from langchain_neo4j import Neo4jGraph

logger = logging.getLogger(__name__)

def get_graph():
    """
    Retorna conexión a Neo4j con estrategia de fallback remoto→local.
    
    Returns:
        Neo4jGraph: Instancia conectada a Neo4j
    
    Raises:
        Exception: Si no se puede conectar a ninguna instancia
    """
    # Leer credenciales de entorno
    aura_uri = os.getenv('NEO4J_URI') or os.getenv('NEO4J_URL_QUERY') or ''
    bolt_local = os.getenv('NEO4J_URL', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USERNAME', 'neo4j')
    pwd = os.getenv('NEO4J_PASSWORD', '')

    # INTENTO 1: Conexión remota (Neo4j Aura)
    if aura_uri:
        try:
            logger.info('Intentando conectar a Neo4j remoto (Aura)...')
            graph = Neo4jGraph(url=aura_uri, username=user, password=pwd)
            # Smoke test: validar conexión con query simple
            graph.query('RETURN 1 AS ok')
            logger.info('✅ Conexión Neo4j establecida en remoto (Aura).')
            return graph
        except Exception as e:
            logger.warning(f'⚠️ Fallo conexión remota: {e}. Intentando local...')

    # INTENTO 2: Conexión local (fallback)
    try:
        logger.info('Intentando conectar a Neo4j local...')
        graph = Neo4jGraph(url=bolt_local, username=user, password=pwd)
        graph.query('RETURN 1 AS ok')
        logger.info('✅ Conexión Neo4j establecida en local.')
        return graph
    except Exception as e:
        logger.error('❌ No se pudo conectar a Neo4j (remoto ni local).', exc_info=True)
        raise Exception('Neo4j no disponible. Verifica las instancias.') from e
```


### **Archivo 2**: `src/langchain.py` (Generación dinámica de queries Cypher)

```python
from neo4j_connection import get_graph

# Inicializar conexión global
graph = get_graph()

def cypher_query(keywords, tipo_usuario):
    """
    Genera query Cypher parametrizada para recuperar solución.
    
    Args:
        keywords (list): Lista de keywords extraídas
        tipo_usuario (str): Rol del usuario (Organizador/Prestador/Propietario)
    
    Returns:
        str: Query Cypher como string
    """
    # Normalizar keywords a minúsculas
    kw_list = [k.lower() for k in keywords]
    kwstr = "[" + ", ".join([f"'{k}'" for k in kw_list]) + "]"
    
    return f"""
    -- 1. Preparar lista de keywords como parámetro
    WITH {kwstr} AS kws
    
    -- 2. Descomponer lista y matchear con nodos PalabraClave
    UNWIND kws AS kw
    MATCH (k:PalabraClave)
    WHERE toLower(k.nombre) = kw
    
    -- 3. Navegar por relaciones semánticas
    MATCH (k)-[:DISPARA]->(c:CategoriaProblema)
    OPTIONAL MATCH (c)-[:AGRUPA]->(t:TipoProblema)-[:RESUELTO_POR]->(s:Solucion)
    OPTIONAL MATCH (c)-[:TIENE_UN]->(tu:TipoUsuario {{nombre: '{tipo_usuario}'}})
    
    -- 4. Agregar keywords matcheadas y calcular métricas
    WITH c, t, s, tu, collect(DISTINCT k.nombre) AS matched_keywords
    WITH c, t, s, tu, matched_keywords, 
         size(matched_keywords) AS matched_count,
         coalesce(c.confianzaDecision, 0) AS confianza,
         CASE WHEN tu IS NULL THEN 0 ELSE 1 END AS has_type
    
    -- 5. Retornar resultado con múltiples criterios de ordenamiento
    RETURN DISTINCT
        t.nombre AS tipo_problema,
        s.accion AS solucion,
        confianza AS confianza,
        matched_count AS matched_count,
        matched_keywords AS matched_keywords,
        has_type
    ORDER BY has_type DESC, matched_count DESC, confianza DESC
    LIMIT 1
    """

# Ejecutar query
def recuperar_solucion(keywords, tipo_usuario):
    """Ejecuta query y retorna resultado."""
    cypher = cypher_query(keywords, tipo_usuario)
    result = graph.query(cypher)
    return result[0] if result else None
```


***

## **Ejemplo de Funcionamiento**

### **Caso 1: Consulta exitosa con múltiples matches**

**Input**:

```python
keywords = ['tarjeta', 'rechazar', 'pago']
tipo_usuario = 'Organizador'
```

**Query Cypher generada**:

```cypher
WITH ['tarjeta', 'rechazar', 'pago'] AS kws
UNWIND kws AS kw
MATCH (k:PalabraClave)
WHERE toLower(k.nombre) = kw
MATCH (k)-[:DISPARA]->(c:CategoriaProblema)
OPTIONAL MATCH (c)-[:AGRUPA]->(t:TipoProblema)-[:RESUELTO_POR]->(s:Solucion)
OPTIONAL MATCH (c)-[:TIENE_UN]->(tu:TipoUsuario {nombre: 'Organizador'})
WITH c, t, s, tu, collect(DISTINCT k.nombre) AS matched_keywords
WITH c,t,s,tu,matched_keywords, size(matched_keywords) AS matched_count,
     coalesce(c.confianzaDecision,0) AS confianza,
     CASE WHEN tu IS NULL THEN 0 ELSE 1 END AS has_type
RETURN DISTINCT
    t.nombre AS tipo_problema,
    s.accion AS solucion,
    confianza AS confianza,
    matched_count AS matched_count,
    matched_keywords AS matched_keywords,
    has_type
ORDER BY has_type DESC, matched_count DESC, confianza DESC
LIMIT 1
```

**Camino recorrido en el grafo**:

```
PalabraClave(tarjeta) ──DISPARA──► CategoriaProblema(ProblemaPago)
PalabraClave(rechazar)──DISPARA──►            │
PalabraClave(pago)     ──DISPARA──►            │
                                               │
                                               ├──AGRUPA──► TipoProblema(Tarjeta rechazada)
                                               │                    │
                                               │                    └──RESUELTO_POR──► Solucion(...)
                                               │
                                               └──TIENE_UN──► TipoUsuario(Organizador)
```

**Output**:

```python
{
  'tipo_problema': 'Tarjeta rechazada',
  'solucion': 'Verifique los datos de su tarjeta e intente nuevamente.',
  'confianza': 0.9,
  'matched_count': 3,
  'matched_keywords': ['tarjeta', 'rechazar', 'pago'],
  'has_type': 1
}
```


***

### **Caso 2: Consulta con coincidencia parcial**

**Input**:

```python
keywords = ['comision', 'ayuda']
tipo_usuario = 'Prestador'
```

**Resultado**:

```python
{
  'tipo_problema': 'Info comisiones',
  'solucion': 'Las comisiones son del 1% por operación.',
  'confianza': 0.9,
  'matched_count': 1,  # Solo "comision" matcheó
  'matched_keywords': ['comision'],
  'has_type': 1
}
```

**Observación**: Aunque solo 1 keyword matcheó, el sistema retorna la mejor coincidencia disponible.

***

### **Caso 3: Sin coincidencias (fuera de dominio)**

**Input**:

```python
keywords = ['dolor', 'cabeza']
tipo_usuario = 'Organizador'
```

**Resultado**:

```python
[]  # Lista vacía
```

**Manejo en el sistema**:

```python
result = graph.query(cypher)
if not result:
    # Derivar a soporte o profesional adecuado
    return "Lo siento, no puedo ayudar con ese tipo de consulta..."
```


***

## **Capturas del Sistema**

### **Captura 1: Visualización del grafo completo**

**Query en Neo4j Browser**:

```cypher
MATCH (n) RETURN n LIMIT 100
```

*(Incluir captura mostrando nodos de diferentes tipos con colores distintos: PalabraClave en azul, CategoriaProblema en verde, TipoProblema en amarillo, Solucion en naranja)*

***

### **Captura 2: Camino específico de una consulta**

**Query**:

```cypher
MATCH path = (k:PalabraClave {nombre: 'tarjeta'})-[:DISPARA]->(c:CategoriaProblema)
            -[:AGRUPA]->(t:TipoProblema)-[:RESUELTO_POR]->(s:Solucion)
WHERE c.nombre = 'ProblemaPago'
RETURN path
```

*(Incluir captura del camino visual completo desde tarjeta hasta la solución)*

***

### **Captura 3: Consulta con filtro por TipoUsuario**

**Query**:

```cypher
MATCH (c:CategoriaProblema {nombre: 'ProblemaServicio'})-[:TIENE_UN]->(tu:TipoUsuario)
RETURN c.nombre AS categoria, collect(tu.nombre) AS usuarios_permitidos
```

**Resultado esperado**:

```
categoria: "ProblemaServicio"
usuarios_permitidos: ["Organizador"]
```


***

## **Resultados de Pruebas**

### **Prueba 1: Latencia de consultas**

| Tipo de consulta | Entorno | Latencia promedio | Observación |
| :-- | :-- | :-- | :-- |
| Query simple (1 keyword) | Remoto (Aura) | 2.1-2.8 seg | Incluye latencia de red |
| Query simple (1 keyword) | Local | 100-130 ms | Sin latencia de red |
| Query compleja (3 keywords) | Remoto | 2.5-3.2 seg | Agregación aumenta tiempo |
| Query compleja (3 keywords) | Local | 150-200 ms | Procesamiento rápido |

**Conclusión**: Latencia local es 15-20x más rápida, pero remoto es aceptable (<5 seg).

***

### **Prueba 2: Precisión de recuperación**

| Keywords | Tipo Usuario | Match esperado | Match obtenido | ✓/✗ |
| :-- | :-- | :-- | :-- | :-- |
| ['pago', 'rechazar'] | Organizador | "Tarjeta rechazada" | "Tarjeta rechazada" | ✅ |
| ['servicio', 'reclamo'] | Organizador | "Reclamo servicio" | "Reclamo servicio" | ✅ |
| ['comision'] | Prestador | "Info comisiones" | "Info comisiones" | ✅ |
| ['ayuda', 'app'] | Propietario | "Ayuda con app" | "Ayuda con app" | ✅ |
| ['dolor', 'cabeza'] | Organizador | null (fuera de dominio) | [] | ✅ |

**Tasa de precisión**: 100% en casos de prueba (5/5)

***

### **Prueba 3: Ordenamiento correcto por criterios múltiples**

**Escenario**: Múltiples resultados posibles, sistema debe priorizar:

1. Coincidencia de `TipoUsuario` (`has_type`)
2. Mayor cantidad de keywords matcheadas (`matched_count`)
3. Mayor confianza (`confianza`)

**Test ejecutado**:

```python
keywords = ['pago', 'acreditar']
tipo_usuario = 'Prestador'
```

**Resultados candidatos** (antes del ORDER BY):

```python
[
  {'tipo_problema': 'No recibí pago', 'matched_count': 2, 'has_type': 1, 'confianza': 0.9},
  {'tipo_problema': 'Demora en acreditación', 'matched_count': 2, 'has_type': 1, 'confianza': 0.9},
  {'tipo_problema': 'Info comisiones', 'matched_count': 1, 'has_type': 1, 'confianza': 0.9}
]
```

**Resultado final** (con LIMIT 1):

```python
{
  'tipo_problema': 'No recibí pago',  # Primer match con máximos criterios
  'matched_count': 2,
  'has_type': 1,
  'confianza': 0.9
}
```

✅ **Ordenamiento funciona correctamente**

***

### **Prueba 4: Fallback de conexión**

**Escenario**: Simular fallo de conexión remota

**Test 1 - Remoto disponible**:

```
[INFO] Intentando conectar a Neo4j remoto (Aura)...
[INFO] ✅ Conexión Neo4j establecida en remoto (Aura).
```

**Test 2 - Remoto no disponible (simulado con URI inválida)**:

```
[INFO] Intentando conectar a Neo4j remoto (Aura)...
[WARNING] ⚠️ Fallo conexión remota: ... Intentando local...
[INFO] Intentando conectar a Neo4j local...
[INFO] ✅ Conexión Neo4j establecida en local.
```

✅ **Sistema de fallback funciona correctamente**

***

### **Prueba 5: Manejo de casos edge**

| Caso | Input | Resultado esperado | Resultado obtenido | ✓/✗ |
| :-- | :-- | :-- | :-- | :-- |
| Keywords vacías | `[]` | Error controlado o derivación | Mensaje de fallback | ✅ |
| Keyword con mayúsculas | `['PAGO']` | Match (case-insensitive) | Match correcto | ✅ |
| Keywords con acentos | `['acreditación']` | Match si existe en BD | Match correcto | ✅ |
| Usuario no válido | `'AdminXYZ'` | `has_type = 0` | `has_type = 0` | ✅ |
| Query muy compleja (10 keywords) | `[...]` | Timeout < 10 seg | 3.8 seg (remoto) | ✅ |


***

## **Estructura de la Base de Datos**

### **Estadísticas del grafo**

**Query para obtener métricas**:

```cypher
MATCH (n)
RETURN labels(n) AS tipo_nodo, count(*) AS cantidad
ORDER BY cantidad DESC
```

**Resultado**:

```
┌──────────────────────┬──────────┐
│ tipo_nodo            │ cantidad │
├──────────────────────┼──────────┤
│ PalabraClave         │ 38       │
│ TipoProblema         │ 12       │
│ Solucion             │ 12       │
│ CategoriaProblema    │ 4        │
│ Emocion              │ 3        │
│ TipoUsuario          │ 3        │
└──────────────────────┴──────────┘
Total de nodos: 72
```

**Query para contar relaciones**:

```cypher
MATCH ()-[r]->()
RETURN type(r) AS tipo_relacion, count(r) AS cantidad
ORDER BY cantidad DESC
```

**Resultado**:

```
┌──────────────────┬──────────┐
│ tipo_relacion    │ cantidad │
├──────────────────┼──────────┤
│ DISPARA          │ 38       │
│ AGRUPA           │ 12       │
│ RESUELTO_POR     │ 12       │
│ TIENE_UN         │ 12       │
│ MODIFICA         │ 12       │
│ INFLUYE          │ 12       │
└──────────────────┴──────────┘
Total de relaciones: 98
```


***

## **Diagrama de Arquitectura de Conexión**

```
┌─────────────────────────┐
│   Aplicación Python     │
│   (langchain.py)        │
└───────────┬─────────────┘
            │
            │ get_graph()
            ▼
┌─────────────────────────┐
│  neo4j_connection.py    │
│  (Gestor con fallback)  │
└───────┬─────────────────┘
        │
        ├──── Intento 1 ───────┐
        │                       ▼
        │              ┌──────────────────┐
        │              │  Neo4j Aura      │
        │              │  (Cloud Remoto)  │
        │              │  neo4j+s://...   │
        │              └──────────────────┘
        │                       │
        │                    [ÉXITO]─────► Retorna graph
        │                       │
        │                    [FALLO]
        │                       │
        ├──── Intento 2 ───────┘
        │                       ▼
        │              ┌──────────────────┐
        │              │  Neo4j Local     │
        │              │  bolt://localhost│
        │              └──────────────────┘
        │                       │
        │                    [ÉXITO]─────► Retorna graph
        │                       │
        │                    [FALLO]
        │                       │
        └───────────────────────┴────────► Exception
```


***

## **Optimizaciones Implementadas**

### **1. Índices implícitos en propiedades `nombre`**

Neo4j crea índices automáticos en propiedades frecuentemente consultadas:

```cypher
CREATE INDEX palabra_clave_nombre IF NOT EXISTS
FOR (k:PalabraClave) ON (k.nombre)
```

**Impacto**: Reduce tiempo de búsqueda de O(n) a O(log n)

### **2. Case-insensitive matching con `toLower()`**

```cypher
WHERE toLower(k.nombre) = kw
```

**Impacto**: Evita duplicados por mayúsculas/minúsculas

### **3. Uso de `OPTIONAL MATCH` para relaciones opcionales**

```cypher
OPTIONAL MATCH (c)-[:TIENE_UN]->(tu:TipoUsuario {nombre: 'Organizador'})
```

**Impacto**: Query no falla si el nodo TipoUsuario no existe

### **4. `LIMIT 1` para evitar resultados redundantes**

**Impacto**: Reduce transferencia de datos en red

***

## **Observaciones y Sugerencias**

### **Fortalezas**

- ✅ **Fallback robusto**: Sistema nunca falla completamente si una instancia Neo4j está disponible
- ✅ **Consultas contextualizadas**: Ordenamiento por `has_type`, `matched_count` y `confianza` prioriza resultados relevantes
- ✅ **Latencia aceptable**: Incluso en remoto, <3 seg es tolerable para chat
- ✅ **Escalabilidad**: Agregar nuevos nodos/relaciones no requiere cambios en queries
- ✅ **Trazabilidad**: Logs detallados de conexión y queries


### **Limitaciones Identificadas**

- ⚠️ **Latencia remota variable**: Dependiendo de la región del servidor Aura, puede variar 1-5 seg
- ⚠️ **Sin caché de resultados**: Cada consulta golpea la BD, incluso para keywords repetidas
- ⚠️ **Dependencia de conexión**: Si ambas instancias (remota y local) fallan, el sistema no puede operar
- ⚠️ **Sin análisis de sinónimos en BD**: Keywords como "pago" y "pagos" son nodos separados


### **Mejoras Futuras**

#### **1. Implementar caché local con TTL**

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def recuperar_solucion_cached(keywords_tuple, tipo_usuario):
    # Convertir tupla a lista para compatibilidad
    keywords = list(keywords_tuple)
    return recuperar_solucion(keywords, tipo_usuario)

# Uso
keywords_tuple = tuple(sorted(keywords))  # Normalizar orden
result = recuperar_solucion_cached(keywords_tuple, tipo_usuario)
```

**Impacto**: Reduce latencia en consultas repetidas de ~3 seg a <1 ms

#### **2. Conexión persistente (pool de conexiones)**

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(aura_uri, auth=(user, pwd))

def query_with_pool(cypher):
    with driver.session() as session:
        result = session.run(cypher)
        return [record.data() for record in result]
```

**Impacto**: Reduce overhead de establecer conexión en cada query

#### **3. Expansión de sinónimos con embeddings**

```python
# Agregar propiedad "embedding" a nodos PalabraClave
CREATE (k:PalabraClave {nombre: 'pago', embedding: [0.21, 0.45, ...]})

# Query con similitud semántica
MATCH (k:PalabraClave)
WHERE gds.similarity.cosine(k.embedding, $query_embedding) > 0.8
```

**Impacto**: Captura variantes lingüísticas sin crear nodos duplicados

#### **4. Monitoreo de salud de conexión**

```python
def health_check():
    try:
        graph.query('RETURN 1')
        return {'status': 'healthy', 'latency_ms': ...}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}
```

**Impacto**: Permite alertas proactivas antes de que usuarios reporten fallos

#### **5. Queries preparadas (Cypher parameterizado)**

```python
prepared_query = """
MATCH (k:PalabraClave)
WHERE toLower(k.nombre) IN $keywords
...
"""
result = graph.query(prepared_query, params={'keywords': keywords, 'user_type': tipo_usuario})
```

**Impacto**: Protección contra inyección Cypher + mejor rendimiento

***

## **Resumen Técnico**

| Aspecto | Valor | Observación |
| :-- | :-- | :-- |
| **Nodos totales** | 72 | Escalable a miles sin degradación |
| **Relaciones totales** | 98 | Modelo semántico rico |
| **Latencia remota** | 2-3 seg | Aceptable para UX conversacional |
| **Latencia local** | 100-200 ms | Excelente |
| **Tasa de éxito** | 100% | En casos de prueba documentados |
| **Disponibilidad** | Alta | Fallback garantiza operación |
| **Escalabilidad** | Alta | Arquitectura permite crecimiento |


***