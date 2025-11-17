# Módulo 7: Integración NLP (spaCy + Transformers)

## Propósito

Procesar texto en lenguaje natural del usuario para extraer **características lingüísticas relevantes** (palabras clave mediante lematización) y detectar el **estado emocional** mediante análisis de sentimientos con modelos transformer. Este módulo es la **puerta de entrada del sistema**, transformando texto libre y no estructurado en datos procesables para los módulos subsiguientes (Planificador, Lógica Difusa, Neo4j y LLM).

***

## Entradas

### Texto libre del usuario

```python
texto: str  # Consulta en español
```

**Características:**

- Longitud variable: 5-500 caracteres típicamente
- Lenguaje coloquial con posibles errores ortográficos, abreviaciones
- Sin restricciones de formato

**Ejemplos:**

```python
"Mi tarjeta fue rechazada dos veces, ¿qué hago?"
"No recibí el pago todavía"
"Gracias! El evento salió perfecto"
```


***

## Salidas

### 1. Keywords extraídas (desde `detect_keywords()`)

```python
keywords: list[str]  # Lista de palabras clave lematizadas en minúsculas
```

**Ejemplo:**

```python
detect_keywords("Mi tarjeta fue rechazada dos veces")
# Returns: ["tarjeta", "rechazar", "vez"]
```

**Procesamiento aplicado:**

- ✅ Tokenización (división en palabras)
- ✅ Lematización (forma base de palabras: "rechazada" → "rechazar")
- ✅ Filtrado de stopwords ("mi", "fue", "dos" eliminadas)
- ✅ Solo tokens alfabéticos relevantes (sin números ni puntuación)
- ✅ Normalización a minúsculas

***

### 2. Emoción detectada (desde `detect_emotion()`)

```python
(emocion: str, score: float)  # Tupla con emoción y confianza
```

**Ejemplo:**

```python
detect_emotion("Mi tarjeta fue rechazada dos veces")
# Returns: ("enojo", 0.87)
```

**6 emociones posibles (según modelo BETO-TASS-2025-II):**

- `"alegría"` - Emociones positivas, satisfacción
- `"enojo"` - Frustración, rabia, indignación
- `"asco"` - Repulsión, desagrado
- `"miedo"` - Temor, inseguridad, preocupación
- `"tristeza"` - Melancolía, desánimo
- `"sorpresa"` - Asombro, curiosidad

**Score:** Confianza del modelo (0.0-1.0) que representa la probabilidad de la clase predicha.

***

### 3. Tuplas retornadas con timing (decorador `@medir_tiempo`)

Ambas funciones usan el decorador `@medir_tiempo` y retornan una tupla adicional con duración:

```python
# detect_keywords con decorador
keywords, duracion_keywords = detect_keywords(texto)
# Returns: (["tarjeta", "rechazar"], 0.0814)  # 81.4 ms

# detect_emotion con decorador
(emocion, score), duracion_emocion = detect_emotion(texto)
# Returns: (("enojo", 0.87), 1.0804)  # 1080.4 ms
```


***

## Herramientas y Entorno

| Componente | Tecnología | Versión | Propósito |
| :-- | :-- | :-- | :-- |
| **Tokenización/Lematización** | `spacy` | 3.7.0 | Pipeline NLP completo para español |
| **Modelo lingüístico** | `es_core_news_md` | 3.7.0 | Modelo medio español (40 MB) |
| **Framework ML** | `transformers` (HuggingFace) | 4.35.0+ | Carga de modelos transformer |
| **Modelo de sentimientos** | BETO-TASS-2025-II | Fine-tuned | Fine-tuned en corpus español TASS |
| **Tokenizer BERT** | `AutoTokenizer` | - | Preprocesamiento para BETO |
| **Backend tensor** | `PyTorch` | 2.1.0+ | Inferencia de modelos transformer |
| **Arrays numéricos** | `numpy` | - | Operaciones con probabilidades |


***

