# 📋 **ÍNDICE TÉCNICO GENERAL - SISTEMA WEVENTLY**

## **Arquitectura del Sistema de 9 Módulos**

```
┌─────────────────────────────────────────────────────────────────────┐
│              ARQUITECTURA COMPLETA - WEVENTLY CHATBOT               │
│                     (9 Módulos Integrados)                          │
└─────────────────────────────────────────────────────────────────────┘

CAPA DE PRESENTACIÓN
┌─────────────────────────────────────────────────────────────────┐
│  MÓDULO 9: API DEL ASISTENTE (Streamlit)                        │
│  • Interfaz web responsive con chat                             │
│  • Gestión de sesiones y estado                                 │
│  • Orquestación de pipeline completo                            │
└─────────────────────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  MÓDULO 1: RED DE PROCESOS (Orquestador)                        │
│  • Flujo de decisión condicional                                │
│  • Logging de operaciones                                       │
│  • Coordinación entre módulos                                   │
└─────────────────────────────────────────────────────────────────┘
                                 ▼
                    ┌────────────┴────────────┐
                    ▼                         ▼
CAPA DE PROCESAMIENTO NLP              CAPA DE CONOCIMIENTO
┌──────────────────────────┐    ┌──────────────────────────────┐
│ MÓDULO 7: INTEGRACIÓN    │    │ MÓDULO 2: RED SEMÁNTICA      │
│ NLP (spaCy + BETO)       │    │ (Estructura conceptual)      │
│ • Análisis sintáctico    │    │ • Relaciones conceptuales    │
│ • Extracción de entidades│    │ • Jerarquía de categorías    │
│ • Detección sentimiento  │    │ • Palabras clave             │
└──────────────────────────┘    └──────────────────────────────┘
           │                                  │
           │                                  ▼
           │                    ┌──────────────────────────────┐
           │                    │ MÓDULO 4: BASE ORIENTADA A   │
           │                    │ GRAFOS (Neo4j)               │
           │                    │ • Persistencia de red        │
           │                    │ • Queries Cypher             │
           │                    │ • Recuperación contextual    │
           │                    └──────────────────────────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          ▼
           ┌──────────────────────────────────┐
           │ MÓDULO 3: RED DE FRAMES DIFUSOS  │
           │ (Lógica Fuzzy)                   │
           │ • Cálculo de confianza           │
           │ • Membership functions           │
           │ • Defuzzification                │
           └──────────────────────────────────┘
                          │
                          ▼
CAPA DE GENERACIÓN
┌─────────────────────────────────────────────────────────────────┐
│  MÓDULO 8: INTEGRACIÓN GENERATIVA (Ollama LLM)                  │
│  • Generación de respuestas contextualizadas                    │
│  • Personalización según tipo de usuario                        │
│  • Control de temperatura y creatividad                         │
└─────────────────────────────────────────────────────────────────┘

CAPA DE INFRAESTRUCTURA
┌─────────────────────────────────────────────────────────────────┐
│  MÓDULO 5: FLUJO DE PLANIFICACIÓN (Logging & Orchestration)     │
│  • Medición de tiempos por módulo                               │
│  • Registros de auditoría                                       │
│  • Gestión de errores                                           │
└─────────────────────────────────────────────────────────────────┘

MÓDULO NO IMPLEMENTADO
┌─────────────────────────────────────────────────────────────────┐
│  MÓDULO 6: MODELOS DE APRENDIZAJE (ML - NO IMPLEMENTADO)        │
│  • Experimento Random Forest: 48% accuracy (descartado)         │
│  • Decisión: Usar enfoque simbólico (Módulos 2-4)              │
└─────────────────────────────────────────────────────────────────┘
```


***

## **Índice de Documentación Técnica**

### **MÓDULO 1: RED DE PROCESOS**

📄 **Archivo**: `MODULO_1_RED_PROCESOS.md`

**Contenido**:

- Propósito: Orquestación del flujo de decisión condicional
- Entradas: Mensaje de usuario, tipo de usuario
- Salidas: Respuesta final estructurada con categoría, confianza, respuesta generada
- Herramientas: Python 3.11, logging, diccionarios condicionales
- Código relevante: Función `generar_respuesta_streamlit()`
- Ejemplos: Flujo completo de consulta sobre "pago rechazado"
- Resultados de pruebas: 100% de ejecuciones exitosas, latencia total 4.2 seg
- Observaciones: Módulo crítico para coordinación, sin él no hay integración

**Dependencias**:

- ⬇️ Recibe datos de: Módulo 9 (interfaz)
- ➡️ Coordina: Módulos 2, 3, 4, 5, 7, 8
- ⬆️ Envía resultados a: Módulo 9

***

### **MÓDULO 2: RED SEMÁNTICA**

📄 **Archivo**: `MODULO_2_RED_SEMANTICA.md`

**Contenido**:

- Propósito: Definición de estructura conceptual del dominio (pagos, tarjetas, transacciones)
- Entradas: No aplica (es una estructura estática de conocimiento)
- Salidas: Esquema conceptual para Módulo 4 (Neo4j)
- Herramientas: Cypher (lenguaje de Neo4j), modelado de grafos
- Código relevante: Scripts de creación de nodos y relaciones
- Ejemplos: Red de conceptos "Tarjeta" → "Rechazo" → "Fondos Insuficientes"
- Resultados de pruebas: 42 nodos, 67 relaciones cargadas en Neo4j
- Observaciones: Base conceptual del sistema, define qué conocimiento tiene el asistente

