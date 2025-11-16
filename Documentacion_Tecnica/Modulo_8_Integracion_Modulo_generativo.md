# Módulo 8: Integración Generativa (Ollama, LangChain)

## **Propósito**

Generar la respuesta final en lenguaje natural, ajustando el tono, estilo y contenido según el contexto recuperado de la base de conocimiento, el rol del usuario y su estado emocional. Este módulo es la **interfaz de salida** del sistema, transformando datos estructurados en texto conversacional coherente y empático.

***

## **Entradas**

### **Prompt enriquecido** (string formateado) que incluye:

1. **Saludo personalizado por rol**:
    - Organizador: `"¡Hola estimado organizador!"`
    - Prestador: `"Hola prestador,"`
    - Propietario: `"Bienvenido propietario,"`
2. **Tipo de problema detectado**:
    - Ejemplo: `"Tarjeta rechazada"`, `"Demora en acreditación"`
3. **Solución sugerida**:
    - Ejemplo: `"Verifique los datos de su tarjeta e intente nuevamente."`
4. **Tono emocional** (mapeado desde emoción detectada):
    - `enojo` → `"serio, conciliador y orientado a soluciones"`
    - `tristeza` → `"consolador, empático y paciente"`
    - `alegría` → `"positivo, amable y orientado a soluciones"`
5. **Metadatos del análisis**:
    - Emoción detectada y score
    - Nivel de confianza (lógica difusa)
6. **Mensaje original del usuario**
7. **Extras por rol**:
    - Organizador: `"Recuerda que puedes gestionar tus eventos desde el panel de control..."`
    - Prestador: `"No olvides mantener tu perfil y disponibilidad actualizados..."`
8. **Post-data** (según confianza):
    - Alta confianza (≥0.7): `"Respuesta recomendada por nuestro sistema."`
    - Baja confianza (<0.7): `"Respuesta con baja confianza, verificar manualmente."`

***

### **Ejemplo de prompt completo**:

```python
prompt_llm = """
Como asistente del sistema Wevently para la organización de eventos privados donde organizadores, prestadores de servicios y propietarios de lugar operan, contesta a la pregunta del usuario.

¡Hola estimado organizador! Se detectó el problema: Tarjeta rechazada.
Solución sugerida: Verifique los datos de su tarjeta e intente nuevamente.

Por favor responde en un tono serio, conciliador y orientado a soluciones.
(Emoción detectada: enojo, score emoción: 0.87, confianza del sistema: 0.90).

Mensaje original: Mi tarjeta fue rechazada dos veces, ¿qué hago?

Recuerda que puedes gestionar tus eventos desde el panel de control si necesitas asistencia inmediata.

Respuesta recomendada por nuestro sistema.
"""
```


***

## **Salidas**

### **Texto de respuesta generado** (string):

```
¡Hola estimado organizador! Entendemos tu frustración cuando una tarjeta es rechazada durante el proceso de pago.

Para resolver este problema, te recomendamos los siguientes pasos:

1. **Verifica los datos de tu tarjeta**: Asegúrate de que el número de tarjeta, fecha de vencimiento y código CVV estén correctamente ingresados.

2. **Confirma el saldo disponible**: Contacta con tu banco para verificar que tu tarjeta tenga fondos suficientes y no esté bloqueada.

3. **Intenta con otra tarjeta**: Si el problema persiste, prueba con un método de pago alternativo.

4. **Contacta a soporte si continúa fallando**: Si después de estos pasos sigues teniendo problemas, escríbenos a weventlyempresa@gmail.com con:
   - Número de evento
   - Últimos 4 dígitos de la tarjeta
   - Captura del error (si es posible)

Recuerda que puedes gestionar tus eventos desde el panel de control si necesitas asistencia inmediata. Nuestro equipo responderá dentro de las 24 horas hábiles.

¡Estamos aquí para ayudarte!
```

**Características de la respuesta generada**:

- ✅ Tono empático y conciliador (acorde a emoción "enojo")
- ✅ Estructura clara (pasos numerados)
- ✅ Información de contacto de soporte
- ✅ Personalización por rol (menciona "panel de control")
- ✅ Longitud apropiada (150-300 palabras)

***

## **Herramientas y Entorno**