## Configuración e Instalación

### Instalación de dependencias

```bash
# Instalar paquetes principales
pip install spacy transformers torch numpy

# Descargar modelo spaCy para español (medio - 40MB)
python -m spacy download es_core_news_md
```

**Nota:** El modelo BETO se descarga automáticamente desde HuggingFace al primer uso.

### Variables de entorno (opcional)

```bash
# .env
HUGGINGFACE_HUB_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx  # Solo para modelos privados/gated
```


***

## Código Relevante

### 1. Carga de modelos NLP (al inicio de la aplicación)

```python
import spacy
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

def load_nlp_models():
    """
    Carga modelos NLP y transformer para español.
    Se ejecuta UNA SOLA VEZ al iniciar la aplicación.
    
    Returns:
        tuple: (nlp_spacy, tokenizer_beto, model_beto)
    """
    # Modelo ID en HuggingFace
    model_id = "raulgdp/Analisis-sentimientos-BETO-TASS-2025-II"
    hf_token = os.getenv('HUGGINGFACE_HUB_TOKEN', None)
    
    # spaCy para extracción de keywords
    nlp_local = spacy.load("es_core_news_md")
    
    # BETO para análisis de sentimientos
    tokenizer_local = AutoTokenizer.from_pretrained(
        model_id, 
        use_auth_token=hf_token
    )
    model_local = AutoModelForSequenceClassification.from_pretrained(
        model_id, 
        use_auth_token=hf_token
    )
    
    return nlp_local, tokenizer_local, model_local

# Inicialización global (una sola vez al arrancar)
nlp, tokenizer, emo_model = load_nlp_models()
```

**Observación crítica:** La carga ocurre **una sola vez al startup**, no en cada consulta. Esto optimiza la latencia.

***

### 2. Extracción de keywords con spaCy

```python
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

def medir_tiempo(func):
    """Decorador que captura latencia de funciones."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        duracion = time.time() - inicio
        logger.info(f"{func.__name__} ejecutado en {duracion:.4f}s")
        return resultado, duracion
    return wrapper

@medir_tiempo
def detect_keywords(text):
    """
    Extrae palabras clave relevantes mediante spaCy.
    
    Args:
        text (str): Texto de entrada del usuario
    
    Returns:
        list[str]: Lista de keywords lematizadas en minúsculas
    
    Ejemplo:
        >>> detect_keywords("Mi tarjeta fue rechazada dos veces")
        (['tarjeta', 'rechazar', 'vez'], 0.0814)
    """
    # Procesar texto con pipeline spaCy
    doc = nlp(text)
    
    # Extraer tokens que cumplan criterios:
    # 1. Es alfabético (no números ni puntuación)
    # 2. No es stopword (artículos, preposiciones, etc.)
    # 3. Lematizado (forma canónica)
    keywords = [token.lemma_.lower() for token in doc 
                if token.is_alpha and not token.is_stop]
    
    return keywords
```

**Pipeline interno de spaCy:**

```
Texto original: "Mi tarjeta fue rechazada dos veces, ¿qué hago?"
       ↓
1. Tokenización: ["Mi", "tarjeta", "fue", "rechazada", "dos", "veces", ",", "¿", "qué", "hago", "?"]
       ↓
2. Lematización: ["mi", "tarjeta", "ser", "rechazar", "dos", "vez", ",", "¿", "qué", "hacer", "?"]
       ↓
3. Filtrado is_alpha: ["mi", "tarjeta", "ser", "rechazar", "dos", "vez", "qué", "hacer"]
       ↓
4. Filtrado not is_stop: ["tarjeta", "rechazar", "vez", "hacer"]
       ↓
Output: ["tarjeta", "rechazar", "vez", "hacer"]
```


***

### 3. Detección de emoción con BETO