**Dependencias**:

- ⬇️ Recibe datos de: Ninguno (conocimiento predefinido)
- ➡️ Alimenta a: Módulo 4 (Neo4j implementa esta red)
- ⬆️ Envía resultados a: Módulo 4

***

### **MÓDULO 3: RED DE FRAMES DIFUSOS**

📄 **Archivo**: `MODULO_3_FRAMES_DIFUSOS.md`

**Contenido**:

- Propósito: Cálculo de confianza mediante lógica fuzzy
- Entradas: Coincidencia de palabras clave (0-100%), sentimiento (-1 a 1), longitud del mensaje
- Salidas: Valor de confianza defuzzificado (0.0 - 1.0)
- Herramientas: scikit-fuzzy 0.4.2, membership functions triangulares/trapezoidales
- Código relevante: Función `calcular_confianza_fuzzy()`
- Ejemplos: Coincidencia 80%, sentimiento negativo → confianza 0.87
- Resultados de pruebas: Confianza promedio 0.87 (20 casos), sin falsos positivos
- Observaciones: Mejora decisiones vs. umbral binario, maneja incertidumbre

**Dependencias**:

- ⬇️ Recibe datos de: Módulo 4 (coincidencia keywords), Módulo 7 (sentimiento)
- ➡️ Procesa con: Lógica fuzzy (reglas IF-THEN)
- ⬆️ Envía resultados a: Módulo 1 (para decisión final)

***

### **MÓDULO 4: BASE ORIENTADA A GRAFOS**

📄 **Archivo**: `MODULO_4_BASE_GRAFOS_NEO4J.md`

**Contenido**:
- Propósito: Persistencia y consulta de la red semántica mediante base de datos de grafos
- Entradas: Palabras clave extraídas del mensaje, tipo de usuario
- Salidas: Categoría detectada, solución asociada, porcentaje de coincidencia
- Herramientas: Neo4j 5.14.0, langchain-neo4j, Cypher DSL, Neo4j AuraDB
- Código relevante: Función `cypher_query()` con generación dinámica de queries
- Ejemplos: Query "tarjeta rechazada" → retorna nodo "Rechazo_Tarjeta" con solución
- Resultados de pruebas: 95% precisión (19/20 casos), latencia 2.5 seg (remota) / 120 ms (local)
- Observaciones: Bottleneck principal de latencia, migración a local reduce tiempo 95%

**Dependencias**:

- ⬇️ Recibe datos de: Módulo 2 (esquema conceptual), Módulo 7 (keywords extraídas)
- ➡️ Procesa con: Queries Cypher sobre grafo Neo4j
- ⬆️ Envía resultados a: Módulo 3 (coincidencia para fuzzy), Módulo 1 (categoría para respuesta)

***

### **MÓDULO 5: FLUJO DE PLANIFICACIÓN**

📄 **Archivo**: `MODULO_5_FLUJO_PLANIFICACION.md`

**Contenido**:

- Propósito: Logging de operaciones, medición de tiempos, auditoría del sistema
- Entradas: Eventos de inicio/fin de operaciones de cada módulo
- Salidas: Registros estructurados en logs, métricas de latencia por componente
- Herramientas: Python `logging` module, timestamps con `time.time()`, archivos `.log`
- Código relevante: Configuración de logger, decoradores de timing, formato de logs
- Ejemplos: Log entry "INFO - Neo4j query completada en 2.48 segundos"
- Resultados de pruebas: 100% de operaciones registradas, overhead < 5 ms por log
- Observaciones: Infraestructura invisible pero crítica para debugging y optimización

**Dependencias**:

- ⬇️ Recibe datos de: Todos los módulos (1, 3, 4, 7, 8, 9)
- ➡️ Procesa con: Sistema de logging centralizado
- ⬆️ Envía resultados a: Archivos de log, consola (para monitoreo)

***

### **MÓDULO 6: MODELOS DE APRENDIZAJE**

📄 **Archivo**: `MODULO_6_MODELOS_APRENDIZAJE.md`

**Contenido**:

- Propósito: Clasificación de consultas mediante Machine Learning supervisado
- Entradas: Dataset de consultas etiquetadas por categoría
- Salidas: **NO IMPLEMENTADO** - Experimento no integrado al sistema
- Herramientas: scikit-learn, Random Forest Classifier, TfidfVectorizer
- Código relevante: Script experimental `clasificador_rf.py` (no usado en producción)
- Experimento realizado: Random Forest con 200 árboles, accuracy 48% (validación cruzada)
- Razón de no implementación: Accuracy insuficiente vs. enfoque simbólico (Neo4j 95%)
- Observaciones: Decisión arquitectónica clave - priorizar precisión sobre automatización

**Dependencias**:

- ⬇️ Recibe datos de: Dataset manual de consultas (no integrado)
- ➡️ **NO INTEGRADO** - Módulo experimental descartado
- ⬆️ Envía resultados a: Ninguno (sustituido por Módulos 2+4)

**Justificación técnica de exclusión**:

```
┌─────────────────────────────────────────────────────────────────┐
│         COMPARACIÓN: ML vs. ENFOQUE SIMBÓLICO                   │
└─────────────────────────────────────────────────────────────────┘

Métrica                  Random Forest    Neo4j + Fuzzy
─────────────────────────────────────────────────────────────────
Accuracy                     48%              95%
Mantenibilidad              Baja           Alta (actualizar grafo)
Explicabilidad              Baja           Alta (queries Cypher)
Requisitos de datos      Alto (>1000)      Bajo (conocimiento experto)
Tiempo de entrenamiento    ~5 min           N/A (sin entrenamiento)
Latencia de inferencia     ~50 ms          2.5 seg (query remota)

DECISIÓN: Enfoque simbólico preferido por accuracy superior y 
          explicabilidad crítica para dominio financiero.
```


