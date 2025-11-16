### **Módulo 1: Red de Procesos del Sistema Experto**

#### **Propósito**

Define y ejecuta el flujo de decisión y las reglas principales del negocio que determinan cómo el sistema procesa una consulta del usuario, desde la validación de dominio hasta la generación de la respuesta final.

#### **Entradas**

- Consulta en texto plano del usuario
- Tipo de usuario (Organizador, Prestador, Propietario)
- Keywords extraídas (spaCy)
- Emoción detectada (BETO)
- Nivel de confianza (lógica difusa)


#### **Salidas**

- Respuesta generada por el LLM
- Categoría del problema detectado
- Solución propuesta (de Neo4j o mensaje de derivación)
- Metadatos: keywords, emoción, confianza


#### **Herramientas y Entorno**

- **Lenguaje**: Python 3.9+
- **Orquestación**: Función `generar_respuesta_streamlit()` en `langchain.py`
- **Reglas**: Diccionarios `DOMAIN_KEYWORDS`, `role_details`, `EMOTION_TO_TONE`
- **Logging**: Módulo `logging` para trazabilidad


#### **Código Relevante**

**Archivo**: `src/langchain.py`

**Flujo principal (simplificado):**

```python
def generar_respuesta_streamlit(pregunta, tipo_usuario='Prestador', debug=False):
    # 1. Extracción de características
    keywords, kw_time = detect_keywords(pregunta)
    (emocion, emo_score), emo_time = detect_emotion(pregunta)
    confianza, conf_time = fuzzy_problem_categorization(keywords)
    
    # 2. Validación de dominio (REGLA CRÍTICA)
    kw_set = set(keywords or [])
    domain_match = kw_set.intersection(DOMAIN_KEYWORDS)
    if not domain_match:
        return "Lo siento, no puedo ayudar con ese tipo de consulta...", keywords, emocion, confianza
    
    # 3. Consulta a base de conocimiento
    cypher = cypher_query(keywords, tipo_usuario)
    result = graph.query(cypher)
    
    # 4. Evaluación de resultados y confianza
    if result and matched_count > 0:
        tipo_problema = r.get('tipo_problema')
        solucion = r.get('solucion')
        if confianza < 0.7:
            postdata = "Confianza baja, verificar manualmente."
        else:
            postdata = "Respuesta recomendada por nuestro sistema."
    else:
        postdata = "No se encontró solución automática..."
    
    # 5. Personalización por rol y emoción
    rd = role_details.get(tipo_usuario)
    emotion_tone = EMOTION_TO_TONE.get(emocion)
    
    # 6. Generación de respuesta con LLM
    prompt_llm = f"{rd['saludo']}... Tono {emotion_tone}..."
    respuesta = llm.invoke(prompt_llm)
    
    return respuesta, keywords, emocion, confianza
```

**Reglas de negocio clave:**

```python
# Palabras clave del dominio (define qué consultas son válidas)
DOMAIN_KEYWORDS = {
    'pago','pagos','acreditar','transferencia','tarjeta','comision',
    'servicio','proveedor','prestador','reclamo','evento','rechazar'
}

# Personalización por rol
role_details = {
    "Organizador": {"saludo": "¡Hola estimado organizador!", "tono": "empático"},
    "Prestador": {"saludo": "Hola prestador,", "tono": "apoyo operativo"},
    "Propietario": {"saludo": "Bienvenido propietario,", "tono": "estratégico"}
}

# Mapeo de emoción a tono de respuesta
EMOTION_TO_TONE = {
    "enojo": "serio, conciliador y orientado a soluciones",
    "tristeza": "consolador, empático y paciente",
    "alegría": "positivo, amable y orientado a soluciones"
}
```


#### **Ejemplo de Funcionamiento**

**Caso 1: Consulta dentro del dominio**

```
Entrada: "Mi tarjeta fue rechazada, ¿qué hago?"
├─ Keywords: ['tarjeta', 'rechazar', 'hacer']
├─ Emoción: "enojo" (0.87)
├─ Confianza: 0.90
├─ Match con DOMAIN_KEYWORDS: ✅ 'tarjeta', 'rechazar'
├─ Neo4j: Categoría "Demora en acreditación"
└─ Respuesta: Tono serio, solución específica + contacto soporte
```

**Caso 2: Consulta fuera del dominio**

```
Entrada: "Me duele la cabeza"
├─ Keywords: ['doler', 'cabeza']
├─ Match con DOMAIN_KEYWORDS: ❌ (ninguna coincidencia)
└─ Respuesta: "Lo siento, no puedo ayudar con ese tipo de consulta. Contacta a un profesional adecuado."
```


#### **Diagrama de Flujo (Representación Visual)**

```
┌─────────────────┐
│ Usuario envía   │
│ consulta        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extrae keywords │ (spaCy)
│ Detecta emoción │ (BETO)
│ Calcula conf.   │ (Fuzzy)
└────────┬────────┘
         │
         ▼
    ┌────────────┐
    │ Keywords ∈ │  NO ──► Derivar a profesional
    │ DOMAIN?    │         adecuado
    └────┬───────┘
         │ SÍ
         ▼
┌─────────────────┐
│ Consulta Neo4j  │
│ con keywords +  │
│ tipo_usuario    │
└────────┬────────┘
         │
         ▼
    ┌────────────┐
    │ Resultado  │  NO ──► "No se encontró solución"
    │ válido?    │
    └────┬───────┘
         │ SÍ
         ▼
    ┌────────────┐
    │ Confianza  │  < 0.7 ──► Advertir baja confianza
    │ >= 0.7?    │
    └────┬───────┘
         │ ≥ 0.7
         ▼
┌─────────────────┐
│ Personaliza por │
│ rol + emoción   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Genera respuesta│ (Ollama LLM)
│ contextualizada │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Retorna respuesta│
│ al usuario       │
└──────────────────┘
```


#### **Resultados de Pruebas**

- ✅ Validación coherente de reglas en 100% de casos de prueba
- ✅ Latencia promedio del flujo completo: 3-8 segundos
- ✅ Derivación correcta de consultas fuera de dominio: 100%
- ✅ Personalización por rol funcionando correctamente

**Métricas registradas** (ver `resultados_pruebas.json`):

```json
{
  "test_id": "2025-11-15T22:30:15",
  "tipo_usuario": "Organizador",
  "keywords": ["tarjeta", "rechazar"],
  "emocion": "enojo",
  "confianza": 0.90,
  "tipo_problema": "Demora en acreditación",
  "tiempos": {
    "keywords_ms": 81.39,
    "emocion_ms": 1080.45,
    "fuzzy_ms": 12.01,
    "neo4j_ms": 2501.61,
    "llm_ms": 4288.25,
    "total_ms": 7963.71
  }
}
```

#### Observaciones y Sugerencias
✅ El flujo es modular y escalable, permitiendo agregar nuevos roles o categorías sin refactorizar

⚠️ Limitación: No mantiene contexto conversacional entre turnos (cada consulta es independiente)

💡 Mejora futura: Implementar memoria de conversación (buffer de contexto o embeddings de historial)

💡 Mejora futura: Agregar reglas para detectar consultas compuestas y descomponerlas

📊 El sistema es diagramable y documentable, facilitando auditorías y explicabilidad