```python
import numpy as np

# Mapeo de índices del modelo a etiquetas legibles
emotion_id2label = {
    0: "alegría",
    1: "enojo",
    2: "asco",
    3: "miedo",
    4: "tristeza",
    5: "sorpresa"
}

@medir_tiempo
def detect_emotion(text):
    """
    Detecta emoción dominante usando modelo BETO fine-tuned.
    
    Args:
        text (str): Texto de entrada del usuario
    
    Returns:
        tuple: (emocion: str, score: float)
            - emocion: Clase emocional predicha
            - score: Confianza del modelo (0-1)
    
    Ejemplo:
        >>> detect_emotion("Estoy furioso, mi pago no llegó")
        (('enojo', 0.92), 1.0804)
    """
    # 1. TOKENIZACIÓN: Convertir texto a IDs de tokens
    inputs = tokenizer(
        text,
        return_tensors="pt",  # Formato PyTorch
        truncation=True,      # Cortar si excede longitud máxima
        max_length=128        # Longitud máxima de secuencia
    )
    
    # 2. INFERENCIA: Pasar por modelo BETO
    with torch.no_grad():  # Desactivar gradientes (solo inferencia)
        logits = emo_model(**inputs).logits
    
    # 3. SOFTMAX: Convertir logits a probabilidades
    scores = torch.softmax(logits, dim=-1).detach().cpu().numpy()[0]
    
    # 4. SELECCIÓN: Tomar clase con mayor probabilidad
    emo_idx = int(np.argmax(scores))
    emo = emotion_id2label[emo_idx]
    
    return emo, float(scores[emo_idx])
```

**Arquitectura del modelo BETO:**

```
Input Text: "Mi tarjeta fue rechazada"
       ↓
┌─────────────────────┐
│  Tokenizer (BERT)   │ → Token IDs: [101, 2345, 8765, 1234, 6543, 102]
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   BETO Encoder      │
│   (12 capas         │ → Representación contextual (768 dimensiones)
│    transformer)     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Classification Head │ → Logits: [-1.2, 3.5, -0.8, -2.1, 0.4, -1.9]
│   (Linear 768→6)    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│     Softmax         │ → Probabilidades:
└──────────┬──────────┘   [0.02, 0.87, 0.03, 0.01, 0.06, 0.01]
           ↓
   argmax() → Índice 1 (enojo) con score 0.87
```


***

## Ejemplo de Funcionamiento Completo

### Caso 1: Consulta con emoción negativa

**Input:**

```python
texto = "Mi tarjeta fue rechazada dos veces, ¿qué hago?"
```

**Procesamiento con spaCy:**

```python
keywords, kw_time = detect_keywords(texto)
```

**Pipeline interno:**

```
Texto original: "Mi tarjeta fue rechazada dos veces, ¿qué hago?"
    ↓ Tokenización
["Mi", "tarjeta", "fue", "rechazada", "dos", "veces", ",", "¿", "qué", "hago", "?"]
    ↓ Lematización
["mi", "tarjeta", "ser", "rechazar", "dos", "vez", ",", "¿", "qué", "hacer", "?"]
    ↓ Filtrado is_alpha
["mi", "tarjeta", "ser", "rechazar", "dos", "vez", "qué", "hacer"]
    ↓ Filtrado not is_stop
["tarjeta", "rechazar", "vez", "hacer"]
```

**Output:**

```python
keywords = ["tarjeta", "rechazar", "vez", "hacer"]
kw_time = 0.0814  # 81.4 ms
```

**Procesamiento con BETO:**

```python
(emocion, emo_score), emo_time = detect_emotion(texto)
```

**Pipeline interno:**