***

### **MÓDULO 7: INTEGRACIÓN NLP**

📄 **Archivo**: `MODULO_7_INTEGRACION_NLP.md`

**Contenido**:

- Propósito: Procesamiento de lenguaje natural con análisis sintáctico y detección de sentimiento
- Entradas: Mensaje de usuario en texto plano (español)
- Salidas: Tokens, entidades nombradas, sentimiento (positivo/negativo/neutro)
- Herramientas: spaCy 3.7.0 (`es_core_news_md`), Transformers 4.30.0 (BETO fine-tuned)
- Código relevante: Función `analizar_sentimiento()`, pipeline spaCy + BETO
- Ejemplos: "Mi tarjeta fue rechazada" → sentimiento negativo (-0.85), keywords ["tarjeta", "rechazada"]
- Resultados de pruebas: 90% accuracy sentimiento (18/20), 100% extracción keywords relevantes
- Observaciones: BETO mejora detección de negación vs. lexicones tradicionales

**Dependencias**:

- ⬇️ Recibe datos de: Módulo 1 (mensaje crudo del usuario)
- ➡️ Procesa con: Pipeline spaCy → Tokenización → BETO (sentiment)
- ⬆️ Envía resultados a: Módulo 4 (keywords para Neo4j), Módulo 3 (sentimiento para fuzzy)

**Comparativa de modelos de sentimiento**:

```
Modelo              Accuracy   Latencia   Manejo de Negación
─────────────────────────────────────────────────────────────
VADER (lexicon)        65%      10 ms           ❌ Pobre
TextBlob ES            70%      15 ms           ❌ Limitado
BETO fine-tuned        90%     800 ms           ✅ Excelente

Ejemplo crítico:
Mensaje: "No me gusta que mi pago NO fue rechazado"
VADER:    Negativo (error - doble negación)
BETO:     Positivo (correcto - entiende contexto)
```


***

### **MÓDULO 8: INTEGRACIÓN GENERATIVA**

📄 **Archivo**: `MODULO_8_INTEGRACION_GENERATIVA.md`

**Contenido**:

- Propósito: Generación de respuestas personalizadas mediante Large Language Model
- Entradas: Categoría detectada, solución de Neo4j, tipo de usuario, sentimiento
- Salidas: Respuesta en lenguaje natural adaptada al contexto
- Herramientas: Ollama (servidor local), Llama 3.2 3B (modelo), API REST
- Código relevante: Función `generar_respuesta_ollama()` con prompt engineering
- Ejemplos: Prospecto + sentimiento negativo → tono empático y persuasivo
- Resultados de pruebas: 100% coherencia contextual (20/20), latencia 700 ms
- Observaciones: Control de temperatura (0.7) balancea creatividad y precisión

**Dependencias**:

- ⬇️ Recibe datos de: Módulo 4 (categoría + solución), Módulo 7 (sentimiento), Módulo 1 (tipo usuario)
- ➡️ Procesa con: Llama 3.2 con prompt context-aware
- ⬆️ Envía resultados a: Módulo 1 (respuesta final), Módulo 9 (visualización)

**Configuración de prompts por tipo de usuario**:

```python
PROMPTS = {
    "prospecto": """
        Eres un asistente de ventas de Wevently. El usuario está considerando 
        usar la plataforma. Sé persuasivo, empático y destaca beneficios.
        Problema: {categoria}
        Solución: {solucion}
        Sentimiento del usuario: {sentimiento}
        Genera respuesta en máximo 3 párrafos.
    """,
    "cliente_activo": """
        Eres soporte técnico de Wevently. El usuario ya es cliente.
        Sé conciso, técnico y orientado a resolver rápidamente.
        Problema: {categoria}
        Solución: {solucion}
        Genera respuesta con pasos específicos.
    """,
    "organizador": """
        Eres consultor de Wevently para organizadores de eventos.
        El usuario gestiona eventos grandes. Sé profesional y estratégico.
        Problema: {categoria}
        Solución: {solucion}
        Genera respuesta con mejores prácticas.
    """
}
```


***

### **MÓDULO 9: API DEL ASISTENTE**

📄 **Archivo**: `MODULO_9_API_ASISTENTE.md`

**Contenido**:

- Propósito: Interfaz web para interacción del usuario final con el sistema completo
- Entradas: Mensaje de texto desde input web, selección de tipo de usuario
- Salidas: Respuesta visualizada en chat, historial de conversación
- Herramientas: Streamlit 1.28.0, HTML/CSS personalizado, `st.session_state`
- Código relevante: Aplicación principal `app.py`, función `render_interfaz_chat()`
- Ejemplos: Usuario escribe "¿Cómo recupero mi dinero?" → sistema responde en 4.2 seg
- Resultados de pruebas: 99.2% uptime (8h pruebas), soporta 5 usuarios concurrentes
- Observaciones: Adecuado para MVP académico, requiere migración a FastAPI para producción

**Dependencias**:

- ⬇️ Recibe datos de: Usuario final (navegador web)
- ➡️ Procesa con: Orquestación de Módulos 1-8
- ⬆️ Envía resultados a: Navegador (HTML renderizado)

***