| Componente | Tecnología | Versión | Propósito |
| :-- | :-- | :-- | :-- |
| **Proveedor LLM** | Ollama Cloud | - | Inferencia de modelos LLM en la nube |
| **Modelo** | `gpt-oss:20b-cloud` | - | Modelo generativo de 20B parámetros |
| **Framework integración** | `langchain-ollama` | ≥0.1.0 | Wrapper Python para Ollama |
| **Base LangChain** | `langchain` | ≥0.1.0 | Orquestación de LLMs |
| **Lenguaje** | Python | ≥3.9 | Implementación |

### **Configuración**:

**Variables de entorno** (`.env`):

```env
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_API_KEY=tu_api_key  # Si requiere autenticación
```

**Instalación**:

```bash
pip install langchain langchain-ollama
```


***

## **Código Relevante**

### **Archivo principal**: `src/langchain.py`

#### **1. Inicialización del cliente Ollama**

```python
from langchain_ollama import OllamaLLM
import os

# Configurar cliente LLM
llm = OllamaLLM(
    model="gpt-oss:20b-cloud",
    base_url="https://ollama.com"
)

# Opcional: configurar API key si el modelo lo requiere
if os.getenv('OLLAMA_API_KEY'):
    os.environ['OLLAMA_API_KEY'] = os.getenv('OLLAMA_API_KEY')
```


***

#### **2. Detalles de personalización por rol**

```python
role_details = {
    "Organizador": {
        "saludo": "¡Hola estimado organizador! ",
        "tono": "empático y resolutivo",
        "extra": "Recuerda que puedes gestionar tus eventos desde el panel de control si necesitas asistencia inmediata."
    },
    "Prestador": {
        "saludo": "Hola prestador, ",
        "tono": "enfocado en apoyo operativo",
        "extra": "No olvides mantener tu perfil y disponibilidad actualizados para evitar inconvenientes."
    },
    "Propietario": {
        "saludo": "Bienvenido propietario, ",
        "tono": "informativo y estratégico",
        "extra": "Contacta a soporte si necesitas revisar condiciones contractuales o detalles de cobro."
    }
}
```


***

#### **3. Mapeo de emoción a tono de respuesta**

```python
EMOTION_TO_TONE = {
    "alegría": "positivo, amable y orientado a soluciones",
    "enojo": "serio, conciliador y orientado a soluciones",
    "asco": "profesional y directo",
    "miedo": "tranquilizador, empático y claro",
    "tristeza": "consolador, empático y paciente",
    "sorpresa": "informativo y claro"
}
```


***

#### **4. Construcción y ejecución del prompt**

```python
def generar_respuesta_streamlit(pregunta, tipo_usuario='Prestador', debug=False):
    """
    Función principal que genera respuesta usando LLM.
    """
    # ... (procesamiento previo: keywords, emoción, fuzzy, Neo4j) ...
    
    # Obtener detalles de personalización
    rd = role_details.get(tipo_usuario, role_details["Prestador"])
    emotion_tone = EMOTION_TO_TONE.get(emocion, rd.get('tono', 'neutral'))
    
    # CONSTRUCCIÓN DEL PROMPT
    prompt_llm = (
        f"Como asistente del sistema Wevently para la organización de eventos privados "
        f"donde organizadores, prestadores de servicios y propietarios de lugar operan, "
        f"contesta a la pregunta del usuario.\n\n"
        f"{rd['saludo']}Se detectó el problema: {tipo_problema}. "
        f"Solución sugerida: {solucion}. "
        f"Por favor responde en un tono {emotion_tone}. "
        f"(Emoción detectada: {emocion}, score emoción: {emo_score:.2f}, "
        f"confianza del sistema: {confianza:.2f}). "
        f"Mensaje original: {pregunta}\n"
        f"{rd['extra']}\n{postdata}"
    )
    
    # MEDICIÓN DE LATENCIA
    inicio_llm = time.time()
    
    # INVOCACIÓN DEL LLM
    respuesta = llm.invoke(prompt_llm)
    
    llm_time = time.time() - inicio_llm
    logger.info(f"LLM respuesta generada ({llm_time:.4f}s)")
    
    return respuesta, keywords, emocion, confianza
```


***

## **Ejemplo de Funcionamiento**

### **Caso 1: Organizador con problema de pago (emoción: enojo)**