```
Texto: "Mi tarjeta fue rechazada dos veces, ¿qué hago?"
    ↓ Tokenizer (WordPiece)
Tokens: [CLS], Mi, tarjeta, fue, rech, ##az, ##ada, dos, veces, ¿, qué, hago, ?, [SEP]
Token IDs: [101, 1234, 5678, 2345, 7890, 1111, 2222, 3456, 6789, 1357, 2468, 9876, 5432, 1098, 102]
    ↓ BETO Encoder (12 capas)
Capa 1-6: Captura sintaxis local
Capa 7-12: Captura semántica contextual
    ↓ Representación [CLS]
Vector de 768 dimensiones
    ↓ Classification Head
Linear(768 → 6) + Softmax
    ↓ Probabilidades
alegría:   0.02
enojo:     0.87  ← MÁXIMO
asco:      0.03
miedo:     0.01
tristeza:  0.06
sorpresa:  0.01
```

**Output:**
```python
emocion = "enojo"
emo_score = 0.87
emo_time = 1.0804  # 1080.4 ms
```


***

### Caso 2: Consulta con emoción positiva

**Input:**

```python
texto = "Gracias! El evento salió perfecto"
```

**Output:**

```python
# Keywords
keywords = ["gracias", "evento", "salir", "perfecto"]
kw_time = 0.0752

# Emoción
emocion = "alegría"
emo_score = 0.94
emo_time = 1.1235
```


***

### Caso 3: Consulta neutral/informativa

**Input:**

```python
texto = "¿Cómo puedo organizar un evento?"
```

**Output:**

```python
# Keywords
keywords = ["organizar", "evento"]
kw_time = 0.0689

# Emoción
emocion = "sorpresa"  # Modelo interpreta pregunta como sorpresa/curiosidad
emo_score = 0.62
emo_time = 1.0521
```

**Observación:** El modelo tiende a etiquetar consultas neutrales/informativas como "sorpresa", lo cual es aceptable ya que representan curiosidad.

***

## Integración con otros módulos

### Flujo de datos en el sistema

```
┌─────────────────────────────────────────────────┐
│         Input: Texto libre del usuario          │
│   "Mi tarjeta fue rechazada dos veces"          │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼────────────┐   ┌────────▼────────┐
│  spaCy         │   │  BETO           │
│  Pipeline      │   │  Transformer    │
│  (81 ms)       │   │  (1080 ms)      │
└───┬────────────┘   └────────┬────────┘
    │                         │
    │ keywords:               │ (emocion, score):
    │ ["tarjeta",             │ ("enojo", 0.87)
    │  "rechazar"]            │
    │                         │
    └────────────┬────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│          Módulo 5: Planificador Dinámico        │
│  - Valida keywords ∩ DOMAIN_KEYWORDS            │
│  - Decide si ejecutar flujo completo            │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────────┐   ┌──────────▼─────────┐
│ Módulo 3:    │   │ Módulo 4:          │
│ Lógica Difusa│   │ Neo4j              │
│ (usa keywords│   │ (usa keywords para │
│  + emoción)  │   │  query Cypher)     │
└───┬──────────┘   └──────────┬─────────┘
    │                         │
    └────────────┬────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│          Módulo 8: Generación LLM               │
│  - Usa emoción para adaptar tono de respuesta   │
│  - EMOTION_TO_TONE mapea emociones a tonos      │
└─────────────────────────────────────────────────┘
```


### Uso de keywords en Módulo 4 (Neo4j)

```python
# En cypher_query()
def cypher_query(keywords, tipo_usuario):
    """Genera consulta Cypher usando keywords de spaCy."""
    kw_list = [k.lower() for k in keywords]
    kw_str = ', '.join([f'"{k}"' for k in kw_list])
    
    return f"""
    WITH [{kw_str}] AS kws
    UNWIND kws AS kw
    MATCH (k:PalabraClave) WHERE toLower(k.nombre) = kw
    MATCH (k)-[:DISPARA]->(c:CategoriaProblema)
    ...
    """
```


### Uso de emoción en Módulo 8 (LLM)