## **FLUJO DE DATOS COMPLETO - EJEMPLO END-TO-END**

```
┌─────────────────────────────────────────────────────────────────────┐
│  CASO DE USO: Usuario prospecto pregunta sobre pago rechazado       │
└─────────────────────────────────────────────────────────────────────┘

[USUARIO] Escribe en interfaz Streamlit:
  "Hola, mi tarjeta fue rechazada al intentar comprar entradas"

      ▼
[MÓDULO 9] Captura mensaje + tipo_usuario="prospecto"
  └──> Envía a generar_respuesta_streamlit()

      ▼
[MÓDULO 1] Inicia orquestación
  ├──> Registra inicio en logs (MÓDULO 5)
  └──> Envía mensaje a análisis NLP

      ▼
[MÓDULO 7] Procesa con spaCy + BETO
  ├──> Tokens: ["tarjeta", "rechazada", "comprar", "entradas"]
  ├──> Keywords: ["tarjeta", "rechazada"]
  └──> Sentimiento: NEGATIVO (-0.85)

      ▼
[MÓDULO 4] Query Neo4j con keywords
  ├──> Cypher: MATCH (n) WHERE n.nombre CONTAINS "tarjeta" AND 
  │            n.nombre CONTAINS "rechazada" RETURN n
  ├──> Resultado: nodo "Rechazo_Tarjeta"
  ├──> Solución: "Verificar fondos, validar datos tarjeta, contactar banco"
  └──> Coincidencia: 85%

      ▼
[MÓDULO 3] Calcula confianza fuzzy
  ├──> Input: coincidencia=85%, sentimiento=-0.85, longitud=62
  ├──> Membership: coincidencia=ALTA, sentimiento=NEGATIVO
  ├──> Regla activada: IF coincidencia ALTA AND sentimiento NEGATIVO 
  │                     THEN confianza ALTA
  └──> Output: confianza = 0.87

      ▼
[MÓDULO 8] Genera respuesta con Ollama
  ├──> Prompt: "Usuario prospecto con problema 'Rechazo_Tarjeta', 
  │             sentimiento negativo. Solución: {solucion}"
  ├──> Llama 3.2 genera respuesta empática y persuasiva
  └──> Respuesta: "Entiendo tu frustración al no poder completar 
                   tu compra. El rechazo de tarjeta puede ocurrir 
                   por varias razones: fondos insuficientes, datos 
                   incorrectos o restricciones del banco. Te 
                   recomiendo: 1) Verificar saldo disponible, 
                   2) Confirmar número y CVV, 3) Contactar a tu 
                   banco. En Wevently procesamos pagos de forma 
                   segura con múltiples métodos. ¿Te gustaría 
                   intentar con otra tarjeta?"

      ▼
[MÓDULO 1] Ensambla respuesta final
  ├──> Registra fin en logs (MÓDULO 5): "Total: 4.2 segundos"
  └──> Retorna diccionario: {
         "respuesta": "...",
         "categoria": "Rechazo_Tarjeta",
         "confianza": 0.87
       }

      ▼
[MÓDULO 9] Renderiza en interfaz
  └──> Muestra respuesta en burbuja de chat del asistente
       con timestamp y efecto de fade-in

[USUARIO] Lee respuesta y continúa conversación
```

**Métricas del flujo completo**:

- ✅ Latencia total: 4.2 segundos
- ✅ Categoría correcta: Sí (Rechazo_Tarjeta)
- ✅ Confianza adecuada: 0.87 (ALTA)
- ✅ Respuesta contextualizada: Sí (tono empático + persuasivo)
- ✅ Información útil: Sí (pasos accionables)


## **MATRIZ DE DEPENDENCIAS ENTRE MÓDULOS**

```
┌─────────────────────────────────────────────────────────────────────┐
│           MATRIZ DE DEPENDENCIAS (9x9)                              │
│  Filas = Módulo origen | Columnas = Módulo destino                 │
└─────────────────────────────────────────────────────────────────────┘

        │ M1 │ M2 │ M3 │ M4 │ M5 │ M6 │ M7 │ M8 │ M9 │
────────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
M1      │ -  │ ✓  │ ✓  │ ✓  │ ✓  │ ✗  │ ✓  │ ✓  │ ←→ │
M2      │ ✗  │ -  │ ✗  │ →  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │
M3      │ ←  │ ✗  │ -  │ ←  │ →  │ ✗  │ ←  │ ✗  │ ✗  │
M4      │ ←  │ ←  │ →  │ -  │ →  │ ✗  │ ←  │ ✗  │ ✗  │
M5      │ ←  │ ←  │ ←  │ ←  │ -  │ ✗  │ ←  │ ←  │ ←  │
M6      │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ -  │ ✗  │ ✗  │ ✗  │
M7      │ ←  │ ✗  │ →  │ →  │ →  │ ✗  │ -  │ ✗  │ ✗  │
M8      │ ←  │ ✗  │ ✗  │ ←  │ →  │ ✗  │ ←  │ -  │ ✗  │
M9      │ ←→ │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ -  │

Leyenda:
  ✓  = Módulo origen coordina/invoca módulo destino
  ←  = Módulo origen recibe datos de módulo destino
  →  = Módulo origen envía datos a módulo destino
  ←→ = Comunicación bidireccional
  ✗  = Sin dependencia
  -  = Mismo módulo
```

**Observaciones críticas**:

