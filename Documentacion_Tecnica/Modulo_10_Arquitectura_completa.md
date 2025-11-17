# **Arquitectura Completa del Sistema Inteligente Wevently**

## **Flujo de Interacción entre Módulos**


***

## **1. Visión General del Sistema**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SISTEMA INTELIGENTE WEVENTLY                     │
│          Asistente Virtual para Gestión de Eventos                  │
└─────────────────────────────────────────────────────────────────────┘

Componentes: 9 Módulos Integrados
Objetivo: Procesar consultas en lenguaje natural y generar respuestas
          personalizadas usando IA simbólica + ML + LLM
```


***

## **2. Diagrama de Arquitectura Completa**

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CAPA DE PRESENTACIÓN                              │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 9: API del Asistente (Streamlit)                          │  │
│  │  - Interface visual estilo WhatsApp                                │  │
│  │  - Selector de rol (Organizador/Prestador/Propietario)            │  │
│  │  - Gestión de sesión y historial de chat                          │  │
│  │  - Renderizado de burbujas y metadatos                            │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                        │
│                                  │ Usuario envía mensaje                 │
│                                  ▼                                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE ORQUESTACIÓN                                 │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 1: Orquestador Principal                                   │  │
│  │  generar_respuesta_streamlit(pregunta, tipo_usuario)              │  │
│  │                                                                     │  │
│  │  Responsabilidades:                                                │  │
│  │  ✓ Coordinar ejecución secuencial de todos los módulos            │  │
│  │  ✓ Aplicar reglas de negocio (DOMAIN_KEYWORDS, umbrales)          │  │
│  │  ✓ Gestionar múltiples puntos de fallback                         │  │
│  │  ✓ Personalizar según rol y emoción                               │  │
│  │  ✓ Logging completo y persistencia de métricas                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                        │
└──────────────────────────────────┼────────────────────────────────────────┘
                                   │
                                   │ Inicio del flujo
                                   ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE DECISIÓN INTELIGENTE                           │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 5: Planificador Dinámico                                  │  │
│  │  planificar_flujo(pregunta, tipo_usuario)                         │  │
│  │                                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  1. Clasificación ML Pre-Filtro (Módulo 6)                   │ │  │
│  │  │     - Modelo: RandomForest (48% accuracy)                     │ │  │
│  │  │     - Categorías: 15 tipos de problemas                       │ │  │
│  │  │     - Latencia: ~10-15 ms                                     │ │  │
│  │  │     ├─→ categoría_ml: "RechazoTarjeta"                        │ │  │
│  │  │     └─→ confianza_ml: 0.45                                    │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                  │                                 │  │
│  │  ┌──────────────────────────────▼───────────────────────────────┐ │  │
│  │  │  2. Extracción de Keywords (Módulo 7 - spaCy)               │ │  │
│  │  │     - Pipeline: tokenización → lematización → filtrado       │ │  │
│  │  │     - Latencia: ~81 ms                                        │ │  │
│  │  │     └─→ keywords: ["tarjeta", "rechazar", "hacer"]           │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                  │                                 │  │
│  │  ┌──────────────────────────────▼───────────────────────────────┐ │  │
│  │  │  3. DECISIÓN: ¿Ejecutar flujo completo?                      │ │  │
│  │  │                                                                │ │  │
│  │  │  VALIDACIÓN 1: categoría_ml != "NoRepresentaAlDominio" ✓     │ │  │
│  │  │  VALIDACIÓN 2: confianza_ml >= 0.10 (umbral) ✓               │ │  │
│  │  │  VALIDACIÓN 3: keywords ∩ DOMAIN_KEYWORDS != ∅ ✓             │ │  │
│  │  │                                                                │ │  │
│  │  │  ├─[TODAS ✓]─→ ejecutar_flujo_completo = True                │ │  │
│  │  │  └─[ALGUNA ✗]─→ ejecutar_flujo_completo = False              │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                            │                   │                          │
│                    [True]  │                   │  [False]                 │
│                            │                   │                          │
└────────────────────────────┼───────────────────┼──────────────────────────┘
                             │                   │
                             │                   └─→ FALLBACK INMEDIATO
                             │                       "Lo siento, no puedo
                             │                        ayudar con ese tipo
                             │                        de consulta."
                             │                       
                             ▼
      ┌─────────────────────────────────────────┐
      │  CONTINUAR FLUJO COMPLETO               │
      └─────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE PROCESAMIENTO NLP                              │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 7: Integración NLP (spaCy + Transformers)                 │  │
│  │                                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  A. Extracción de Keywords (spaCy - es_core_news_md)        │ │  │
│  │  │     detect_keywords(texto)                                    │ │  │
│  │  │                                                               │ │  │
│  │  │     Input: "Mi tarjeta fue rechazada dos veces"              │ │  │
│  │  │     Pipeline:                                                 │ │  │
│  │  │       1. Tokenización → ["Mi","tarjeta","fue"...]            │ │  │
│  │  │       2. Lematización → ["mi","tarjeta","ser","rechazar"...] │ │  │
│  │  │       3. Filtrado (stopwords, alfabéticos)                   │ │  │
│  │  │       4. Normalización (lowercase)                           │ │  │
│  │  │                                                               │ │  │
│  │  │     Output: ["tarjeta", "rechazar", "vez", "hacer"]          │ │  │
│  │  │     Latencia: ~81 ms                                         │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                  │                                 │  │
│  │  ┌──────────────────────────────▼───────────────────────────────┐ │  │
│  │  │  B. Detección de Emoción (BETO-TASS-2025-II)                │ │  │
│  │  │     detect_emotion(texto)                                     │ │  │
│  │  │                                                               │ │  │
│  │  │     Input: "Mi tarjeta fue rechazada dos veces"              │ │  │
│  │  │     Pipeline:                                                 │ │  │
│  │  │       1. Tokenización BERT (WordPiece)                       │ │  │
│  │  │       2. Inferencia BETO (12 capas transformer)              │ │  │
│  │  │       3. Clasificación 6 clases                              │ │  │
│  │  │       4. Softmax → probabilidades                            │ │  │
│  │  │                                                               │ │  │
│  │  │     Probabilidades:                                           │ │  │
│  │  │       alegría: 0.02                                          │ │  │
│  │  │       enojo: 0.87 ← MÁXIMO                                   │ │  │
│  │  │       asco: 0.03                                             │ │  │
│  │  │       miedo: 0.01                                            │ │  │
│  │  │       tristeza: 0.06                                         │ │  │
│  │  │       sorpresa: 0.01                                         │ │  │
│  │  │                                                               │ │  │
│  │  │     Output: ("enojo", 0.87)                                  │ │  │
│  │  │     Latencia: ~1080 ms (53% del Módulo 7)                   │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                        │
│                                  │ keywords + emoción                    │
│                                  ▼                                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE VALIDACIÓN DIFUSA                              │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 3: Lógica Difusa (scikit-fuzzy)                           │  │
│  │  fuzzy_problem_categorization(keywords)                           │  │
│  │                                                                     │  │
│  │  Input: keywords = ["tarjeta", "rechazar", "hacer"]               │  │
│  │         matched_count = 3                                          │  │
│  │                                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  Sistema de Inferencia Difusa (Mamdani)                      │ │  │
│  │  │                                                                │ │  │
│  │  │  Variable de entrada: num_keywords [0-5]                     │ │  │
│  │  │  Conjuntos difusos:                                          │ │  │
│  │  │    - BAJO: [0,0,2]  trimf                                    │ │  │
│  │  │    - MEDIO: [1,3,5] trimf                                    │ │  │
│  │  │    - ALTO: [3,5,5]  trimf                                    │ │  │
│  │  │                                                                │ │  │
│  │  │  Variable de salida: confianza [0.0-1.0]                     │ │  │
│  │  │  Conjuntos difusos:                                          │ │  │
│  │  │    - BAJA: [0,0,0.7]  trimf                                  │ │  │
│  │  │    - ALTA: [0.6,1,1]  trimf                                  │ │  │
│  │  │                                                                │ │  │
│  │  │  Reglas:                                                      │ │  │
│  │  │    R1: IF bajo  → THEN baja                                  │ │  │
│  │  │    R2: IF medio → THEN baja                                  │ │  │
│  │  │    R3: IF alto  → THEN alta                                  │ │  │
│  │  │                                                                │ │  │
│  │  │  Fuzzificación (num_keywords = 3):                           │ │  │
│  │  │    μ_bajo(3) = 0.0                                           │ │  │
│  │  │    μ_medio(3) = 0.67                                         │ │  │
│  │  │    μ_alto(3) = 0.67                                          │ │  │
│  │  │                                                                │ │  │
│  │  │  Inferencia:                                                  │ │  │
│  │  │    R1 NO activa (grado = 0.0)                                │ │  │
│  │  │    R2 activa con grado 0.67 → baja                           │ │  │
│  │  │    R3 activa con grado 0.67 → alta                           │ │  │
│  │  │                                                                │ │  │
│  │  │  Defuzzificación (centroide):                                │ │  │
│  │  │    confianza = 0.90                                          │ │  │
│  │  └──────────────────────────────────────────────────```
│  │  │    confianza = 0.90                                          │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                     │  │
│  │  Output: confianza = 0.90                                          │  │
│  │  Latencia: ~12 ms                                                  │  │
│  │                                                                     │  │
│  │  Interpretación:                                                   │  │
│  │  ✓ confianza >= 0.7 → ALTA CONFIANZA                              │  │
│  │    → Proceder con flujo normal                                     │  │
│  │  ✗ confianza < 0.7 → BAJA CONFIANZA                               │  │
│  │    → Advertir al usuario sobre incertidumbre                       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                        │
│                                  │ confianza_fuzzy                       │
│                                  ▼                                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                  CAPA DE VALIDACIÓN DE DOMINIO                            │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 1: Validación con DOMAIN_KEYWORDS                         │  │
│  │                                                                     │  │
│  │  keywords = {"tarjeta", "rechazar", "hacer"}                       │  │
│  │                                                                     │  │
│  │  DOMAIN_KEYWORDS = {                                               │  │
│  │    "pago", "pagos", "pagar", "acreditar", "tarjeta",              │  │
│  │    "debito", "credito", "comision", "rechazo", "rechazar",        │  │
│  │    "servicio", "prestador", "evento", "transferencia", ...        │  │
│  │  } # 35 términos                                                   │  │
│  │                                                                     │  │
│  │  domain_match = keywords ∩ DOMAIN_KEYWORDS                         │  │
│  │               = {"tarjeta", "rechazar"}                            │  │
│  │               ≠ ∅ ✓                                                │  │
│  │                                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  DECISIÓN:                                                    │ │  │
│  │  │                                                                │ │  │
│  │  │  ✓ domain_match ≠ ∅ → Continuar flujo (consultar Neo4j)      │ │  │
│  │  │  ✗ domain_match = ∅ → Fallback sin consultar Neo4j/LLM       │ │  │
│  │  │                        "Lo siento, no puedo ayudar..."        │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                        │
│                                  │ [Match ✓]                             │
│                                  ▼                                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│              CAPA DE CONOCIMIENTO (RED SEMÁNTICA)                         │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 4: Base de Grafos (Neo4j)                                 │  │
│  │  MÓDULO 2: Red Semántica (Modelo Conceptual)                      │  │
│  │                                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  A. Generación de Query Cypher                                │ │  │
│  │  │     cypher_query(keywords, tipo_usuario)                      │ │  │
│  │  │                                                                │ │  │
│  │  │     Input:                                                     │ │  │
│  │  │       keywords = ["tarjeta", "rechazar", "hacer"]             │ │  │
│  │  │       tipo_usuario = "Organizador"                            │ │  │
│  │  │                                                                │ │  │
│  │  │     Query Cypher generada:                                    │ │  │
│  │  │     ```
│  │  │     WITH ["tarjeta", "rechazar", "hacer"] AS kws              │ │  │
│  │  │     UNWIND kws AS kw                                          │ │  │
│  │  │     MATCH (k:PalabraClave)                                    │ │  │
│  │  │     WHERE toLower(k.nombre) = kw                              │ │  │
│  │  │     MATCH (k)-[:DISPARA]->(c:CategoriaProblema)               │ │  │
│  │  │     OPTIONAL MATCH                                            │ │  │
│  │  │       (c)-[:AGRUPA]->(t:TipoProblema)                         │ │  │
│  │  │       -[:RESUELTO_POR]->(s:Solucion)                          │ │  │
│  │  │     OPTIONAL MATCH                                            │ │  │
│  │  │       (c)-[:TIENE_UN]->(tu:TipoUsuario                        │ │  │
│  │  │         {nombre: "Organizador"})                              │ │  │
│  │  │     WITH c,t,s,tu,                                            │ │  │
│  │  │       collect(DISTINCT k.nombre) AS matched_keywords,         │ │  │
│  │  │       size(...) AS matched_count,                             │ │  │
│  │  │       coalesce(c.confianzaDecision,0) AS confianza,           │ │  │
│  │  │       CASE WHEN tu IS NULL THEN 0 ELSE 1 END AS has_type      │ │  │
│  │  │     RETURN DISTINCT                                           │ │  │
│  │  │       t.nombre AS tipo_problema,                              │ │  │
│  │  │       s.accion AS solucion,                                   │ │  │
│  │  │       confianza, matched_count, matched_keywords, has_type    │ │  │
│  │  │     ORDER BY has_type DESC, matched_count DESC,               │ │  │
│  │  │              confianza DESC                                   │ │  │
│  │  │     # NO HAY LIMIT 1 - Retorna todos los resultados          │ │  │
│  │  │     ```                                                       │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                  │                                 │  │
│  │  ┌──────────────────────────────▼───────────────────────────────┐ │  │
│  │  │  B. Ejecución en Neo4j (Remoto/Local con Fallback)          │ │  │
│  │  │                                                                │ │  │
│  │  │  Estrategia de conexión (neo4j_connection.py):               │ │  │
│  │  │    1. Intento remoto (Neo4j Aura Cloud)                      │ │  │
│  │  │       ├─ ÉXITO → Usar remoto (latencia: 2.5 seg)             │ │  │
│  │  │       └─ FALLO → Intento 2                                   │ │  │
│  │  │    2. Intento local (bolt://localhost:7687)                  │ │  │
│  │  │       ├─ ÉXITO → Usar local (latencia: 120 ms)               │ │  │
│  │  │       └─ FALLO → Exception crítica                           │ │  │
│  │  │                                                                │ │  │
│  │  │  graph.query(cypher) → Ejecuta consulta                      │ │  │
│  │  │  Latencia: 2501 ms (remoto) / 120 ms (local)                 │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                  │                                 │  │
│  │  ┌──────────────────────────────▼───────────────────────────────┐ │  │
│  │  │  C. Resultados Obtenidos (Múltiples candidatos)              │ │  │
│  │  │                                                                │ │  │
│  │  │  result = [                                                   │ │  │
│  │  │    {                                                          │ │  │
│  │  │      "tipo_problema": "Tarjeta rechazada",                   │ │  │
│  │  │      "solucion": "Verifique los datos de su tarjeta...",     │ │  │
│  │  │      "confianza": 0.9,                                        │ │  │
│  │  │      "matched_count": 2,                                      │ │  │
│  │  │      "matched_keywords": ["tarjeta", "rechazar"],            │ │  │
│  │  │      "has_type": 1                                            │ │  │
│  │  │    },                                                         │ │  │
│  │  │    {                                                          │ │  │
│  │  │      "tipo_problema": "Problema con tarjeta de crédito",     │ │  │
│  │  │      "solucion": "Contacte a su banco emisor...",            │ │  │
│  │  │      "confianza": 0.85,                                       │ │  │
│  │  │      "matched_count": 2,                                      │ │  │
│  │  │      "matched_keywords": ["tarjeta", "rechazar"],            │ │  │
│  │  │      "has_type": 1                                            │ │  │
│  │  │    },                                                         │ │  │
│  │  │    # ... más resultados ordenados ...                        │ │  │
│  │  │  ]                                                            │ │  │
│  │  │                                                                │ │  │
│  │  │  SIN LIMIT 1 → El LLM seleccionará el mejor resultado        │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                     │  │
│  │  Estructura del Grafo (72 nodos, 98 relaciones):                  │  │
│  │                                                                     │  │
│  │    (PalabraClave:tarjeta) ─[:DISPARA]→                            │  │
│  │    (PalabraClave:rechazar)─[:DISPARA]→                            │  │
│  │         (CategoriaProblema:Problema_Pago)                          │  │
│  │                │                     │                             │  │
│  │         [:AGRUPA]             [:TIENE_UN]                          │  │
│  │                │                     │                             │  │
│  │                ▼                     ▼                             │  │
│  │    (TipoProblema:Tarjeta rechazada) (TipoUsuario:Organizador)     │  │
│  │                │                                                    │  │
│  │       [:RESUELTO_POR]                                              │  │
│  │                │                                                    │  │
│  │                ▼                                                    │  │
│  │    (Solucion:Verifique los datos...)                               │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                        │
│                                  │ Múltiples resultados                  │
│                                  ▼                                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    CAPA GENERATIVA (LLM)                                  │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 8: Integración Generativa (Ollama + LangChain)            │  │
│  │                                                                     │  │
│  │  *** FUNCIÓN DOBLE DEL MÓDULO 8 ***                               │  │
│  │                                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  FUNCIÓN 1: Selección de Mejor Solución con LLM              │ │  │
│  │  │  elegir_mejor_solucion_con_llm(...)                          │ │  │
│  │  │                                                                │ │  │
│  │  │  Input:                                                        │ │  │
│  │  │    - user_message: "Mi tarjeta fue rechazada..."             │ │  │
│  │  │    - all_results: [resultado1, resultado2, ...]              │ │  │
│  │  │    - categoria_ml: "RechazoTarjeta"                           │ │  │
│  │  │    - emocion: "enojo"                                         │ │  │
│  │  │                                                                │ │  │
│  │  │  Proceso:                                                      │ │  │
│  │  │    1. Formatear candidatos como texto:                        │ │  │
│  │  │       "Opción 1: Tipo=..., Solución=..., Confianza=..."      │ │  │
│  │  │       "Opción 2: Tipo=..., Solución=..., Confianza=..."      │ │  │
│  │  │                                                                │ │  │
│  │  │    2. Construir prompt de selección:                          │ │  │
│  │  │       "Como capa intermedia de decisión, debes elegir         │ │  │
│  │  │        la mejor solución de las ofrecidas.                      │ │  │
│  │  │        Mensaje usuario: {user_message}                         │ │  │
│  │  │        Categoría ML: {categoria_ml}                            │ │  │
│  │  │        Emoción: {emocion}                                      │ │  │
│  │  │        Opciones: {candidates_text}                             │ │  │
│  │  │        Responde con 'Opción X' y justificación breve."        │ │  │
│  │  │                                                                │ │  │
│  │  │    3. Invocar LLM:                                            │ │  │
│  │  │       respuesta = llm.invoke(selection_prompt)                │ │  │
│  │  │       Latencia: ~700-1200 ms                                  │ │  │
│  │  │                                                                │ │  │
│  │  │    4. Parsear respuesta con regex:                            │ │  │
│  │  │       match = re.search(r"Opción (\d+)", respuesta)           │ │  │
│  │  │       idx = int(match.group(1)) - 1                           │ │  │
│  │  │       elegido = all_results[idx]                              │ │  │
│  │  │                                                                │ │  │
│  │  │  Output:                                                       │ │  │
│  │  │    tipo_problema_llm = "Tarjeta rechazada"                    │ │  │
│  │  │    solucion_llm = "Verifique los datos de su tarjeta..."     │ │  │
│  │  │    justificacion_llm = "Opción 1 es la más relevante..."     │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                  │                                 │  │
│  │                                  │ Solución seleccionada           │  │
│  │                                  ▼                                 │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  FUNCIÓN 2: Generación de Respuesta Final                    │ │  │
│  │  │  llm.invoke(prompt_final)                                     │ │  │
│  │  │                                                                │ │  │
│  │  │  A. Obtener detalles de personalización:                     │ │  │
│  │  │                                                                │ │  │
│  │  │     role_details[tipo_usuario]:                               │ │  │
│  │  │       - Organizador:                                          │ │  │
│  │  │           saludo: "Hola estimado organizador!"                │ │  │
│  │  │           tono: "empático y resolutivo"                       │ │  │
│  │  │           extra: "Recuerda que puedes gestionar..."           │ │  │
│  │  │       - Prestador:                                            │ │  │
│  │  │           saludo: "Hola prestador,"                           │ │  │
│  │  │           tono: "apoyo operativo y resolutivo"                │ │  │
│  │  │           extra: "No olvides mantener tu perfil..."           │ │  │
│  │  │       - Propietario:                                          │ │  │
│  │  │           saludo: "Hola propietario,"                         │ │  │
│  │  │           tono: "informativo y estratégico"                   │ │  │
│  │  │           extra: "No olvides mantener..."                     │ │  │
│  │  │                                                                │ │  │
│  │  │  B. Mapear emoción a tono:                                    │ │  │
│  │  │                                                                │ │  │
│  │  │     EMOTION_TO_TONE[emocion]:                                 │ │  │
│  │  │       - enojo → "serio, conciliador y orientado a soluciones"│ │  │
│  │  │       - alegría → "positivo, amable y orientado a soluciones"│ │  │
│  │  │       - tristeza → "consolador, empático y paciente"         │ │  │
│  │  │       - miedo → "tranquilizador, empático y claro"           │ │  │
│  │  │       - asco → "profesional y directo"                        │ │  │
│  │  │       - sorpresa → "informativo y claro"                      │ │  │
│  │  │                                                                │ │  │
│  │  │  C. Determinar post-data según confianza:                     │ │  │
│  │  │                                                                │ │  │
│  │  │     if confianza_fuzzy >= 0.7:                                │ │  │
│  │  │       postdata = "✅ Respuesta recomendada por nuestro       │ │  │
│  │  │                   sistema."                                   │ │  │
│  │  │     else:                                                      │ │  │
│  │  │       postdata = "⚠️ Respuesta con baja confianza,           │ │  │
│  │  │                   verificar manualmente."                     │ │  │
│  │  │                                                                │ │  │
│  │  │  D. Construir prompt contextualizado:                         │ │  │
│  │  │                                                                │ │  │
│  │  │     prompt_llm = f"""                                         │ │  │
│  │  │     Como asistente del sistema Wevently para la               │ │  │
│  │  │     organización de eventos privados donde organizadores,     │ │  │
│  │  │     prestadores de servicios y propietarios de lugar operan,  │ │  │
│  │  │     contesta a la pregunta del usuario.                       │ │  │
│  │  │                                                                │ │  │
│  │  │     {rd['saludo']}                                            │ │  │
│  │  │     Se detectó el problema: {tipo_problema_llm}.              │ │  │
│  │  │     Solución sugerida: {solucion_llm}                         │ │  │
│  │  │     {justificacion_llm}.                                      │ │  │
│  │  │                                                                │ │  │
│  │  │     Por favor responde en un tono {emotion_tone}.             │ │  │
│  │  │                                                                │ │  │
│  │  │     Categor

ía ML: {categoria_ml},                          │ │  │
│  │  │     Emoción detectada: {emocion}, score: {emo_score:.2f},    │ │  │
│  │  │     confianza ML: {confianza_ml:.2f},                         │ │  │
│  │  │     confianza fuzzy: {confianza_fuzzy:.2f}.                   │ │  │
│  │  │                                                                │ │  │
│  │  │     Mensaje original: {pregunta}                              │ │  │
│  │  │                                                                │ │  │
│  │  │     {rd['extra']}                                             │ │  │
│  │  │     {postdata}                                                │ │  │
│  │  │     """                                                       │ │  │
│  │  │                                                                │ │  │
│  │  │  E. Invocar LLM para generar respuesta:                       │ │  │
│  │  │                                                                │ │  │
│  │  │     respuesta = llm.invoke(prompt_llm)                        │ │  │
│  │  │     Latencia: ~4000-5500 ms (53% del flujo total)            │ │  │
│  │  │                                                                │ │  │
│  │  │  F. Respuesta generada:                                       │ │  │
│  │  │                                                                │ │  │
│  │  │     "Hola estimado organizador! Entiendo perfectamente tu     │ │  │
│  │  │      frustración cuando una tarjeta es rechazada durante el   │ │  │
│  │  │      pago. Trabajemos juntos para resolver esto:              │ │  │
│  │  │                                                                │ │  │
│  │  │      Pasos inmediatos:                                        │ │  │
│  │  │      1. Verifica los datos ingresados:                        │ │  │
│  │  │         - Número de tarjeta completo                          │ │  │
│  │  │         - Fecha de vencimiento (MM/AA)                        │ │  │
│  │  │         - Código CVV (3 dígitos al reverso)                   │ │  │
│  │  │         - Nombre tal como aparece en la tarjeta               │ │  │
│  │  │                                                                │ │  │
│  │  │      2. Confirma con tu banco:                                │ │  │
│  │  │         - Saldo disponible suficiente                         │ │  │
│  │  │         - Sin bloqueos por seguridad                          │ │  │
│  │  │         - Límite de compra no excedido                        │ │  │
│  │  │                                                                │ │  │
│  │  │      3. Prueba alternativas:                                  │ │  │
│  │  │         - Otra tarjeta de débito/crédito                      │ │  │
│  │  │         - Diferentes navegadores o dispositivos               │ │  │
│  │  │                                                                │ │  │
│  │  │      Si el problema persiste:                                 │ │  │
│  │  │      Contacta a nuestro equipo de soporte en                  │ │  │
│  │  │      wevently.empresa@gmail.com con:                          │ │  │
│  │  │        - ID del evento                                        │ │  │
│  │  │        - Últimos 4 dígitos de la tarjeta                      │ │  │
│  │  │        - Captura del mensaje de error                         │ │  │
│  │  │                                                                │ │  │
│  │  │      Responderemos en menos de 24 horas hábiles.              │ │  │
│  │  │                                                                │ │  │
│  │  │      Recuerda que puedes gestionar tus eventos desde la       │ │  │
│  │  │      sección 'mis eventos'. Cualquier duda no dudes en        │ │  │
│  │  │      consultarme.                                             │ │  │
│  │  │                                                                │ │  │
│  │  │      Estamos aquí para ayudarte!                              │ │  │
│  │  │                                                                │ │  │
│  │  │      ✅ Respuesta recomendada por nuestro sistema."           │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                     │  │
│  │  Modelo LLM utilizado: gpt-oss:20b-cloud (Ollama Cloud)           │  │
│  │  Parámetros: 20B, API REST en https://ollama.com                  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                        │
│                                  │ respuesta_final                       │
│                                  ▼                                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│              CAPA DE PERSISTENCIA Y LOGGING                               │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 1 & 5: Sistema de Observabilidad                          │  │
│  │                                                                     │  │
│  │  A. Logging Estructurado (pruebas_wevently.log):                  │  │
│  │                                                                     │  │
│  │     2025-11-15 22:30:15,338 - main - INFO -                        │  │
│  │       TEST 2025-11-15T22:30:15.338580 Iniciando -                 │  │
│  │       Usuario: Organizador,                                        │  │
│  │       Pregunta: Mi tarjeta fue rechazada...                        │  │
│  │                                                                     │  │
│  │     2025-11-15 22:30:15,419 - main - INFO -                        │  │
│  │       detect_keywords ejecutado en 0.0814s                         │  │
│  │                                                                     │  │
│  │     2025-11-15 22:30:16,500 - main - INFO -                        │  │
│  │       detect_emotion ejecutado en 1.0804s                          │  │
│  │                                                                     │  │
│  │     2025-11-15 22:30:16,512 - main - INFO -                        │  │
│  │       fuzzy_problem_categorization ejecutado en 0.0120s            │  │
│  │                                                                     │  │
│  │     2025-11-15 22:30:19,014 - main - INFO -                        │  │
│  │       Neo4j query ejecutada: 2.5016s, 2 resultados                │  │
│  │                                                                     │  │
│  │     2025-11-15 22:30:23,302 - main - INFO -                        │  │
│  │       LLM respuesta generada: 4.2882s                              │  │
│  │                                                                     │  │
│  │     2025-11-15 22:30:23,303 - main - INFO -                        │  │
│  │       TEST 2025-11-15T22:30:15.338580 Completado                  │  │
│  │                                                                     │  │
│  │  B. Persistencia JSON (resultados_pruebas.json):                  │  │
│  │                                                                     │  │
│  │     {                                                              │  │
│  │       "test_id": "2025-11-15T22:30:15.338580",                    │  │
│  │       "entrada": "Mi tarjeta fue rechazada dos veces...",         │  |
│  │       "tipo_usuario": "Organizador",                              │  │
│  │       "categoria_predicha_ml": "RechazoTarjeta",                  │  │
│  │       "confianza_ml": 0.45,                                        │  │
│  │       "keywords": ["tarjeta", "rechazar", "hacer"],               │  │
│  │       "emocion": "enojo",                                          │  │
│  │       "confianza_fuzzy": 0.90,                                     │  │
│  │       "tipo_problema": "Tarjeta rechazada",                        │  │
│  │       "solucion": "Verifique los datos de su tarjeta...",         │  │
│  │       "matched_keywords": ["tarjeta", "rechazar"],                │  │
│  │       "respuesta": "Hola estimado organizador! Entiendo...",      │  │
│  │       "plan": {                                                    │  │
│  │         "categoria_ml": "RechazoTarjeta",                          │  │
│  │         "confianza_ml": 0.45,                                      │  │
│  │         "keywords": ["tarjeta", "rechazar", "hacer"],             │  │
│  │         "ejecutar_flujo_completo": true,                           │  │
│  │         "justificacion": ["Confianza ML suficiente y keywords     │  │
│  │                            relevantes en dominio."]                │  │
│  │       },                                                           │  │
│  │       "tiempos": {                                                 │  │
│  │         "keywords_ms": 81.39,                                      │  │
│  │         "emocion_ms": 1080.45,                                     │  │
│  │         "fuzzy_ms": 12.01,                                         │  │
│  │         "neo4j_ms": 2501.61,                                       │  │
│  │         "llm_ms": 4288.25,                                         │  │
│  │         "total_ms": 7963.71                                        │  │
│  │       }                                                            │  │
│  │     }                                                              │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                  │                                        │
│                                  │ Métricas guardadas                    │
│                                  ▼                                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                         RETORNO A CAPA DE PRESENTACIÓN                    │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  MÓDULO 9: Renderización en Streamlit                             │  │
│  │                                                                     │  │
│  │  Tupla retornada desde generar_respuesta_streamlit():             │  │
│  │                                                                     │  │
│  │    (respuesta, keywords, emocion, confianza_fuzzy)                 │  │
│  │                                                                     │  │
│  │  Procesamiento en streamlit_app.py:                               │  │
│  │                                                                     │  │
│  │    1. Agregar a historial de chat:                                │  │
│  │       st.session_state.chat_history.append({                       │  │
│  │         "usuario": "Organizador",                                  │  │
│  │         "mensaje": "Mi tarjeta fue rechazada...",                 │  │
│  │         "respuesta": "Hola estimado organizador!...",             │  │
│  │         "keywords": ["tarjeta", "rechazar", "hacer"],             │  │
│  │         "emocion": "enojo",                                        │  │
│  │         "confianza": 0.90,                                         │  │
│  │         "hora": "22:30"                                            │  │
│  │       })                                                           │  │
│  │                                                                     │  │
│  │    2. Persistir en localStorage (simulado):                       │  │
│  │       save_chat_to_local_storage(chat_history)                    │  │
│  │       TTL: 30 minutos                                              │  │
│  │                                                                     │  │
│  │    3. Renderizar burbujas de chat:                                │  │
│  │                                                                     │  │
│  │       ┌────────────────────────────────────────────────────────┐  │  │
│  │       │  Chat Container (500px height, scroll)                 │  │
│  │       │                                                         │  │
│  │       │  ┌──────────────────────────────────────┐ 22:30       │  │
│  │       │  │ Mi tarjeta fue rechazada dos veces   │ Organizador │  │
│  │       │  │ ¿qué hago?                           │             │  │
│  │       │  └──────────────────────────────────────┘             │  │
│  │       │                                                         │  │
│  │       │  22:30 Asistente                                       │  │
│  │       │  ┌──────────────────────────────────────┐             │  │
│  │       │  │ Hola estimado organizador!           │             │  │
│  │       │  │ Entiendo perfectamente tu            │             │  │
│  │       │  │ frustración cuando una tarjeta       │             │  │
│  │       │  │ es rechazada durante el pago...      │             │  │
│  │       │  │                                       │             │  │
│  │       │  │ [Pasos detallados...]                │             │  │
│  │       │  │                                       │             │  │
│  │       │  │ KW: tarjeta, rechazar, hacer         │             │  │
│  │       │  │ Emoción: enojo                       │             │  │
│  │       │  │ Confianza: 0.90                      │             │  │
│  │       │  └──────────────────────────────────────┘             │  │
│  │       └────────────────────────────────────────────────────────┘  │  │
│  │                                                                     │  │
│  │    4. Ejecutar st.rerun() para refrescar UI                        │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```


***

## **3. Diagrama Simplificado de Flujo de Datos**

```
USUARIO (Navegador)
       │
       │ "Mi tarjeta fue rechazada dos veces"
       ▼
┌─────────────────┐
│   MÓDULO 9      │  Streamlit UI
│   Interface     │  - Captura mensaje
│   Web           │  - Selector de rol
└────────┬────────┘
         │
         │ generar_respuesta_streamlit(pregunta, tipo_usuario)
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MÓDULO 1: ORQUESTADOR                         │
│                  (Coordinador Central)                           │
│                                                                  │
│  Test ID: 2025-11-15T22:30:15.338580                           │
│  Logger: INFO - Iniciando flujo...                              │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├──────────────────────────────────────────────────────┐
         │                                                       │
         ▼                                                       │
┌─────────────────┐                                             │
│   MÓDULO 5      │  Planificador Dinámico                      │
│   Decisión      │                                             │
│   Inteligente   │  ┌──> MÓDULO 6: Clasificación ML           │
│                 │  │    (RandomForest, ~15ms)                 │
│                 │  │    → categoria: "RechazoTarjeta"         │
│                 │  │    → confianza: 0.45                     │
│                 │  │                                           │
│                 │  ├──> Extracción keywords (spaCy)           │
│                 │  │    → ["tarjeta", "rechazar", "hacer"]    │
│                 │  │                                           │
│                 │  └──> DECISIÓN:                             │
│                 │       ✓ Categoría válida                    │
│                 │       ✓ Confianza >= 0.10                   │
│                 │       ✓ Keywords ∩ DOMAIN_KEYWORDS ≠ ∅     │
│                 │       → ejecutar_flujo_completo = True      │
└────────┬────────┘                                             │
         │                                                       │
         │ [Flujo completo aprobado]                            │
         │                                                       │
         ├───────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MÓDULO 7: NLP PIPELINE                        │
│                  (Procesamiento Lingüístico)                     │
│                                                                  │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │  spaCy             │         │  BETO Transformer  │         │
│  │  (es_core_news_md) │         │  (6 emociones)     │         │
│  │  ~81 ms            │         │  ~1080 ms          │         │
│  │                    │         │                    │         │
│  │  Output:           │         │  Output:           │         │
│  │  keywords =        │         │  emocion = "enojo" │         │
│  │  ["tarjeta",       │         │  score = 0.87      │         │
│  │   "rechazar",      │         │                    │         │
│  │   "hacer"]         │         │                    │         │
│  └────────────────────┘         └────────────────────┘         │
└────────┬────────────────────────────────┬────────────────────────┘
         │                                │
         │                                │
         ▼                                ▼
┌─────────────────┐              ┌──────────────────┐
│   MÓDULO 3      │              │   MÓDULO 1       │
│   Lógica Difusa │              │   Validación     │
│   ~12 ms        │              │   Dominio        │
│                 │              │                  │
│  Input:         │              │  keywords ∩      │
│  len(keywords)  │              │  DOMAIN_KEYWORDS │
│  = 3            │              │  = {"tarjeta",   │
│                 │              │     "rechazar"}  │
│  Sistema        │              │  ≠ ∅ ✓          │
│  Mamdani:       │              │                  │
│  - bajo(3)=0.0  │              │  → Continuar     │
│  - medio(3)=0.67│              │                  │
│  - alto(3)=0.67 │              │                  │
│                 │              │                  │
│  Output:        │              │                  │
│  confianza=0.90 │              │                  │
└────────┬────────┘              └────────┬─────────┘
         │                                │
         │                                │ [Match ✓]
         └────────────────┬───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              MÓDULO 4: NEO4J + MÓDULO 2: RED SEMÁNTICA           │
│                    (Base de Conocimiento)                        │
│                                                                  │
│  Conexión: Remoto (Aura) con fallback a Local                   │
│  Latencia: 2501 ms (remoto) / 120 ms (local)                    │
│                                                                  │
│  Query Cypher:                                                   │
│    WITH ["tarjeta", "rechazar", "hacer"] AS kws                 │
│    UNWIND kws AS kw                                              │
│    MATCH (k:PalabraClave) WHERE toLower(k.nombre) = kw          │
│    MATCH (k)-[:DISPARA]->(c:CategoriaProblema)                  │
│    OPTIONAL MATCH (c)-[:AGRUPA]->(t:TipoProblema)               │
│                       -[:RESUELTO_POR]->(s:Solucion)            │
│    OPTIONAL MATCH (c)-[:TIENE_UN]->(tu:TipoUsuario              │
│                       {nombre:"Organizador"})                    │
│    ...                                                           │
│    ORDER BY has_type DESC, matched_count DESC, confianza DESC    │
│    # SIN LIMIT 1 - Retorna todos los resultados                 │
│                                                                  │
│  Resultados (múltiples candidatos):                             │
│    [                                                             │
│      {tipo_problema: "Tarjeta rechazada",                       │
│       solucion: "Verifique los datos...", confianza: 0.9, ...}, │
│      {tipo_problema: "Problema tarjeta crédito",                │
│       solucion: "Contacte a su banco...", confianza: 0.85, ...},│
│      ...                                                         │
│    ]                                                             │
└────────┬────────────────────────────────────────────────────────┘
         │
         │ Múltiples soluciones candidatas
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              MÓDULO 8: GENERACIÓN LLM (Ollama Cloud)             │
│                   *** DOBLE FUNCIÓN ***                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FUNCIÓN 1: Selección de Mejor Solución                  │   │
│  │  elegir_mejor_solucion_con_llm(...)                      │   │
│  │  ~700-1200 ms                                             │   │
│  │                                                            │   │
│  │  LLM evalúa múltiples candidatos considerando:           │   │
│  │    - Mensaje original del usuario                         │   │
│  │    - Categoría ML predicha                                │   │
│  │  FUNCIÓN 1: Selección de Mejor Solución                  │   │
│  │  elegir_mejor_solucion_con_llm(...)                      │   │
│  │  ~700-1200 ms                                             │   │
│  │                                                            │   │
│  │  Entrada:                                                 │   │
│  │    - user_message: "Mi tarjeta fue rechazada..."         │   │
│  │    - all_results: [candidato1, candidato2, ...]          │   │
│  │    - categoria_ml: "RechazoTarjeta"                       │   │
│  │    - emocion: "enojo"                                     │   │
│  │    - llm: OllamaLLM (gpt-oss:20b-cloud)                  │   │
│  │                                                            │   │
│  │  Proceso:                                                 │   │
│  │    1. Formatear candidatos:                               │   │
│  │       candidates_text = "Opción 1: Tipo=Tarjeta          │   │
│  │       rechazada, Solución=Verifique datos...,             │   │
│  │       Confianza=0.90, Keywords=[tarjeta, rechazar]"      │   │
│  │                                                            │   │
│  │    2. Construir prompt de selección:                      │   │
│  │       selection_prompt = f"""                             │   │
│  │       Como capa intermedia de un proceso de decisión      │   │
│  │       para ofrecer la mejor solución al problema/         │   │
│  │       consulta del usuario, debes elegir cual es la       │   │
│  │       mejor solución de las ofrecidas.                    │   │
│  │       No modifiques la solución ni el tipo de problema.   │   │
│  │                                                            │   │
│  │       Mensaje del usuario: '{user_message}'              │   │
│  │       Categoría ML: {categoria_ml}                        │   │
│  │       Emoción detectada: {emocion}                        │   │
│  │                                                            │   │
│  │       Soluciones candidatas:                              │   │
│  │       {candidates_text}                                   │   │
│  │                                                            │   │
│  │       Evalúa todas las opciones y elige la más            │   │
│  │       relevante para el mensaje y emoción del usuario.    │   │
│  │       Elige SOLO la opción más relevante.                 │   │
│  │       Responde exactamente con 'Opción X:' seguido        │   │
│  │       de una justificación breve.                         │   │
│  │       Si varias opciones son similares, desempata por     │   │
│  │       cantidad de keywords y confianza.                   │   │
│  │       """                                                 │   │
│  │                                                            │   │
│  │    3. Invocar LLM:                                        │   │
│  │       respuesta = llm.invoke(selection_prompt)            │   │
│  │       Ejemplo: "Opción 1 es la más relevante porque      │   │
│  │                 coincide exactamente con el problema      │   │
│  │                 del usuario y tiene la confianza más      │   │
│  │                 alta (0.90). Los pasos son claros y       │   │
│  │                 accionables."                             │   │
│  │                                                            │   │
│  │    4. Parsear respuesta con regex:                        │   │
│  │       import re                                           │   │
│  │       match = re.search(r"Opción\s*(\d+)", respuesta)     │   │
│  │       if not match:                                       │   │
│  │         → return (None, None, None,                       │   │
│  │           "No se pudo determinar opción de LLM...")       │   │
│  │       idx = int(match.group(1)) - 1  # Convertir a 0-idx │   │
│  │       if idx < 0 or idx >= len(all_results):             │   │
│  │         → return (None, None, None,                       │   │
│  │           "Índice elegido fuera de rango...")             │   │
│  │                                                            │   │
│  │    5. Extraer solución elegida:                           │   │
│  │       elegido = all_results[idx]                          │   │
│  │       tipo_problema_llm = elegido.get('tipo_problema')    │   │
│  │       solucion_llm = elegido.get('solucion')              │   │
│  │       justificacion_llm = respuesta                       │   │
│  │                                                            │   │
│  │  Salida:                                                  │   │
│  │    (tipo_problema_llm, solucion_llm, elegido,             │   │
│  │     justificacion_llm)                                    │   │
│  │                                                            │   │
│  │  Casos de error (fallback):                               │   │
│  │    - all_results vacío:                                   │   │
│  │      → (None, None, None,                                 │   │
│  │         "No hay soluciones candidatas...")                │   │
│  │    - Regex no encuentra "Opción X":                       │   │
│  │      → (None, None, None,                                 │   │
│  │         "No se pudo determinar opción de LLM...")         │   │
│  │    - Índice fuera de rango:                               │   │
│  │      → (None, None, None,                                 │   │
│  │         "Índice elegido fuera de rango...")               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FUNCIÓN 2: Generación de Respuesta Final                │   │
│  │  llm.invoke(prompt_final)                                │   │
│  │  ~4000-5500 ms (53% del tiempo total del flujo)          │   │
│  │                                                            │   │
│  │  A. Obtener detalles de personalización por rol:         │   │
│  │                                                            │   │
│  │     rd = role_details.get(tipo_usuario,                  │   │
│  │                           role_details["Prestador"])      │   │
│  │                                                            │   │
│  │     Si tipo_usuario = "Organizador":                      │   │
│  │       rd = {                                              │   │
│  │         "saludo": "¡Hola estimado organizador! ",        │   │
│  │         "tono": "empático y resolutivo",                 │   │
│  │         "extra": "Recuerda que puedes gestionar tus      │   │
│  │                   eventos desde la sección mis eventos.   │   │
│  │                   Cualquier duda no dudes en consultarme."│   │
│  │       }                                                   │   │
│  │                                                            │   │
│  │     Si tipo_usuario = "Prestador":                        │   │
│  │       rd = {                                              │   │
│  │         "saludo": "Hola prestador, ",                    │   │
│  │         "tono": "enfocado en apoyo operativo y resolutivo│   │
│  │         "extra": "No olvides mantener tu perfil y        │   │
│  │                   disponibilidad actualizados para evitar │   │
│  │                   inconvenientes."                        │   │
│  │       }                                                   │   │
│  │                                                            │   │
│  │     Si tipo_usuario = "Propietario":                      │   │
│  │       rd = {                                              │   │
│  │         "saludo": "Hola propietario, ",                  │   │
│  │         "tono": "informativo, estratégico y resolutivo", │   │
│  │         "extra": "No olvides mantener tu perfil y        │   │
│  │                   disponibilidad actualizados para evitar │   │
│  │                   inconvenientes."                        │   │
│  │       }                                                   │   │
│  │                                                            │   │
│  │  B. Mapear emoción detectada a tono de respuesta:        │   │
│  │                                                            │   │
│  │     emotion_tone = EMOTION_TO_TONE.get(emocion,          │   │
│  │                                        rd.get('tono'))    │   │
│  │                                                            │   │
│  │     EMOTION_TO_TONE = {                                  │   │
│  │       "alegría": "positivo, amable y orientado a         │   │
│  │                   soluciones",                            │   │
│  │       "enojo": "serio, conciliador y orientado a         │   │
│  │               soluciones",                                │   │
│  │       "asco": "profesional y directo",                   │   │
│  │       "miedo": "tranquilizador, empático y claro",       │   │
│  │       "tristeza": "consolador, empático y paciente",     │   │
│  │       "sorpresa": "informativo y claro"                  │   │
│  │     }                                                     │   │
│  │                                                            │   │
│  │     Si emocion = "enojo":                                 │   │
│  │       emotion_tone = "serio, conciliador y orientado a   │   │
│  │                       soluciones"                         │   │
│  │                                                            │   │
│  │  C. Determinar post-data según nivel de confianza:       │   │
│  │                                                            │   │
│  │     if confianza_fuzzy >= 0.7:                            │   │
│  │       postdata = "✅ Respuesta recomendada por nuestro   │   │
│  │                   sistema."                               │   │
│  │     else:                                                 │   │
│  │       postdata = "⚠️ Respuesta tomada de la base de       │   │
│  │                   conocimiento (confianza baja,           │   │
│  │                   verificar manualmente)."                │   │
│  │                                                            │   │
│  │  D. Construir prompt contextualizado final:              │   │
│  │                                                            │   │
│  │     prompt_llm = f"""                                     │   │
│  │     Como asistente del sistema Wevently para la           │   │
│  │     organización de eventos privados donde organizadores, │   │
│  │     prestadores de servicios y propietarios de lugar      │   │
│  │     operan, contesta a la pregunta del usuario.           │   │
│  │                                                            │   │
│  │     {rd['saludo']}                                        │   │
│  │     Se detectó el problema: {tipo_problema_llm}.          │   │
│  │     Solución sugerida: {solucion_llm}                     │   │
│  │     {justificacion_llm}.                                  │   │
│  │                                                            │   │
│  │     Por favor responde en un tono {emotion_tone}.         │   │
│  │                                                            │   │
│  │     (Categoría ML: {categoria_ml},                        │   │
│  │      Emoción detectada: {emocion},                        │   │
│  │      score emoción: {emo_score:.2f},                      │   │
│  │      confianza ML: {confianza_ml:.2f},                    │   │
│  │      confianza fuzzy: {confianza_fuzzy:.2f}).             │   │
│  │                                                            │   │
│  │     Mensaje original: {pregunta}                          │   │
│  │                                                            │   │
│  │     {rd['extra']}                                         │   │
│  │     {postdata}                                            │   │
│  │     """                                                   │   │
│  │                                                            │   │
│  │  E. Invocar LLM para generar respuesta final:            │   │
│  │                                                            │   │
│  │     inicio_llm = time.time()                              │   │
│  │     respuesta = llm.invoke(prompt_llm)                    │   │
│  │     llm_time = time.time() - inicio_llm                   │   │
│  │     Latencia: ~4000-5500 ms                               │   │
│  │                                                            │   │
│  │  F. Respuesta generada (ejemplo completo):               │   │
│  │                                                            │   │
│  │     "Hola estimado organizador! Entiendo perfectamente    │   │
│  │      tu frustración cuando una tarjeta es rechazada       │   │
│  │      durante el pago. Trabajemos juntos para resolver     │   │
│  │      esto:                                                 │   │
│  │                                                            │   │
│  │      **Pasos inmediatos:**                                │   │
│  │                                                            │   │
│  │      1. **Verifica los datos ingresados:**                │   │
│  │         - Número de tarjeta completo (sin espacios)       │   │
│  │         - Fecha de vencimiento (MM/AA)                    │   │
│  │         - Código CVV (3 dígitos al reverso)               │   │
│  │         - Nombre tal como aparece en la tarjeta           │   │
│  │         - Dirección de facturación coincida               │   │
│  │                                                            │   │
│  │      2. **Confirma con tu banco:**                        │   │
│  │         - Saldo disponible suficiente                     │   │
│  │         - Sin bloqueos por seguridad (fraude)             │   │
│  │         - Límite de compra no excedido                    │   │
│  │         - Tarjeta no vencida                              │   │
│  │         - Contacta al banco si hay dudas                  │   │
│  │                                                            │   │
│  │      3. **Prueba alternativas:**                          │   │
│  │         - Otra tarjeta de débito/crédito                  │   │
│  │         - Diferentes navegadores (Chrome, Firefox, etc.)  │   │
│  │         - Dispositivos diferentes (móvil vs escritorio)   │   │
│  │         - Desactiva extensiones bloqueadoras              │   │
│  │                                                            │   │
│  │      **Si el problema persiste:**                         │   │
│  │      Contacta a nuestro equipo de soporte en              │   │
│  │      wevently.empresa@gmail.com con:                      │   │
│  │        - ID del evento                                    │   │
│  │        - Últimos 4 dígitos de la tarjeta                  │   │
│  │        - Captura de pantalla del mensaje de error         │   │
│  │        - Navegador y sistema operativo                    │   │
│  │        - Hora exacta del intento                          │   │
│  │                                                            │   │
│  │      Responderemos en menos de 24 horas hábiles.          │   │
│  │                                                            │   │
│  │      Recuerda que puedes gestionar tus eventos desde la   │   │
│  │      sección 'mis eventos'. Cualquier duda no dudes en    │   │
│  │      consultarme.                                         │   │
│  │                                                            │   │
│  │      ¡Estamos aquí para ayudarte!                         │   │
│  │                                                            │   │
│  │      ✅ Respuesta recomendada por nuestro sistema."       │   │
│  │                                                            │   │
│  │  Características de la respuesta generada:                │   │
│  │    ✓ Tono: Serio, conciliador y orientado a soluciones   │   │
│  │      (adaptado a emoción "enojo")                         │   │
│  │    ✓ Estructura: Pasos numerados y claros                │   │
│  │    ✓ Personalización: Saludo específico para Organizador │   │
│  │    ✓ Contexto: Información sobre el evento y gestión      │   │
│  │    ✓ Fallback: Contacto de soporte con detalles          │   │
│  │    ✓ Confianza: Indicador visual (✅) según umbral        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Output final: respuesta (string con formato markdown)           │
└─────────────────────────────────────────────────────────────────┘
         │
         │ respuesta generada
         ▼
┌─────────────────────────────────────────────────────────────────┐
│            CAPA DE PERSISTENCIA Y LOGGING (Actualización)        │
│                                                                  │
│  Construcción del objeto resultado_prueba:                      │
│                                                                  │
│  resultado_prueba = {                                            │
│    "test_id": "2025-11-15T22:30:15.338580",                    │
│    "entrada": "Mi tarjeta fue rechazada dos veces...",         │
│    "tipo_usuario": "Organizador",                              │
│    "categoria_predicha_ml": "RechazoTarjeta",                  │
│    "confianza_ml": 0.45,                                        │
│    "keywords": ["tarjeta", "rechazar", "hacer"],               │
│    "emocion": "enojo",                                          │
│    "confianza_fuzzy": 0.90,                                     │
│    "tipo_problema": "Tarjeta rechazada",                        │
│    "solucion": "Verifique los datos de su tarjeta...",         │
│    "matched_keywords": ["tarjeta", "rechazar"],                │
│    "respuesta": "Hola estimado organizador! Entiendo...",      │
│    "plan": {                                                    │
│      "categoria_ml": "RechazoTarjeta",                          │
│      "confianza_ml": 0.45,                                      │
│      "keywords": ["tarjeta", "rechazar", "hacer"],             │
│      "ejecutar_flujo_completo": true,                           │
│      "justificacion": [                                         │
│        "Confianza ML suficiente y keywords relevantes en        │
│         dominio. Ejecuto flujo completo."                       │
│      ]                                                          │
│    },                                                           │
│    "tiempos": {                                                 │
│      "keywords_ms": 81.39,                                      │
│      "emocion_ms": 1080.45,                                     │
│      "fuzzy_ms": 12.01,                                         │
│      "neo4j_ms": 2501.61,                                       │
│      "llm_ms": 4288.25,                                         │
│      "total_ms": 7963.71                                        │
│    }                                                            │
│  }                                                              │
│                                                                  │
│  Persistencia:                                                   │
│    with open('resultados_pruebas.json', 'a') as f:             │
│      f.write(json.dumps(resultado_prueba) + '\n')              │
│                                                                  │
│  Logging:                                                        │
│    logger.info(f"[TEST {test_id}] Completado")                 │
│    if debug:                                                    │
│      logger.info(f"[DEBUG] {json.dumps(resultado_prueba)}")     │
└────────┬────────────────────────────────────────────────────────┘
         │
         │ Retorno al orquestador
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RETORNO A CAPA DE PRESENTACIÓN                │
│                                                                  │
│  Tupla retornada desde generar_respuesta_streamlit():           │
│                                                                  │
│  return (respuesta, keywords, emocion, confianza_fuzzy)         │
│                                                                  │
│  Donde:                                                          │
│    respuesta = "Hola estimado organizador!..."                  │
│    keywords = ["tarjeta", "rechazar", "hacer"]                  │
│    emocion = "enojo"                                            │
│    confianza_fuzzy = 0.90                                       │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MÓDULO 9: RENDERIZACIÓN STREAMLIT             │
│                      (Interface Web)                             │
│                                                                  │
│  Procesamiento en streamlit_app.py:                             │
│                                                                  │
│  1. Agregar a historial de chat:                                │
│     st.session_state.chat_history.append({                       │
│       "usuario": "Organizador",                                 │
│       "mensaje": "Mi tarjeta fue rechazada...",                │
│       "respuesta": "Hola estimado organizador!...",            │
│       "keywords": ["tarjeta", "rechazar", "hacer"],            │
│       "emocion": "enojo",                                       │
│       "confianza": 0.90,                                        │
│       "hora": "22:30"                                           │
│     })                                                          │
│                                                                  │
│  2. Persistir en localStorage (simulado):                       │
│     save_chat_to_local_storage(chat_history)                   │
│     TTL: 30 minutos                                             │
│     Formato: Base64 encoded JSON                                │
│                                                                  │
│  3. Renderizar burbujas de chat:                                │
│                                                                  │
│     ┌────────────────────────────────────────────────────────┐  │
│     │  Chat Container (500px height, scroll automático)      │  │
│     │                                                         │  │
│     │  ┌──────────────────────────────────────┐ 22:30       │  │
│     │  │ Mi tarjeta fue rechazada dos veces   │ Organizador │  │
│     │  │ ¿qué hago?                           │             │  │
│     │  └──────────────────────────────────────┘             │  │
│     │  Burbuja alineada a la derecha (usuario)               │  │
│     │  Fondo: color primario (#3498db)                       │  │
│     │  Texto: blanco                                         │  │
│     │                                                         │  │
│     │  22:30 Asistente Wevently                             │  │
│     │  ┌──────────────────────────────────────┐             │  │
│     │  │ Hola estimado organizador!           │             │  │
│     │  │ Entiendo perfectamente tu            │             │  │
│     │  │ frustración cuando una tarjeta       │             │  │
│     │  │ es rechazada durante el pago...      │             │  │
│     │  │                                       │             │  │
│     │  │ **Pasos inmediatos:**                │             │  │
│     │  │ 1. Verifica los datos ingresados:    │             │  │
│     │  │    - Número de tarjeta completo      │             │  │
│     │  │    - Fecha de vencimiento (MM/AA)    │             │  │
│     │  │    - Código CVV (3 dígitos)          │             │  │
│     │  │    - Nombre en la tarjeta            │             │  │
│     │  │                                       │             │  │
│     │  │ 2. Confirma con tu banco:            │             │  │
│     │  │    - Saldo disponible suficiente     │             │  │
│     │  │    - Sin bloqueos por seguridad      │             │  │
│     │  │    - Límite de compra no excedido    │             │  │
│     │  │                                       │             │  │
│     │  │ 3. Prueba alternativas:              │             │  │
│     │  │    - Otra tarjeta de débito/crédito  │             │  │
│     │  │    - Diferentes navegadores          │             │  │
│     │  │    - Dispositivos diferentes         │             │  │
│     │  │                                       │             │  │
│     │  │ Si el problema persiste:             │             │  │
│     │  │ Contacta a wevently.empresa@gmail.com│             │  │
│     │  │                                       │             │  │
│     │  │ ✅ Respuesta recomendada por nuestro │             │  │
│     │  │    sistema.                          │             │  │
│     │  └──────────────────────────────────────┘             │  │
│     │  Burbuja alineada a la izquierda (asistente)           │  │
│     │  Fondo: gris claro (#ecf0f1)                           │  │
│     │  Texto: gris oscuro (#2c3e50)                          │  │
│     │                                                         │  │
│     │  Metadatos (expandibles):                              │  │
│     │  ┌──────────────────────────────────────┐             │  │
│     │  │ 🔍 Detalles de procesamiento         │             │  │
│     │  │ Keywords: tarjeta, rechazar, hacer   │             │  │
│     │  │ Emoción: enojo (87%)                 │             │  │
│     │  │ Confianza: 0.90 (ALTA)               │             │  │
│     │  │ Latencia total: 7.96s                │             │  │
│     │  │   - Keywords: 81ms                   │             │  │
│     │  │   - Emoción: 1080ms                  │             │  │
│     │  │   - Fuzzy: 12ms                      │             │  │
│     │  │   - Neo4j: 2502ms                    │             │  │
│     │  │   - LLM: 4288ms                      │             │  │
│     │  └──────────────────────────────────────┘             │  │
│     └────────────────────────────────────────────────────────┘  │
│                                                                  │
│  4. Input area para nuevo mensaje:                              │
│     ┌────────────────────────────────────────────────────────┐  │
│     │ Escribe tu mensaje aquí...                             │  │
│     │ [Enviar] [Limpiar historial]                           │  │
│     └────────────────────────────────────────────────────────┘  │
│                                                                  │
│  5. Ejecutar st.rerun() para refrescar UI:                      │
│     st.rerun()  # Actualiza la interfaz con nuevo mensaje      │
│                                                                  │
│  6. Selector de rol (sidebar):                                  │
│     ┌────────────────────────────────────────┐                 │
│     │ Selecciona tu rol:                      │                 │
│     │ ○ Organizador                           │                 │
│     │ ● Prestador                             │                 │
│     │ ○ Propietario                           │                 │
│     │                                         │                 │
│     │ [Debug Mode] ☑                          │                 │
│     └────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Ciclo completo
         ▼
    USUARIO VE RESPUESTA EN PANTALLA



┌─────────────────────────────────────────────────────────────────┐
│              PUNTOS DE DECISIÓN Y FALLBACKS                      │
│                                                                  │
│  El sistema implementa múltiples capas de fallback para         │
│  garantizar robustez ante fallos en cualquier módulo.           │
└─────────────────────────────────────────────────────────────────┘

FALLBACK 1: Clasificación ML Fallida
─────────────────────────────────────────────────────────────────

Condición:
  categoria_ml == "NoRepresentaAlDominio" 
  O confianza_ml < ML_CONFIDENCE_THRESHOLD (0.10)

Ubicación: planificar_flujo() → Módulo 5

Acción:
  plan["ejecutar_flujo_completo"] = False
  plan["justificacion"].append(
    f"Categoría ML: NoRepresentaAlDominio o confianza baja 
     {confianza_ml:.2f}. Fallback inmediato."
  )

Resultado:
  respuesta = "Lo siento, no puedo ayudar con ese tipo de 
               consulta."
  
  resultado_prueba guardado con:
    - test_id: UUID único
    - entrada: pregunta original
    - categoria_predicha_ml: "NoRepresentaAlDominio"
    - confianza_ml: < 0.10
    - respuesta: mensaje de fallback
    - plan: justificación completa

Latencia: ~15 ms (solo Módulo 6 ML)

Ejemplo:
  Usuario: "¿Cuál es la capital de Francia?"
  Categoría ML: "NoRepresentaAlDominio"
  Confianza: 0.05
  Respuesta: "Lo siento, no puedo ayudar con ese tipo de consulta."


FALLBACK 2: Sin Keywords de Dominio
─────────────────────────────────────────────────────────────────

Condición:
  keywords ∩ DOMAIN_KEYWORDS = ∅ (conjunto vacío)

Ubicación: planificar_flujo() → Módulo 5
           generar_respuesta_streamlit() → Módulo 1

Acción:
  plan["ejecutar_flujo_completo"] = False
  plan["justificacion"].append(
    "Sin keywords relevantes de dominio. Fallback."
  )

Resultado:
  respuesta = "Lo siento, no puedo ayudar con ese tipo de 
               consulta."
  
  domain_match = [] (vacío)
  No se ejecuta consulta Neo4j
  No se invoca LLM para respuesta final

Latencia: ~93 ms (Módulos 6 + 7 NLP)

Ejemplo:
  Usuario: "¿Cuándo es mi próxima reunión?"
  Keywords: ["próximo", "reunión", "cuando"]
  domain_match: [] (ninguno coincide con DOMAIN_KEYWORDS)
  Respuesta: "Lo siento, no puedo ayudar con ese tipo de consulta."


FALLBACK 3: Sin Resultados en Neo4j
─────────────────────────────────────────────────────────────────

Condición:
  result = [] (lista vacía después de graph.query())
  O matched_count = 0 para todos los resultados

Ubicación: generar_respuesta_streamlit() → Módulo 1

Acción:
  tipo_problema = "No definido"
  solucion = "No definida"
  matched_keys = []
  postdata = "No se encontró solución automática, te derivaremos 
             a soporte. (weventlyempresa@gmail.com)"

Resultado:
  El LLM genera respuesta genérica de fallback:
  
  "Hola [rol]! Lamentablemente no encontramos una solución 
   específica en nuestra base de conocimiento para tu problema.
   
   Sin embargo, te recomendamos:
   1. Contactar a nuestro equipo de soporte
   2. Proporcionar detalles específicos de tu caso
   3. Incluir capturas de pantalla si es relevante
   
   Contacto: weventlyempresa@gmail.com
   Tiempo de respuesta: < 24 horas hábiles"

Latencia: ~2593 ms (Módulos 6 + 7 + 3 + 4 sin resultados + 8)

Ejemplo:
  Usuario: "Mi evento tiene un problema muy específico..."
  Keywords: ["evento", "problema", "específico"]
  Neo4j query: Ejecutada correctamente
  Resultados: [] (vacío)
  Respuesta: Mensaje genérico de derivación a soporte


FALLBACK 4: Error en Conexión Neo4j
─────────────────────────────────────────────────────────────────

Condición:
  graph.query(cypher) lanza excepción
  (remoto no disponible, local no disponible)

Ubicación: generar_respuesta_streamlit() → Módulo 4

Acción:
  except Exception as e:
    logger.error(f"[TEST {test_id}] Error: {str(e)}", 
                 exc_info=True)
    raise  # Propagar excepción

Resultado:
  Excepción capturada en capa superior
  Mensaje de error al usuario
  Log completo guardado en pruebas_wevently.log

Latencia: Variable (timeout de conexión)

Estrategia de conexión (neo4j_connection.py):
  1. Intento remoto (Neo4j Aura Cloud)
     ├─ ÉXITO → Usar remoto
     └─ TIMEOUT/FALLO → Intento 2
  2. Intento local (bolt://localhost:7687)
     ├─ ÉXITO → Usar local
     └─ FALLO → Exception crítica