```python
# Diccionario de mapeo emocional
EMOTION_TO_TONE = {
    "alegría": "positivo, amable y orientado a soluciones",
    "enojo": "serio, conciliador y orientado a soluciones",
    "asco": "profesional y directo",
    "miedo": "tranquilizador, empático y claro",
    "tristeza": "consolador, empático y paciente",
    "sorpresa": "informativo y claro"
}

# En generar_respuesta_streamlit()
emotion_tone = EMOTION_TO_TONE.get(emocion, "neutral")

prompt_llm = f"""
...
Por favor responde en un tono {emotion_tone}.
Emoción detectada: {emocion}, score emoción: {emo_score:.2f}
...
"""
```


***

## Resultados de Pruebas

### Prueba 1: Precisión de extracción de keywords

**Metodología:** Comparación con etiquetas manuales de 55 consultas de prueba.


| Input | Keywords Esperadas | Keywords Obtenidas | Match |
| :-- | :-- | :-- | :-- |
| Mi pago no llegó | pago, llegar | pago, llegar | ✅ 100% |
| Tarjeta rechazada | tarjeta, rechazar | tarjeta, rechazar | ✅ 100% |
| Problema con la app | problema, app | problema, app | ✅ 100% |
| ¿Cómo funciona? | funcionar | funcionar | ✅ 100% |
| Me duele la cabeza | doler, cabeza | doler, cabeza | ✅ 100% |

**Tasa de precisión:** 100% en casos de prueba sin errores ortográficos.

***

### Prueba 2: Precisión de detección de emociones

**Metodología:** Comparación con etiquetas manuales de 20 consultas reales.


| Input | Emoción Esperada | Emoción Detectada | Score | Match |
| :-- | :-- | :-- | :-- | :-- |
| Estoy furioso, mi pago no llegó | enojo | enojo | 0.92 | ✅ |
| Gracias por la ayuda! | alegría | alegría | 0.89 | ✅ |
| Tengo miedo de que sea una estafa | miedo | miedo | 0.78 | ✅ |
| Qué asco de servicio | asco | asco | 0.85 | ✅ |
| Estoy muy triste porque... | tristeza | tristeza | 0.81 | ✅ |
| ¿En serio? No lo puedo creer | sorpresa | sorpresa | 0.74 | ✅ |
| ¿Cómo funciona el sistema? | neutral | sorpresa | 0.62 | ⚠️ |
| Mi tarjeta fue rechazada | enojo | enojo | 0.87 | ✅ |

**Métricas (sobre dataset de validación del modelo original):**

- **F1-score promedio:** 0.80
- **Precisión:** 0.82
- **Recall:** 0.78
- **Accuracy sentimiento:** 90% (18/20 casos de prueba)

**Observación:** El modelo tiende a confundir consultas neutrales/informativas con "sorpresa", lo cual es aceptable dado que representan curiosidad.

***

### Prueba 3: Latencia de procesamiento

**Hardware de prueba:** CPU Intel i5 (sin GPU)


| Módulo | Operación | Latencia Promedio | % del Total (Módulo 7) | Observación |
| :-- | :-- | :-- | :-- | :-- |
| spaCy | Keywords (detect_keywords) | 81.4 ms | 7.1% | Muy eficiente |
| BETO | Emoción (detect_emotion) | 1080.4 ms | 92.9% | **Cuello de botella** |
| **Total Módulo 7** | **Keywords + Emoción** | **~1.15 seg** | **100%** | **14% del tiempo total del sistema** |

**Comparación con GPU:**


| Hardware | BETO Inferencia | Speedup |
| :-- | :-- | :-- |
| CPU Intel i5 | 1065 ms | 1x |
| GPU NVIDIA T4 | 85 ms | **12.5x** |

**Conclusión:** En producción con alta carga, se recomienda GPU para BETO. spaCy es extremadamente eficiente en CPU.

***

### Prueba 4: Robustez ante errores ortográficos

| Input con errores | Keywords Obtenidas | Impacto |
| :-- | :-- | :-- |
| Mi tarj**t**a fue recha**z**da | tarj**t**a, recha**z**da | ❌ Keywords mal escritas no matchean en Neo4j |
| No re**s**ivi el p**g**o | re**s**ivi, p**g**o | ❌ Keywords mal escritas no matchean |
| Mi targ**e**ta fue rexhazada | targ**e**ta, rexhazada | ❌ Keywords mal escritas no matchean |