- **Módulo 1** es el orquestador central (6 dependencias directas)
- **Módulo 5** recibe datos de todos los módulos activos (logging centralizado)
- **Módulo 6** está completamente aislado (no implementado)
- **Módulo 9** solo interactúa con Módulo 1 (desacoplamiento correcto)
- **Módulos 2+4** forman subsistema de conocimiento (red semántica + persistencia)
- **Módulos 7+8** forman subsistema de IA (NLP + generación)

***

## **TECNOLOGÍAS Y HERRAMIENTAS POR MÓDULO**

| **Módulo** | **Lenguajes** | **Frameworks/Librerías** | **Servicios Externos** | **Versión Mínima** |
| :-- | :-- | :-- | :-- | :-- |
| **M1** | Python 3.11 | logging (stdlib) | - | Python ≥3.11 |
| **M2** | Cypher | - | Neo4j AuraDB | Neo4j ≥5.14 |
| **M3** | Python 3.11 | scikit-fuzzy 0.4.2, numpy | - | scikit-fuzzy ≥0.4.2 |
| **M4** | Python 3.11, Cypher | langchain-neo4j 0.1.0, neo4j-driver | Neo4j AuraDB | neo4j ≥5.14 |
| **M5** | Python 3.11 | logging (stdlib), time | - | Python ≥3.11 |
| **M6** | - | - | - | NO IMPLEMENTADO |
| **M7** | Python 3.11 | spaCy 3.7.0, transformers 4.30.0 | Hugging Face (BETO) | spaCy ≥3.7 |
| **M8** | Python 3.11 | requests, json | Ollama (local) | Ollama ≥0.1.0 |
| **M9** | Python 3.11, HTML/CSS | Streamlit 1.28.0 | - | Streamlit ≥1.28 |

**Stack tecnológico consolidado**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    STACK TECNOLÓGICO WEVENTLY                    │
└─────────────────────────────────────────────────────────────────┘

LENGUAJES
  • Python 3.11 (core del sistema)
  • Cypher (queries Neo4j)
  • HTML/CSS (interfaz Streamlit)

FRAMEWORKS
  • Streamlit 1.28.0 (frontend web)
  • spaCy 3.7.0 (NLP pipeline)
  • Transformers 4.30.0 (modelos BERT)
  • scikit-fuzzy 0.4.2 (lógica difusa)
  • langchain-neo4j 0.1.0 (integración grafos)

BASES DE DATOS
  • Neo4j 5.14.0 (grafo de conocimiento)
  • Neo4j AuraDB (hosting remoto)

MODELOS DE IA
  • es_core_news_md (spaCy español)
  • BETO fine-tuned (sentiment analysis)
  • Llama 3.2 3B (generación de texto)

INFRAESTRUCTURA
  • Ollama (servidor LLM local)
  • Python logging (auditoría)
  • pip/venv (gestión de dependencias)
```


***

## **MÉTRICAS CONSOLIDADAS DEL SISTEMA**

### **Rendimiento General**

| **Aspecto** | **Métrica** | **Valor Objetivo** | **Valor Medido** | **Estado** |
| :-- | :-- | :-- | :-- | :-- |
| Latencia total | Tiempo de respuesta | < 5 seg | 4.2 seg | ✅ Aprobado |
| Accuracy clasificación | Categorización correcta | > 90% | 95% (19/20) | ✅ Aprobado |
| Confianza promedio | Output fuzzy | > 0.70 | 0.87 | ✅ Aprobado |
| Detección sentimiento | Precisión NLP | > 80% | 90% (18/20) | ✅ Aprobado |
| Coherencia LLM | Respuestas relevantes | 100% | 100% (20/20) | ✅ Aprobado |
| Disponibilidad | Uptime interfaz | > 95% | 99.2% | ✅ Aprobado |
| Concurrencia | Usuarios simultáneos | 3-5 | 5 usuarios | ✅ Aprobado |

### **Desglose de Latencia por Módulo**

```
┌─────────────────────────────────────────────────────────────────┐
│         DISTRIBUCIÓN DE LATENCIA (Total: 4200 ms)               │
└─────────────────────────────────────────────────────────────────┘

Módulo 4 (Neo4j remota)    ████████████████████████████  2500 ms (60%)
Módulo 7 (spaCy + BETO)    ████████████                   800 ms (19%)
Módulo 8 (Ollama LLM)      ███████████                    700 ms (17%)
Módulo 3 (Fuzzy Logic)     ███                            150 ms (4%)
Módulo 9 (Streamlit)       █                               50 ms (1%)
Módulo 1 (Orquestación)    (despreciable)                  <5 ms (0%)
Módulo 5 (Logging)         (despreciable)                  <5 ms (0%)

OPTIMIZACIONES PROPUESTAS:
1. Neo4j local: 2500 ms → 200 ms (reducción 92%)
2. ONNX para BETO: 800 ms → 300 ms (reducción 62%)
3. Ollama optimizado: 700 ms → 500 ms (reducción 29%)