**Input al LLM**:

```python
tipo_usuario = "Organizador"
tipo_problema = "Tarjeta rechazada"
solucion = "Verifique los datos de su tarjeta e intente nuevamente."
emocion = "enojo"
emo_score = 0.87
confianza = 0.90
pregunta = "Mi tarjeta fue rechazada dos veces, ¿qué hago?"
```

**Prompt generado**:

```
Como asistente del sistema Wevently para la organización de eventos privados donde organizadores, prestadores de servicios y propietarios de lugar operan, contesta a la pregunta del usuario.

¡Hola estimado organizador! Se detectó el problema: Tarjeta rechazada.
Solución sugerida: Verifique los datos de su tarjeta e intente nuevamente.

Por favor responde en un tono serio, conciliador y orientado a soluciones.
(Emoción detectada: enojo, score emoción: 0.87, confianza del sistema: 0.90).

Mensaje original: Mi tarjeta fue rechazada dos veces, ¿qué hago?

Recuerda que puedes gestionar tus eventos desde el panel de control si necesitas asistencia inmediata.

Respuesta recomendada por nuestro sistema.
```

**Respuesta del LLM**:

```
¡Hola estimado organizador!

Entiendo perfectamente tu frustración cuando una tarjeta es rechazada durante el pago. Trabajemos juntos para resolver esto:

**Pasos inmediatos:**

1. **Verifica los datos ingresados**:
   - Número de tarjeta completo
   - Fecha de vencimiento (MM/AA)
   - Código CVV (3 dígitos al reverso)
   - Nombre tal como aparece en la tarjeta

2. **Confirma con tu banco**:
   - Saldo disponible suficiente
   - Sin bloqueos por seguridad
   - Límite de compra no excedido

3. **Prueba alternativas**:
   - Otra tarjeta de débito/crédito
   - Diferentes navegadores o dispositivos

**Si el problema persiste:**
Contacta a nuestro equipo de soporte en weventlyempresa@gmail.com con:
- ID del evento
- Últimos 4 dígitos de la tarjeta
- Captura del mensaje de error

Responderemos en menos de 24 horas hábiles.

Recuerda que puedes gestionar tus eventos desde el panel de control si necesitas asistencia inmediata.

¡Estamos aquí para ayudarte!
```

**Latencia**: 4.2 segundos

***

### **Caso 2: Prestador con demora de pago (emoción: enojo)**

**Input al LLM**:

```python
tipo_usuario = "Prestador"
tipo_problema = "No recibí pago"
solucion = "El dinero debe acreditarse en 24-48hs según términos y condiciones."
emocion = "enojo"
emo_score = 0.92
confianza = 0.90
pregunta = "Todavía no recibí el pago y necesito una solución urgente"
```

**Respuesta del LLM**:

```
Hola prestador,

Entendemos tu preocupación y la urgencia de tu situación. Veamos cómo resolverlo:

**Información importante:**
Según nuestros términos y condiciones, la acreditación de pagos se realiza en un plazo de 24 a 48 horas hábiles después de finalizado el evento.

**¿Qué hacer ahora?**

1. **Verifica el estado del pago**:
   - Ingresa a tu panel de prestador
   - Sección "Pagos" → "Historial"
   - Confirma la fecha del evento y el estado de acreditación

2. **Si ya pasaron más de 48 horas hábiles**:
   Envía un correo urgente a weventlyempresa@gmail.com con:
   - Tu ID de prestador
   - Número de evento
   - Fecha del servicio prestado
   - Monto acordado
   - Captura del panel de pagos

3. **Información bancaria actualizada**:
   Asegúrate de que tu CBU/CVU esté correctamente registrado en tu perfil. Errores en estos datos pueden demorar la acreditación.

**Prioridad en tu caso:**
Dado que mencionas urgencia, nuestro equipo de soporte priorizará tu caso y te responderá dentro de las 24 horas siguientes al correo recibido.

No olvides mantener tu perfil y disponibilidad actualizados para evitar inconvenientes.

Estamos comprometidos a resolver tu situación cuanto antes.

```

**Latencia**: 5.4 segundos

---

### **Caso 3: Consulta fuera de dominio (sin match en Neo4j)**

