# Módulo 2: Red Semántica (Modelo Conceptual)

## **Propósito**

Modelar el conocimiento del dominio de soporte a usuarios de Wevently mediante un grafo semántico que representa entidades (problemas, soluciones, palabras clave, emociones, tipos de usuario), sus relaciones y la ontología del negocio. Este modelo permite consultas contextuales eficientes y razonamiento sobre categorías de problemas según el perfil del usuario.

***

## **Entradas**

### Datos estructurados de la ontología del dominio:

- **Palabras clave** (33+ variantes): términos y sinónimos relacionados con pagos, servicios, eventos, problemas técnicos
- **Categorías de problemas** (4): `ProblemaPago`, `ProblemaTecnico`, `ProblemaServicio`, `ConsultaGeneral`
- **Tipos de problemas** (12+): Subcategorías específicas (ej: "Tarjeta rechazada", "Demora en acreditación")
- **Soluciones** (12+): Acciones recomendadas para cada tipo de problema
- **Emociones** (3): `Positiva`, `Negativa`, `Neutra`
- **Tipos de usuario** (3): `Organizador`, `Prestador`, `Propietario`

***

## **Salidas**

- **Grafo de conocimiento consultable** almacenado en Neo4j
- **Relaciones semánticas** entre entidades:
    - `PalabraClave -[:DISPARA]-> CategoriaProblema`
    - `CategoriaProblema -[:AGRUPA]-> TipoProblema`
    - `TipoProblema -[:RESUELTO_POR]-> Solucion`
    - `CategoriaProblema -[:TIENE_UN]-> TipoUsuario`
    - `Emocion -[:MODIFICA]-> CategoriaProblema`
    - `Emocion -[:INFLUYE]-> TipoProblema`
- **Valores de confianza** por categoría (definido por lógica difusa).

***

## **Herramientas y Entorno**

| Componente | Tecnología | Versión | Propósito |
| :-- | :-- | :-- | :-- |
| **Base de datos** | Neo4j | ≥5.14.0 | Almacenamiento de grafo semántico |
| **Lenguaje de consulta** | Cypher | - | Creación y consulta del grafo |
| **Cliente Python** | `neo4j` | ≥5.14.0 | Conexión programática desde Python |
| **Integración LangChain** | `langchain_neo4j` | ≥0.0.3 | Wrapper para consultas desde LangChain |
| **Gestor de conexión** | `neo4j_connection.py` | - | Fallback remoto/local |

**Entorno de despliegue:**

- **Remoto**: Neo4j Aura (cloud)
- **Local**: Instancia Neo4j Desktop o Docker (`bolt://localhost:7687`)

***

## **Código Relevante**

### **Archivo principal**: `src/neo4j_connection.py`

```python
import os
import logging
from langchain_neo4j import Neo4jGraph

logger = logging.getLogger(__name__)

def get_graph():
    """Retorna conexión a Neo4j con fallback remoto→local."""
    aura_uri = os.getenv('NEO4J_URI') or ''
    bolt_local = os.getenv('NEO4J_URL', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USERNAME', 'neo4j')
    pwd = os.getenv('NEO4J_PASSWORD', '')

    # Intenta remoto (Aura) primero
    if aura_uri:
        try:
            logger.info('Conectando a Neo4j remoto (Aura)...')
            graph = Neo4jGraph(url=aura_uri, username=user, password=pwd)
            graph.query('RETURN 1 AS ok')
            logger.info('Conexión Neo4j establecida en remoto.')
            return graph
        except Exception:
            logger.warning('Fallo remoto, intentando local...')

    # Fallback a local
    try:
        logger.info('Conectando a Neo4j local...')
        graph = Neo4jGraph(url=bolt_local, username=user, password=pwd)
        graph.query('RETURN 1 AS ok')
        logger.info('Conexión Neo4j establecida en local.')
        return graph
    except Exception as e:
        logger.error('No se pudo conectar a Neo4j (remoto ni local).', exc_info=True)
        raise
```