LATENCIA PROYECTADA POST-OPTIMIZACIÓN: ~1.1 segundos (74% mejora)
```


### **Cobertura Funcional**

| **Capacidad** | **Implementado** | **Cobertura** | **Notas** |
| :-- | :-- | :-- | :-- |
| Clasificación de consultas | ✅ Sí | 12 categorías | Pagos, tarjetas, eventos, cuenta |
| Análisis de sentimiento | ✅ Sí | 3 clases | Positivo, negativo, neutro |
| Personalización por usuario | ✅ Sí | 3 tipos | Prospecto, cliente, organizador |
| Generación contextual | ✅ Sí | LLM adaptativo | Temperatura 0.7 |
| Persistencia conversacional | ⚠️ Parcial | Solo sesión activa | Sin BD permanente |
| Autenticación | ❌ No | N/A | Mejora futura |
| Analytics/Métricas | ❌ No | N/A | Mejora futura |
| Multiidioma | ❌ No | Solo español | BETO no multilingüe |


***

## **CASOS DE PRUEBA DOCUMENTADOS**

### **Batería de Pruebas Ejecutadas (n=20)**

```
┌─────────────────────────────────────────────────────────────────┐
│                   CASOS DE PRUEBA - RESUMEN                      │
└─────────────────────────────────────────────────────────────────┘

CATEGORÍA: PAGOS (n=7)
✅ "Mi pago fue rechazado" → Rechazo_Pago (confianza 0.92)
✅ "No me llegó el reembolso" → Reembolso (confianza 0.88)
✅ "¿Cuándo me devuelven el dinero?" → Reembolso (confianza 0.85)
✅ "Error al procesar pago con tarjeta" → Error_Pago (confianza 0.90)
✅ "Cobro duplicado en mi cuenta" → Cobro_Duplicado (confianza 0.93)
✅ "¿Aceptan transferencia bancaria?" → Metodos_Pago (confianza 0.87)
✅ "Quiero cambiar mi método de pago" → Metodos_Pago (confianza 0.84)

CATEGORÍA: TARJETAS (n=5)
✅ "Mi tarjeta fue rechazada" → Rechazo_Tarjeta (confianza 0.87)
✅ "No puedo agregar mi tarjeta" → Error_Tarjeta (confianza 0.89)
✅ "¿Qué tarjetas aceptan?" → Tarjetas_Aceptadas (confianza 0.91)
✅ "Datos de tarjeta incorrectos" → Datos_Tarjeta (confianza 0.86)
❌ "Mi Visa no funciona" → Clasificado como Error_Pago (esperado: Error_Tarjeta)

CATEGORÍA: EVENTOS (n=4)
✅ "Cómo creo un evento" → Crear_Evento (confianza 0.90)
✅ "No encuentro mi evento publicado" → Gestionar_Evento (confianza 0.83)
✅ "¿Puedo cancelar un evento?" → Cancelar_Evento (confianza 0.88)
✅ "Modificar fecha del evento" → Editar_Evento (confianza 0.85)

CATEGORÍA: CUENTA (n=4)
✅ "Olvidé mi contraseña" → Recuperar_Cuenta (confianza 0.92)
✅ "Cómo cambio mi email" → Editar_Perfil (confianza 0.87)
✅ "No puedo iniciar sesión" → Login_Error (confianza 0.89)
✅ "Eliminar mi cuenta" → Borrar_Cuenta (confianza 0.91)

ACCURACY TOTAL: 95% (19/20 correctos)
CONFIANZA PROMEDIO: 0.88
CASOS FALLIDOS: 1 (confusión Visa → Error_Pago)
```

**Análisis del caso fallido**:

- Input: "Mi Visa no funciona"
- Esperado: `Rechazo_Tarjeta` o `Error_Tarjeta`
- Obtenido: `Error_Pago`
- Causa raíz: Keywords ["visa", "funciona"] no tienen peso suficiente para "tarjeta" en Neo4j
- Solución: Agregar sinónimos en red semántica (Visa, Mastercard, Amex → tipo de Tarjeta)

***

## **LIMITACIONES GLOBALES DEL SISTEMA**

### **Limitaciones Técnicas**

1. **Latencia de Neo4j Remota** (Crítica - Alto Impacto)
    - Problema: 60% de latencia total (2.5 seg) en queries a AuraDB
    - Impacto: Percepción de lentitud en usuarios
    - Solución: Migrar a Neo4j local o implementar caché con Redis
    - Esfuerzo: Medio (2-3 días configuración + migración)
2. **Sin Persistencia entre Sesiones** (Alta - Alto Impacto)
    - Problema: Historial se pierde al cerrar navegador
    - Impacto: Imposible análisis histórico, continuidad conversacional limitada
    - Solución: Implementar SQLite/PostgreSQL para logs de conversaciones
    - Esfuerzo: Medio (3-5 días diseño schema + integración)
3. **Escalabilidad Limitada de Streamlit** (Media - Medio Impacto)
    - Problema: Diseñado para ≤50 usuarios concurrentes
    - Impacto: No apto para producción con tráfico alto
    - Solución: Migrar a FastAPI + React
    - Esfuerzo: Alto (3-4 semanas desarrollo full-stack)
4. **Sin Streaming de Respuestas LLM** (Media - Medio Impacto)
    - Problema: Ollama genera respuesta completa antes de mostrarla
    - Impacto: 3-7 segundos sin feedback visual (percepción de congelamiento)
    - Solución: Implementar streaming con `ollama.generate(stream=True)` + WebSockets
    - Esfuerzo: Bajo (1-2 días implementación)
5. **Modelo BETO No Optimizado** (Media - Medio Impacto)
    - Problema: Inferencia BETO consume 800 ms (19% de latencia total)
    - Impacto: Lentitud acumulativa en conversaciones largas
    - Solución: Convertir a ONNX Runtime (reducción proyectada 60%)
    - Esfuerzo: Medio (2-3 días conversión + validación)
6. **Sin Autenticación de Usuarios** (Alta - Bajo Impacto Inmediato)
    - Problema: Todos los usuarios anónimos, sin personalización real
    - Impacto: No hay contexto de usuario histórico, imposible analytics por usuario
    - Solución: JWT tokens + OAuth2 (Google/Facebook login)
    - Esfuerzo: Medio (3-4 días implementación + testing)

### **Limitaciones Funcionales**

1. **Cobertura Limitada de Categorías** (Media)
    - Actualmente: 12 categorías en Neo4j
    - Problema: Consultas fuera de dominio (ej: "¿Tienen app móvil?") no clasifican correctamente
    - Solución: Expandir red semántica a 30-40 categorías, agregar nodo "Fuera_De_Alcance"
    - Esfuerzo: Medio (1 semana investigación + expansión de grafo)
2. **Sin Capacidad Multiidioma** (Baja - Contexto Académico)
    - Problema: Solo español (modelo BETO)
    - Impacto: No apto para mercados internacionales
    - Solución: Usar XLM-RoBERTa (multilingüe) o detectar idioma + modelo específico
    - Esfuerzo: Alto (2 semanas integración + reentrenamiento)
3. **Sin Manejo de Diálogos Multi-Turn** (Media)
    - Problema: Cada consulta es independiente, no usa contexto de mensajes previos
    - Impacto: Usuario debe repetir información ("¿Y si uso otra tarjeta?" → no entiende contexto)
    - Solución: Implementar ventana de contexto (últimos 3-5 mensajes) en prompt de Ollama
    - Esfuerzo: Bajo (2-3 días modificación de prompt + session_state)
4. **Sin Validación de Respuestas Generadas** (Baja - Ollama Confiable)
    - Problema: No hay verificación de alucinaciones o información incorrecta
    - Impacto: Potencial de respuestas con datos inventados (raro con Llama 3.2)
    - Solución: Implementar fact-checking contra Neo4j o temperatura más baja (0.5)
    - Esfuerzo: Medio (1 semana pipeline de validación)

***

## **RECOMENDACIONES DE EVOLUCIÓN**

### **Fase 1: Optimizaciones Inmediatas (1 mes)**

**Prioridad CRÍTICA** (Impacto Alto, Esfuerzo Bajo):

```python
# 1. Implementar caché de queries Neo4j con Redis
from functools import lru_cache
import hashlib