**Input al LLM**:
```

tipo_usuario = "Organizador"
tipo_problema = "No definido"
solucion = "No definida"
emocion = "alegría"
emo_score = 0.62
confianza = 0.27
pregunta = "Me duele la cabeza"

```

**Prompt generado**:
```

Como asistente del sistema Wevently para la organización de eventos privados...

¡Hola estimado organizador! Se detectó el problema: No definido.
Solución sugerida: No definida.

Por favor responde en un tono positivo, amable y orientado a soluciones.
(Emoción detectada: alegría, score emoción: 0.62, confianza del sistema: 0.27).

Mensaje original: Me duele la cabeza

Recuerda que puedes gestionar tus eventos desde el panel de control si necesitas asistencia inmediata.

No se encontró solución automática, te derivaremos a soporte. (soporte@wevently.com)

```

**Respuesta del LLM**:
```

¡Hola estimado organizador!

Lamento que no te sientas bien. Sin embargo, debo mencionarte que mi función es ayudarte específicamente con consultas relacionadas con la plataforma Wevently (eventos, pagos, servicios, proveedores).

Para temas de salud como el que mencionas, te recomiendo:

- Consultar con un profesional médico
- Contactar con tu servicio de salud

Si tienes alguna consulta sobre tus eventos o la plataforma Wevently, estaré encantado de ayudarte. Recuerda que puedes gestionar tus eventos desde el panel de control si necesitas asistencia inmediata.

¡Que te mejores pronto!

```

**Latencia**: 3.8 segundos

---

## **Diagrama de Flujo de Generación**

```

┌────────────────────────────────────┐
│  Datos de módulos anteriores:      │
│  - Keywords                         │
│  - Emoción + score                  │
│  - Confianza (fuzzy)                │
│  - Tipo problema + Solución (Neo4j) │
│  - Tipo usuario                     │
└───────────────┬────────────────────┘
│
▼
┌────────────────────────────────────┐
│  Selección de detalles por rol     │
│  role_details[tipo_usuario]        │
└───────────────┬────────────────────┘
│
▼
┌────────────────────────────────────┐
│  Mapeo de emoción a tono           │
│  EMOTION_TO_TONE[emocion]          │
└───────────────┬────────────────────┘
│
▼
┌────────────────────────────────────┐
│  Construcción del prompt           │
│  - Instrucción del sistema         │
│  - Saludo personalizado            │
│  - Problema + Solución             │
│  - Tono emocional                  │
│  - Mensaje original                │
│  - Extras por rol                  │
│  - Post-data                       │
└───────────────┬────────────────────┘
│
▼
┌────────────────────────────────────┐
│  llm.invoke(prompt_llm)            │
│  ↓                                 │
│  Ollama Cloud API                  │
│  Model: gpt-oss:20b-cloud          │
│  ↓                                 │
│  Generación de texto (4-5 seg)    │
└───────────────┬────────────────────┘
│
▼
┌────────────────────────────────────┐
│  Respuesta en lenguaje natural     │
│  - Estructurada (pasos, bullets)   │
│  - Tono ajustado a emoción         │
│  - Información de contacto         │
│  - Cierre empático                 │
└────────────────────────────────────┘

```

---

## **Resultados de Pruebas**

### **Prueba 1: Consistencia de tono por emoción**

| Emoción | Tono Esperado | Frases en Respuesta | ✓/✗ |
|---------|---------------|---------------------|-----|
| enojo | Serio, conciliador | "Entendemos tu frustración...", "Trabajemos juntos..." | ✅ |
| tristeza | Consolador, empático | "Lamentamos mucho...", "Estamos aquí para apoyarte..." | ✅ |
| alegría | Positivo, amable | "¡Nos alegra ayudarte!", "Será un placer..." | ✅ |
| miedo | Tranquilizador | "No te preocupes...", "Es completamente seguro..." | ✅ |

**Conclusión**: El modelo respeta las instrucciones de tono en 100% de los casos

---

### **Prueba 2: Personalización por rol**

| Rol | Elemento Esperado | Presente en Respuesta | ✓/✗ |
|-----|-------------------|----------------------|-----|
| Organizador | "panel de control" | ✅ | ✅ |
| Organizador | Saludo "estimado organizador" | ✅ | ✅ |
| Prestador | "mantener tu perfil actualizado" | ✅ | ✅ |
| Prestador | Enfoque operativo | ✅ | ✅ |
| Propietario | "condiciones contractuales" | ✅ | ✅ |