### **Consulta dinámica desde**: `src/langchain.py`

```python
def cypher_query(keywords, tipo_usuario):
    """Genera query Cypher parametrizada para recuperar solución."""
    kw_list = [k.lower() for k in keywords]
    kwstr = "[" + ", ".join([f"'{k}'" for k in kw_list]) + "]"
    return f"""
    WITH {kwstr} AS kws
    UNWIND kws AS kw
    MATCH (k:PalabraClave)
    WHERE toLower(k.nombre) = kw
    MATCH (k)-[:DISPARA]->(c:CategoriaProblema)
    OPTIONAL MATCH (c)-[:AGRUPA]->(t:TipoProblema)-[:RESUELTO_POR]->(s:Solucion)
    OPTIONAL MATCH (c)-[:TIENE_UN]->(tu:TipoUsuario {{nombre: '{tipo_usuario}'}})
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
    """
```


***

## **Estructura del Grafo Semántico**

### **Diagrama de Entidades y Relaciones**

```
┌─────────────────┐
│  PalabraClave   │
│  (33+ nodos)    │
│  - pago         │
│  - tarjeta      │
│  - servicio     │
│  - fallo        │
└────────┬────────┘
         │ [:DISPARA]
         ▼
┌─────────────────────┐
│ CategoriaProblema   │
│  - ProblemaPago     │
│  - ProblemaTecnico  │
│  - ProblemaServicio │
│  - ConsultaGeneral  │
│  + confianzaDecision│
└────────┬────────────┘
         │ [:AGRUPA]
         ▼
┌─────────────────────┐
│  TipoProblema       │
│  - Tarjeta rechazada│
│  - Demora acreditac.│
│  - Reclamo servicio │
│  - Ayuda con app    │
└────────┬────────────┘
         │ [:RESUELTO_POR]
         ▼
┌─────────────────────┐
│    Solucion         │
│  - Verifique datos  │
│  - Contacte soporte │
│  - Consulte FAQ     │
└─────────────────────┘

         ┌──────────────┐
         │   Emocion    │
         │  - Positiva  │
         │  - Negativa  │
         │  - Neutra    │
         └──────┬───────┘
                │ [:MODIFICA]
                │ [:INFLUYE]
                ▼
        CategoriaProblema
        TipoProblema

┌─────────────────┐
│  TipoUsuario    │
│  - Organizador  │
│  - Prestador    │
│  - Propietario  │
└────────┬────────┘
         │ [:TIENE_UN]
         ▼
   CategoriaProblema
```


***

## **Ejemplo de Funcionamiento**

### **Caso 1: Consulta "Mi tarjeta fue rechazada dos veces"**

**1. Keywords extraídas**: `['tarjeta', 'rechazar']`

**2. Query Cypher ejecutada**:

```cypher
WITH ['tarjeta', 'rechazar'] AS kws
UNWIND kws AS kw
MATCH (k:PalabraClave)
WHERE toLower(k.nombre) = kw
MATCH (k)-[:DISPARA]->(c:CategoriaProblema)
OPTIONAL MATCH (c)-[:AGRUPA]->(t:TipoProblema)-[:RESUELTO_POR]->(s:Solucion)
...
RETURN t.nombre AS tipo_problema, s.accion AS solucion, confianza
```

**3. Resultado**:

```json
{
  "tipo_problema": "Tarjeta rechazada",
  "solucion": "Verifique los datos de su tarjeta e intente nuevamente.",
  "confianza": 0.9,
  "matched_count": 2,
  "matched_keywords": ["tarjeta", "rechazar"]
}
```

**4. Camino recorrido en el grafo**:

```
PalabraClave(tarjeta) → DISPARA → CategoriaProblema(ProblemaPago)
                                    ↓ AGRUPA
                                 TipoProblema(Tarjeta rechazada)
                                    ↓ RESUELTO_POR
                                 Solucion(Verifique datos...)
```


***

### **Caso 2: Consulta fuera de dominio "Me duele la cabeza"**