@lru_cache(maxsize=256)
def cypher_query_cached(mensaje: str, usuario_tipo: str):
    """Cache de queries frecuentes para reducir latencia Neo4j."""
    cache_key = hashlib.md5(f"{mensaje}_{usuario_tipo}".encode()).hexdigest()
    # Implementación con Redis
    resultado = redis_client.get(cache_key)
    if resultado:
        return json.loads(resultado)
    resultado = cypher_query(mensaje, usuario_tipo)
    redis_client.setex(cache_key, 3600, json.dumps(resultado))  # TTL 1h
    return resultado

# Reducción esperada: 2500 ms → 50 ms (95% en queries cacheadas)
```

**Prioridad ALTA** (Impacto Alto, Esfuerzo Medio):

```python
# 2. Persistencia de conversaciones con SQLite
import sqlite3
from datetime import datetime

def guardar_conversacion(sesion_id: str, mensaje: str, respuesta: str, 
                         categoria: str, confianza: float):
    """Guarda historial en base de datos local."""
    conn = sqlite3.connect("wevently_chat.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversaciones 
        (sesion_id, fecha, mensaje, respuesta, categoria, confianza)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sesion_id, datetime.now(), mensaje, respuesta, categoria, confianza))
    conn.commit()
    conn.close()

# Beneficio: Análisis histórico, continuidad entre sesiones
```

**Prioridad MEDIA** (Impacto Medio, Esfuerzo Bajo):

```python
# 3. Streaming de respuestas Ollama
def generar_respuesta_stream(prompt: str):
    """Genera respuesta con streaming token por token."""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2:3b", "prompt": prompt, "stream": True},
        stream=True
    )
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            yield chunk['response']

# En Streamlit:
placeholder = st.empty()
respuesta_completa = ""
for token in generar_respuesta_stream(prompt):
    respuesta_completa += token
    placeholder.markdown(respuesta_completa + "▌")  # Cursor parpadeante
placeholder.markdown(respuesta_completa)

# Beneficio: Feedback visual inmediato, reduce percepción de latencia
```


### **Fase 2: Arquitectura de Producción (3 meses)**

**Migración a Stack Moderno**:

```
┌─────────────────────────────────────────────────────────────────┐
│           ARQUITECTURA PROPUESTA PARA PRODUCCIÓN                 │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │   React Frontend     │
                    │  (TypeScript + Vite) │
                    │  • Chat UI moderno   │
                    │  • Streaming WS      │
                    │  • PWA móvil         │
                    └──────────────────────┘
                              │
                              ▼ HTTPS
                    ┌──────────────────────┐
                    │  NGINX Reverse Proxy │
                    │  • Load balancing    │
                    │  • SSL/TLS           │
                    │  • Rate limiting     │
                    └──────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
     ┌─────────────────────┐    ┌─────────────────────┐
     │  FastAPI Backend #1 │    │  FastAPI Backend #2 │
     │  (Gunicorn workers) │    │  (Horizontal scale) │
     │  • REST API         │    │  • WebSocket        │
     │  • JWT auth         │    │  • Async I/O        │
     └─────────────────────┘    └─────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
                ┌──────────────────────────────┐
                │  Redis (Cache + Sessions)    │
                │  • Query cache Neo4j         │
                │  • Session tokens            │
                │  • Rate limiting counters    │
                └──────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ PostgreSQL     │  │ Neo4j Local    │  │ Ollama Cluster │