**Conclusión**: Personalización por rol funciona correctamente

---

### **Prueba 3: Latencia de generación**

| Longitud Prompt | Longitud Respuesta | Latencia (seg) | Observación |
|-----------------|-------------------|----------------|-------------|
| 150 caracteres | ~200 palabras | 3.8 | Respuesta corta |
| 300 caracteres | ~350 palabras | 4.2 | Respuesta media |
| 500 caracteres | ~500 palabras | 5.4 | Respuesta larga |
| 700 caracteres | ~600 palabras | 6.8 | Respuesta muy larga |

**Promedio**: 4.3 segundos (53% del tiempo total del sistema)

**Comparación con otros LLMs** (estimado):
| Modelo | Latencia Típica | Observación |
|--------|-----------------|-------------|
| gpt-oss:20b-cloud (actual) | 4.3 seg | Modelo usado |
| GPT-3.5-turbo (OpenAI) | 1-2 seg | Más rápido, costo por token |
| Llama-2-13b (local) | 8-12 seg | CPU local sin GPU |
| Mistral-7b (local + GPU) | 0.5-1 seg | Requiere GPU potente |

---

### **Prueba 4: Coherencia con información de Neo4j**

**Caso**: Verificar que el LLM no "alucine" información contradictoria

| Problema Neo4j | Solución Neo4j | Respuesta LLM menciona solución | ✓/✗ |
|----------------|----------------|---------------------------------|-----|
| "Tarjeta rechazada" | "Verifique datos..." | ✅ Menciona verificación | ✅ |
| "Info comisiones" | "1% por operación" | ✅ Menciona 1% | ✅ |
| "Demora acreditación" | "24-48hs hábiles" | ✅ Menciona plazo | ✅ |

**Observación**: El prompt estructurado minimiza alucinaciones

---

### **Prueba 5: Manejo de casos sin solución**

**Input**: Consulta fuera de dominio ("me duele la cabeza")

**Comportamiento esperado**: Derivar amablemente sin intentar dar consejos médicos

**Resultado**: ✅ El LLM correctamente:
- Reconoce que no es su dominio
- No da consejos médicos
- Sugiere consultar profesional apropiado
- Ofrece ayuda en temas de Wevently

---

## **Observaciones y Sugerencias**

### **Fortalezas**
- ✅ **Personalización profunda**: Rol + emoción + contexto crean respuestas únicas
- ✅ **Tono consistente**: Instrucciones de tono son respetadas por el modelo
- ✅ **Sin alucinaciones críticas**: Información de Neo4j se refleja fielmente
- ✅ **Estructura clara**: Respuestas con bullets, pasos numerados, secciones
- ✅ **Fácil cambio de modelo**: Arquitectura LangChain permite cambiar proveedor sin refactorizar

### **Limitaciones Identificadas**
- ⚠️ **Latencia dominante**: 53% del tiempo total del sistema
- ⚠️ **Dependencia de servicio externo**: Si Ollama Cloud cae, sistema no puede responder
- ⚠️ **Sin control de longitud**: Algunas respuestas exceden 500 palabras (demasiado largo)
- ⚠️ **Costo por uso**: Modelos cloud cobran por token (no medido en versión académica)
- ⚠️ **Sin memoria conversacional**: Cada mensaje es independiente, no recuerda contexto previo

### **Mejoras Futuras**

#### **1. Control de longitud de respuesta**
```

llm = OllamaLLM(
model="gpt-oss:20b-cloud",
base_url="https://ollama.com",
max_tokens=300,  \# Limitar longitud
temperature=0.7   \# Controlar creatividad
)

```

**Impacto**: Respuestas más concisas y rápidas

---

#### **2. Sistema de fallback local**
```


# LLM primario (cloud)

llm_primary = OllamaLLM(model="gpt-oss:20b-cloud", base_url="https://ollama.com")

# LLM fallback (local)

llm_fallback = OllamaLLM(model="llama2:7b", base_url="http://localhost:11434")

def invoke_llm_con_fallback(prompt):
try:
return llm_primary.invoke(prompt)
except Exception as e:
logger.warning(f"LLM cloud falló, usando fallback local: {e}")
return llm_fallback.invoke(prompt)

```