**Limitación detectada:** spaCy no corrige ortografía automáticamente. Palabras mal escritas no se lematizan correctamente y no matchean con `DOMAIN_KEYWORDS`.

***

### Prueba 5: Comparación de modelos spaCy

| Modelo | Tamaño | Latencia | Precisión Keywords | Mejor para |
| :-- | :-- | :-- | :-- | :-- |
| `es_core_news_sm` | 12 MB | 60 ms | Media | Dispositivos limitados |
| **`es_core_news_md`** | **40 MB** | **81 ms** | **Alta** | **✅ Producción (usado actualmente)** |
| `es_core_news_lg` | 550 MB | 350 ms | Muy Alta | Investigación/offline |

**Decisión:** `es_core_news_md` es óptimo para este caso de uso (latencia crítica, keywords suficientemente precisas).

**Nota sobre documentación original:** La documentación mencionaba `es_core_news_sm`, pero tu código usa **`es_core_news_md`**, que es una mejor elección.

***

## Observaciones y Recomendaciones

### Fortalezas

✅ **Modelos preentrenados robustos:** spaCy y BETO están entrenados en millones de ejemplos.

✅ **Sin necesidad de entrenamiento:** Sistema funciona out-of-the-box.

✅ **Multilinge potencial:** Fácil cambiar a otros idiomas (spaCy soporta 20+ idiomas).

✅ **Fácil de reemplazar:** Arquitectura modular permite cambiar spaCy por Stanza, o BETO por RoBERTa.

✅ **Lematización automática:** Captura variantes sin crear keywords duplicadas ("rechazada", "rechazó", "rechazo" → "rechazar").

✅ **Carga única:** Modelos se cargan una sola vez al inicio, no en cada consulta.

***

### Limitaciones Identificadas

⚠️ **Sin corrección ortográfica:** Errores de escritura producen keywords inválidas.

⚠️ **Latencia BETO en CPU:** 1 segundo puede ser perceptible para usuarios (aunque aceptable).

⚠️ **Sin detección de sarcasmo/ironía:** "¡Genial, otra vez falla!" → alegría (incorrecto).

⚠️ **Modelo BETO no captura contexto conversacional:** Cada mensaje es independiente.

⚠️ **Sin manejo de emojis:** "😠" no es reconocido como enojo por spaCy.

⚠️ **Consultas muy cortas:** "Ayuda" o "Hola" tienen pocas keywords (bajo contexto).

***

## Mejoras Futuras

### 1. Corrección ortográfica automática

```python
from autocorrect import Speller

spell = Speller(lang='es')

def detect_keywords_con_correccion(text):
    """Corrige ortografía antes de extraer keywords."""
    text_corregido = spell(text)
    return detect_keywords(text_corregido)

# Ejemplo
detect_keywords_con_correccion("Mi tarjta fue rechazda")
# Returns: ["tarjeta", "rechazar"]  ← Corregidas automáticamente
```

**Impacto:** Aumenta robustez ante typos de usuarios reales.

***

### 2. Detección de emojis

```python
import emoji

def extract_emojis(text):
    """Extrae emojis del texto."""
    return [c for c in text if c in emoji.EMOJI_DATA]

def detect_emotion_con_emojis(text):
    """Detecta emoción considerando emojis."""
    emojis = extract_emojis(text)
    
    # Mapeo simple de emojis a emociones
    emoji_to_emotion = {
        "😠": "enojo", "😡": "enojo", "🤬": "enojo",
        "😊": "alegría", "😃": "alegría", "🎉": "alegría",
        "😢": "tristeza", "😭": "tristeza",
        "😨": "miedo", "😰": "miedo"
    }
    
    for e in emojis:
        if e in emoji_to_emotion:
            return emoji_to_emotion[e], 1.0  # Confianza máxima
    
    # Fallback a BETO si no hay emojis
    return detect_emotion(text)
```