│ • User data    │  │ • Knowledge    │  │ • LLM serving  │
│ • Chat logs    │  │ • Fast queries │  │ • GPU accel    │
│ • Analytics    │  │ • 100-200 ms   │  │ • Replication  │
└────────────────┘  └────────────────┘  └────────────────┘
```

**Stack de Producción**:

- **Frontend**: React 18 + TypeScript + Tailwind CSS + Zustand (state)
- **Backend**: FastAPI 0.100+ + Pydantic V2 + SQLAlchemy 2.0
- **Cache**: Redis 7.0 (caché de queries + sesiones)
- **Base de datos**: PostgreSQL 15 (logs, usuarios, analytics)
- **Grafo**: Neo4j 5.14 Community (instancia local)
- **LLM**: Ollama con replicación (2-3 instancias para balanceo)
- **Monitoreo**: Prometheus + Grafana
- **CI/CD**: GitHub Actions + Docker Compose

**Beneficios esperados**:

- ✅ Latencia total < 1.5 segundos (65% mejora)
- ✅ Escalabilidad a 500+ usuarios concurrentes
- ✅ Persistencia completa con analytics
- ✅ Autenticación y personalización real
- ✅ APIs públicas para integraciones third-party
- ✅ Monitoreo en tiempo real de métricas


### **Fase 3: Capacidades Avanzadas (6 meses)**

1. **Sistema de Recomendaciones**
    - ML model para sugerir eventos basados en historial de usuario
    - Collaborative filtering con Neo4j Graph Data Science
2. **Análisis de Sentimiento en Tiempo Real**
    - Dashboard para organizadores: métricas de satisfacción de usuarios
    - Alertas automáticas si sentimiento negativo > 30%
3. **Chatbot Multicanal**
    - Integración con WhatsApp Business API
    - Bot de Telegram
    - Widget embebible para sitios externos
4. **A/B Testing de Prompts**
    - Experimentación con diferentes estrategias de prompt
    - Métricas de conversión por variante
5. **Fine-tuning de Llama 3.2**
    - Entrenamiento con dataset específico de Wevently
    - Mejora de coherencia en respuestas de dominio

***

## **CONCLUSIONES GENERALES DEL PROYECTO**

### **Logros Técnicos del Sistema de 9 Módulos**

El proyecto **Wevently Chatbot** demuestra exitosamente la viabilidad de construir un **asistente virtual inteligente** mediante la integración de múltiples paradigmas de IA:

1. **Enfoque Simbólico** (Módulos 2, 4): Red semántica en Neo4j proporciona conocimiento estructurado y explicable, logrando 95% de accuracy en clasificación sin necesidad de entrenamiento supervisado.
2. **Lógica Difusa** (Módulo 3): Sistema fuzzy basado en scikit-fuzzy maneja incertidumbre de forma más robusta que umbrales binarios, con confianza promedio de 0.87.
3. **Procesamiento de Lenguaje Natural** (Módulo 7): Pipeline spaCy + BETO fine-tuned alcanza 90% de precisión en análisis de sentimiento, crítico para personalización de respuestas.
4. **Generación con LLMs** (Módulo 8): Llama 3.2 3B vía Ollama produce respuestas 100% coherentes y contextualizadas, adaptándose a tipo de usuario (prospecto/cliente/organizador).
5. **Orquestación Efectiva** (Módulos 1, 5, 9): Arquitectura modular permite mantenibilidad, trazabilidad (logging exhaustivo) y experiencia de usuario fluida (interfaz Streamlit).

### **Decisiones Arquitectónicas Clave**

**✅ Decisiones Acertadas**:

- **No implementar Módulo 6 (ML supervisado)**: Random Forest con 48% accuracy era inferior a enfoque simbólico (95%). Priorizar precisión sobre automatización fue correcto para dominio financiero donde errores tienen alto costo.
- **Usar Neo4j para conocimiento**: Grafos permiten relaciones complejas (ej: "Rechazo_Tarjeta" → "Verificar_Fondos" → "Contactar_Banco") que serían difíciles en bases relacionales. Queries Cypher son más expresivas que SQL para navegación conceptual.
- **Lógica fuzzy para confianza**: Manejo de incertidumbre con memberships continuas (BAJA/MEDIA/ALTA) es más realista que `if confidence > 0.8` binario. Reduce falsos positivos y permite ajuste fino de umbrales.
- **Ollama local vs. APIs pagas**: Hosting local de Llama 3.2 elimina costos por token (OpenAI/Anthropic) y garantiza privacidad. Para contexto académico y MVP, es óptimo.
- **Streamlit para prototipo**: Desarrollo rápido (< 1 semana para interfaz completa) permitió validar integración end-to-end. Adecuado para PG7 aunque limitado para producción.

**⚠️ Trade-offs Aceptados**:

- **Latencia Neo4j remota (2.5 seg)**: Usar AuraDB (cloud) simplificó setup pero sacrificó performance. Para MVP académico aceptable, producción requiere instancia local.
- **Sin persistencia entre sesiones**: `st.session_state` volátil es suficiente para demo pero inadecuado para usuarios reales. SQLite/PostgreSQL agregaría complejidad prematura para PG7.
- **Modelo BETO no optimizado**: 800 ms de inferencia es alto pero aceptable en pipeline de 4.2 seg. ONNX reduciría 60% pero requiere tooling adicional (onnxruntime, conversión).