**Impacto**: Alta disponibilidad incluso si servicio cloud falla

---

#### **3. Memoria conversacional (para chat multi-turno)**
```

from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()

def generar_respuesta_con_memoria(pregunta, tipo_usuario):
\# Recuperar contexto previo
historial = memory.load_memory_variables({})

    prompt_con_contexto = f"""
    Historial de conversación:
    {historial}
    
    Nueva pregunta: {pregunta}
    
    Responde considerando el contexto previo...
    """
    
    respuesta = llm.invoke(prompt_con_contexto)
    
    # Guardar en memoria
    memory.save_context({"input": pregunta}, {"output": respuesta})
    
    return respuesta
    ```

**Impacto**: Soporte para conversaciones naturales multi-turno

---

#### **4. Caché de respuestas frecuentes**
```

from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def generar_respuesta_cached(prompt_hash):
\# Si el prompt ya fue procesado, retornar de caché
...

def generar_respuesta_streamlit(pregunta, ...):
\# ... construir prompt ...
prompt_hash = hashlib.md5(prompt_llm.encode()).hexdigest()

    # Buscar en caché primero
    if prompt_hash in cache:
        return cache[prompt_hash], keywords, emocion, confianza
    
    # Generar nueva respuesta
    respuesta = llm.invoke(prompt_llm)
    cache[prompt_hash] = respuesta
    return respuesta, keywords, emocion, confianza
    ```

**Impacto**: Preguntas frecuentes se responden instantáneamente (<10 ms)

---

#### **5. Streaming de respuesta (UX mejorada)**
```

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

llm_streaming = OllamaLLM(
model="gpt-oss:20b-cloud",
streaming=True,
callbacks=[StreamingStdOutCallbackHandler()]
)

# En Streamlit

import streamlit as st

response_placeholder = st.empty()
full_response = ""

for chunk in llm_streaming.stream(prompt_llm):
full_response += chunk
response_placeholder.markdown(full_response)

```

**Impacto**: Usuario ve respuesta generándose en tiempo real (mejor UX)

---

#### **6. Post-procesamiento de respuesta**
```

def post_procesar_respuesta(respuesta):
\# Limitar longitud
if len(respuesta) > 1000:
respuesta = respuesta[:1000] + "..."

    # Remover repeticiones
    lineas = respuesta.split('\n')
    lineas_unicas = []
    for linea in lineas:
        if linea not in lineas_unicas:
            lineas_unicas.append(linea)
    respuesta = '\n'.join(lineas_unicas)
    
    # Asegurar cierre amable
    if not any(cierre in respuesta.lower() for cierre in ['saludos', 'estamos aquí', 'ayudarte']):
        respuesta += "\n\n¡Estamos aquí para ayudarte!"
    
    return respuesta
    ```

**Impacto**: Respuestas más consistentes y profesionales

---

## **Resumen Técnico**

| Aspecto | Valor | Observación |
|---------|-------|-------------|
| **Modelo LLM** | gpt-oss:20b-cloud | 20 mil millones de parámetros |
| **Proveedor** | Ollama Cloud | Servicio cloud https://ollama.com |
| **Latencia promedio**| 4.3 segundos | 53% del tiempo total del sistema |
| **Longitud respuesta** | 200-500 palabras | Variable según complejidad |
| **Tono personalizado** | 6 variantes | Por emoción detectada |
| **Roles soportados** | 3 | Organizador, Prestador, Propietario |
| **Consistencia con Neo4j** | 100% | Sin alucinaciones detectadas |
| **Disponibilidad** | Dependiente de cloud | Sin fallback implementado |
| **Costo** | No medido | Versión académica |
| **% del tiempo total** | 53% | Cuello de botella principal |

***

## **Comparación con Alternativas**

### **Opción actual: Ollama Cloud (gpt-oss:20b-cloud)**

- ✅ Sin setup de infraestructura
- ✅ Modelo potente (20B parámetros)
- ✅ Fácil integración con LangChain
- ⚠️ Latencia 4-5 segundos
- ⚠️ Dependencia de servicio externo
- ⚠️ Costo por token (no medido)


### **Alternativa 1: OpenAI GPT-3.5-turbo**