**1. Keywords extraídas**: `['doler', 'cabeza']`

**2. Query Cypher ejecutada**: (mismo formato)

**3. Resultado**: `[]` (sin matches)

**4. Sistema deriva a profesional**: No se navega el grafo, se retorna mensaje de fallback.

***

## **Capturas del Grafo (Neo4j Browser)**

### **Vista General del Grafo**

```cypher
MATCH (n) RETURN n LIMIT 100
```

![alt text](<Captura de pantalla 2025-11-13 133812.png>)

### **Camino específico: Pago → Problema → Solución**

```cypher
MATCH path = (k:PalabraClave {nombre: 'pago'})-[:DISPARA]->(c:CategoriaProblema)
            -[:AGRUPA]->(t:TipoProblema)-[:RESUELTO_POR]->(s:Solucion)
RETURN path
```


### **Estadísticas del Grafo**

```cypher
MATCH (n) RETURN labels(n) AS tipo, count(*) AS cantidad
```

**Resultado esperado**:


| Tipo | Cantidad |
| :-- | :-- |
| PalabraClave | 38 |
| CategoriaProblema | 4 |
| TipoProblema | 12 |
| Solucion | 12 |
| Emocion | 3 |
| TipoUsuario | 3 |


***

## **Resultados de Pruebas**

### **Prueba 1: Consultas Cypher eficientes**

- ✅ Tiempo promedio de consulta: **2.5 segundos** (incluye latencia de red remota)
- ✅ Tiempo en local: **~100-130 ms**
- ✅ Índices implícitos en propiedades `nombre`


### **Prueba 2: Cobertura de palabras clave**

```cypher
MATCH (k:PalabraClave) RETURN count(k) AS total_keywords
```

**Resultado**: 38 palabras clave + variantes

### **Prueba 3: Relaciones claras**

```cypher
MATCH ()-[r]->() RETURN type(r) AS relacion, count(r) AS cantidad
```

**Resultado**:


| Relación | Cantidad |
| :-- | :-- |
| DISPARA | 38 |
| AGRUPA | 12 |
| RESUELTO_POR | 12 |
| TIENE_UN | 12 |
| MODIFICA | 12 |
| INFLUYE | 12 |

### **Prueba 4: Recuperación exitosa por rol**

```python
# Test con usuario "Organizador"
keywords = ['servicio', 'prestador']
result = graph.query(cypher_query(keywords, 'Organizador'))
assert result[0]['tipo_problema'] == 'Reclamo servicio'
assert result[0]['confianza'] == 0.8
```

✅ **Resultado**: Correcto

***


## **Observaciones y Sugerencias**

### **Fortalezas**

- ✅ **Modelo extensible**: Agregar nuevas categorías/soluciones requiere solo comandos Cypher adicionales
- ✅ **Consultas eficientes**: Índices implícitos en propiedades `nombre`
- ✅ **Fallback robusto**: Conexión remota/local garantiza disponibilidad
- ✅ **Trazabilidad**: Cada relación tiene semántica clara (`DISPARA`, `AGRUPA`, `RESUELTO_POR`)


### **Limitaciones Identificadas**

- ⚠️ **Cobertura limitada**: 38 palabras clave pueden no cubrir todas las variantes coloquiales de usuarios reales
- ⚠️ **Valores de confianza estáticos**: Actualmente se asignan manualmente (0.6-0.9), no se ajustan dinámicamente con aprendizaje


### **Mejoras Futuras**

1. **Expansión del vocabulario**: Agregar 50+ palabras clave adicionales basadas en logs reales de usuarios
2. **Sinónimos automáticos**: Integrar WordNet o embeddings para expandir matches sin crear nodos duplicados
3. **Actualización dinámica de confianza**: Implementar triggers APOC que ajusten `confianzaDecision` según feedback de usuarios
4. **Relaciones ponderadas**: Agregar propiedades `peso` a las relaciones `DISPARA` para priorizar keywords más relevantes