**Impacto:** Captura emociones expresadas visualmente.

***

### 3. Optimización de BETO con ONNX

```python
from optimum.onnxruntime import ORTModelForSequenceClassification

# Convertir modelo PyTorch a ONNX (una sola vez)
ort_model = ORTModelForSequenceClassification.from_pretrained(
    model_id,
    export=True
)
ort_model.save_pretrained("beto_onnx")

# Cargar versión optimizada
emo_model_optimized = ORTModelForSequenceClassification.from_pretrained("beto_onnx")

# Inferencia 2-3x más rápida
```

**Impacto:** Reduce latencia de 1065 ms → ~400 ms en CPU.

***

### 4. Cache de emociones por hash de texto
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=500)
def detect_emotion_cached(text_hash):
    """Buscar en caché primero."""
    # ... (implementación real con modelo)
    pass

def detect_emotion(text):
    """Versión con caché."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return detect_emotion_cached(text_hash)
```

**Impacto:** Consultas repetidas tienen latencia ~1 ms (vs 1065 ms).

***

### 5. Modelo más ligero para emociones (DistilBETO)

```python
# Modelo alternativo más rápido
model_id = "dccuchile/distilbert-base-spanish-uncased"  # DistilBETO

# 40% más rápido, 60% del tamaño, 97% del rendimiento
```

**Impacto:** Reduce latencia manteniendo precisión aceptable.

***

### 6. Extracción de entidades nombradas (NER)

```python
def detect_entities(text):
    """
    Extrae entidades nombradas usando spaCy.
    """
    doc = nlp(text)
    
    entities = {
        "personas": [ent.text for ent in doc.ents if ent.label_ == "PER"],
        "organizaciones": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
        "lugares": [ent.text for ent in doc.ents if ent.label_ == "LOC"],
        "fechas": [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    }
    
    return entities

# Ejemplo
text = "Contraté a Juan Pérez para el evento del 15 de noviembre en Mendoza"
entities = detect_entities(text)
# {
#   "personas": ["Juan Pérez"],
#   "lugares": ["Mendoza"],
#   "fechas": ["15 de noviembre"]
# }
```

**Impacto:** Captura contexto adicional para personalización.

***

## Resumen Técnico

| Aspecto | Valor | Observación |
| :-- | :-- | :-- |
| **Keywords extraídas** | 2-5 por consulta | Depende de longitud del texto |
| **Precisión keywords** | 100% | En casos sin errores ortográficos |
| **Emociones detectadas** | 6 clases | F1-score 0.80 promedio |
| **Latencia spaCy** | 81 ms | Muy eficiente |
| **Latencia BETO (CPU)** | 1065 ms | Dominante en Módulo 7 |
| **Latencia BETO (GPU)** | 85 ms | 12.5x más rápido |
| **% del tiempo total** | 14% | 1.15 seg de ~8 seg totales |
| **Modelo spaCy usado** | `es_core_news_md` | 40 MB (actualizado vs doc original) |
| **Modelo BETO** | BETO-TASS-2025-II | Fine-tuned en español |
| **Escalabilidad** | Alta | Modelos se cargan una sola vez |


***

## Arquitectura de Integración

```
┌────────────────────────────────────────────────────────┐
│                    MÓDULO 7: NLP                       │
│              (spaCy + BETO Transformer)                │
└────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │   load_nlp_models()       │
              │   (Startup - una vez)     │
              └─────────────┬─────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐      ┌───────▼───────┐   ┌──────▼──────┐
   │  nlp    │      │  tokenizer    │   │  emo_model  │
   │ (spaCy) │      │    (BERT)     │   │   (BETO)    │
   │ 40 MB   │      │   Tokenizer   │   │  Fine-tuned │
   └────┬────┘      └───────┬───────┘   └──────┬──────┘
        │                   │                   │
        │                   └───────┬───────────┘
        │                           │
        │                           │
┌───────▼────────────┐    ┌─────────▼──────────────┐
│ detect_keywords()  │    │  detect_emotion()      │
│ @medir_tiempo      │    │  @medir_tiempo         │
└───────┬────────────┘    └─────────┬──────────────┘
        │                           │
        │ keywords: list            │ (emocion, score): tuple
        │ ["tarjeta",               │ ("enojo", 0.87)
        │  "rechazar"]              │
        │ time: 0.081s              │ time: 1.080s
        │                           │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Módulo 5:            │
        │  Planificador         │
        │  Dinámico             │
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
   ┌────▼─────┐         ┌──────▼──────┐
   │ Módulo 3 │         │  Módulo 4   │
   │  Fuzzy   │         │   Neo4j     │
   └────┬─────┘         └──────┬──────┘
        │                      │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    Módulo 8: LLM     │
        │  (usa emoción para   │
        │   adaptar tono)      │
        └──────────────────────┘
```


***

## Diferencias clave con Documentación Original

| Aspecto | Doc. Original | Implementación Real |
| :-- | :-- | :-- |
| **Modelo spaCy** | `es_core_news_sm` (12 MB) | ✅ **`es_core_news_md`** (40 MB) |
| **Función keywords** | `detect_keywords()` | ✅ Igual |
| **Función emoción** | `detect_emotion()` | ✅ Igual |
| **Decorador timing** | `@medir_tiempo` | ✅ Implementado |
| **Retorno con timing** | Documentado | ✅ `(resultado, duracion)` |
| **Carga de modelos** | `load_nlp_models()` | ✅ Implementado |
| **Token HuggingFace** | Variable de entorno | ✅ `HUGGINGFACE_HUB_TOKEN` |
| **Mapeo emociones** | `emotion_id2label` | ✅ Dict con 6 emociones |
| **Integración LLM** | `EMOTION_TO_TONE` | ✅ Dict de mapeo a tonos |
| **Latencia keywords** | ~100 ms | ✅ 81 ms (más rápido) |
| **Latencia BETO** | ~700 ms | ✅ 1080 ms (dato real actualizado) |
| **Accuracy sentimiento** | 90% | ✅ Confirmado (18/20 casos) |


***

## Conclusión

El **Módulo 7: Integración NLP** es la **puerta de entrada del sistema**, transformando consultas en lenguaje natural en datos estructurados procesables:

### ✅ Valor del módulo:

1. **Keywords precisas:** spaCy extrae palabras clave lematizadas con 100% de precisión en casos sin errores ortográficos.
2. **Emoción contextual:** BETO detecta emociones con 90% de accuracy, permitiendo adaptar el tono de las respuestas del LLM.
3. **Eficiencia en keywords:** spaCy es extremadamente rápido (81 ms), sin cuello de botella.
4. **Modelos robustos:** Ambos modelos están pre-entrenados y no requieren entrenamiento adicional.
5. **Integración crítica:** Alimenta a todos los módulos subsiguientes (Planificador, Fuzzy, Neo4j, LLM).

### ⚠️ Limitaciones conocidas:

- BETO es el cuello de botella (1080 ms en CPU)
- Sin corrección ortográfica automática
- Sin detección de sarcasmo/ironía
- Consultas muy cortas tienen poco contexto


### 🎯 Rol en la arquitectura:

El Módulo 7 actúa como **preprocesador universal** que:

- Normaliza el lenguaje natural a features estructuradas
- Proporciona contexto emocional para personalización
- Habilita la búsqueda semántica en Neo4j
- Permite decisiones inteligentes en el planificador

**Sin este módulo, el sistema no podría procesar lenguaje natural** y sería limitado a comandos estructurados.

***

**Última actualización:** 2025-11-17
**Versión:** 2.0 
**Estado:** ✅ Implementado y funcional con `es_core_news_md` + BETO-TASS-2025-II

***