- ✅ Latencia 1-2 segundos (más rápido)
- ✅ Respuestas de alta calidad
- ⚠️ Costo alto (\$0.002/1K tokens)
- ⚠️ Datos enviados a terceros (privacidad)


### **Alternativa 2: Llama-2-13b (local)**

- ✅ Sin costo por uso
- ✅ Soberanía de datos
- ✅ Sin dependencia de internet
- ⚠️ Requiere GPU potente
- ⚠️ Latencia 8-12 seg en CPU
- ⚠️ Setup complejo


### **Alternativa 3: Templates estáticos + variables**

- ✅ Latencia <10 ms
- ✅ Costo cero
- ✅ 100% predecible
- ⚠️ Sin flexibilidad lingüística
- ⚠️ Respuestas repetitivas

***

## **Arquitectura de Integración Final**

```
┌─────────────────────────────────────────┐
│         Sistema Completo                │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
Módulos 1-7              Módulo 8 (LLM)
(~4 seg)                  (~4 seg)
                              │
                              ▼
                    ┌─────────────────┐
                    │  Ollama Cloud   │
                    │  API REST       │
                    │  HTTPS          │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  gpt-oss:20b    │
                    │  20B parámetros │
                    │  Autoregresivo  │
                    └────────┬────────┘
                             │
                             ▼
                    Respuesta generada
                    (texto natural)
```


***

## **Ejemplo de Integración Completa (End-to-End)**

### **Flujo completo desde input hasta output**:

```python
# INPUT DEL USUARIO
pregunta = "Mi tarjeta fue rechazada dos veces, ¿qué hago?"
tipo_usuario = "Organizador"

# MÓDULO 7: NLP
keywords = ['tarjeta', 'rechazar', 'hacer']  # 81 ms
emocion, score = ('enojo', 0.87)             # 1080 ms

# MÓDULO 3: Lógica Difusa
confianza = 0.90                             # 12 ms

# MÓDULO 4: Neo4j
tipo_problema = "Tarjeta rechazada"          # 2501 ms
solucion = "Verifique los datos de su tarjeta..."

# MÓDULO 8: Generación (ESTE MÓDULO)
# Construcción de prompt
rd = role_details["Organizador"]
emotion_tone = EMOTION_TO_TONE["enojo"]

prompt_llm = f"""
Como asistente del sistema Wevently...
{rd['saludo']}Se detectó el problema: {tipo_problema}.
Solución sugerida: {solucion}.
Por favor responde en un tono {emotion_tone}.
...
"""

# Invocación del LLM
respuesta = llm.invoke(prompt_llm)          # 4288 ms

# OUTPUT FINAL
print(respuesta)
"""
¡Hola estimado organizador!

Entendemos tu frustración cuando una tarjeta es rechazada...

**Pasos inmediatos:**
1. Verifica los datos ingresados...
2. Confirma con tu banco...
3. Prueba alternativas...

**Si el problema persiste:**
Contacta a soporte en weventlyempresa@gmail.com...

¡Estamos aquí para ayudarte!
"""

# TIEMPO TOTAL: ~7.96 segundos
```


***

## **Conclusión**

El Módulo 8 (Integración Generativa) es el **componente de interfaz humana** del sistema, transformando datos fríos y estructurados en conversaciones cálidas y empáticas. Aunque consume el 53% del tiempo total de respuesta, su valor es insustituible: convierte un sistema experto técnico en un asistente conversacional que los usuarios perciben como "inteligente" y "humano".

### **Logros clave**:

1. ✅ **Personalización triple**: Rol × Emoción × Contexto
2. ✅ **Respuestas estructuradas**: Pasos numerados, bullets, secciones claras
3. ✅ **Tono consistente**: Instrucciones respetadas en 100% de casos
4. ✅ **Sin alucinaciones críticas**: Fidelidad a información de Neo4j
5. ✅ **Arquitectura flexible**: Cambiar de proveedor LLM es trivial

### **Próximos pasos para producción**:

- Implementar fallback local para alta disponibilidad
- Agregar caché para preguntas frecuentes (reducir latencia y costo)
- Monitorear costo por token en ambiente real
- Considerar streaming para mejor UX
- Evaluar modelos alternativos (GPT-3.5, Llama-2) según métricas reales



