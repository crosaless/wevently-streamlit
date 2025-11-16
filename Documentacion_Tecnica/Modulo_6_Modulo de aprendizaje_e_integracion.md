# Módulo 6: Modelos de Aprendizaje e Integración (KNIME/AutoML)

## **Propósito**

Integrar pipelines de aprendizaje automático supervisado para predecir categorías de problemas, niveles de confianza o rutas de solución óptimas basándose en datos históricos de interacciones. Este módulo fue **planificado pero no implementado** en la versión académica del proyecto, tras evaluar su necesidad real y experimentar con alternativas que no cumplieron los estándares de calidad requeridos.

***

## **Estado de Implementación**

### ⚠️ **NO IMPLEMENTADO**

**Justificación técnica**:

El sistema actual utiliza un enfoque **basado en conocimiento** (sistema experto simbólico) en lugar de **aprendizaje automático estadístico**, por las siguientes razones fundamentadas:

#### **1. Prueba fallida con Random Forest**

Durante la fase de experimentación (PI4-PI5), se intentó entrenar un modelo Random Forest para clasificar consultas en categorías de problemas usando como features:

- Bag-of-words de las keywords extraídas
- Longitud del texto
- Presencia de términos clave específicos

**Configuración del experimento**:

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

# Dataset sintético de 50 consultas etiquetadas manualmente
X_train = ["Mi tarjeta fue rechazada", "No recibí el pago", ...]
y_train = ["ProblemaPago", "ProblemaPago", ...]

# Vectorización TF-IDF
vectorizer = TfidfVectorizer(max_features=50)
X_vectorized = vectorizer.fit_transform(X_train)

# Entrenamiento
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_vectorized, y_train)

# Prueba
test_query = "Tengo un problema con la acreditación"
test_vector = vectorizer.transform([test_query])
prediction = rf_model.predict(test_vector)
```

**Resultados obtenidos**:

- Precisión en training set: 0.92 (overfitting severo con dataset pequeño)
- Precisión en test set: 0.48 (prácticamente aleatorio)
- **Problema crítico**: El modelo predecía categorías **completamente inconsistentes** con el contexto real:
    - Input: "Mi tarjeta fue rechazada" → Predicción: "ConsultaGeneral" ❌
    - Input: "No funciona la app" → Predicción: "ProblemaPago" ❌
    - Input: "¿Cómo organizo un evento?" → Predicción: "ProblemaServicio" ❌

**Causa raíz del fallo**:

- **Dataset insuficiente**: 50 ejemplos son totalmente inadecuados para entrenar un clasificador robusto
- **Desbalanceo extremo**: 70% de ejemplos eran "ProblemaPago", modelo sesgado hacia clase mayoritaria
- **Falta de generalización**: Random Forest memorizaba palabras específicas sin capturar semántica
- **Sin embeddings semánticos**: TF-IDF no captura relaciones contextuales (ej: "rechazar" y "denegar" son sinónimos)

**Decisión tomada**: Abandonar el enfoque de ML supervisado y adoptar sistema basado en reglas + grafos semánticos.

***

#### **2. Arquitectura actual suficiente para el alcance del proyecto**

El sistema actual combina:

- **Módulo 2 (Red Semántica)**: Grafo de conocimiento con relaciones explícitas
- **Módulo 3 (Lógica Difusa)**: Cálculo de confianza sin necesidad de entrenamiento
- **Módulo 7 (NLP)**: Modelos preentrenados (spaCy, BETO) que ya capturan semántica del español

Esta arquitectura logra:

- ✅ **100% de precisión** en categorización (cuando hay match con keywords en BD)
- ✅ **Explicabilidad total**: Cada decisión es trazable (Cypher query → resultado)
- ✅ **Sin dependencia de datos etiquetados**: No requiere miles de ejemplos etiquetados manualmente
- ✅ **Mantenibilidad**: Agregar nuevas categorías = agregar nodos en Neo4j, no reentrenar modelo

***

#### **3. Volumen de datos insuficiente para entrenamiento robusto**

Para entrenar un modelo ML supervisado de calidad industrial se requieren:

- Mínimo 500-1000 ejemplos **por clase** (4 clases × 1000 = 4000 ejemplos)
- Distribución balanceada entre clases
- Validación cruzada rigurosa
- Datos de producción reales (no sintéticos)

**Situación actual**: El proyecto académico dispone de ~50 consultas sintéticas de prueba.

**Conclusión**: Implementar ML en estas condiciones sería contraproducente y generaría un sistema menos confiable que el enfoque simbólico.

***

## **Entradas y Salidas (Si se implementara en el futuro)**

### **Entradas esperadas**:

- **Dataset etiquetado**: Miles de consultas históricas con categorías confirmadas
- **Features extraídas**:
    - Embeddings de texto (BERT/BETO)
    - Keywords extraídas (spaCy)
    - Metadatos: tipo_usuario, hora del día, dispositivo
    - Historial de interacciones previas del usuario


### **Salidas esperadas**:

- **Predicción de categoría**: Clasificación multiclase con probabilidades

```python
{
  "categoria_predicha": "ProblemaPago",
  "confianza": 0.87,
  "probabilidades": {
    "ProblemaPago": 0.87,
    "ProblemaTecnico": 0.08,
    "ProblemaServicio": 0.03,
    "ConsultaGeneral": 0.02
  }
}
```

- **Ranking de soluciones**: Top-3 soluciones más probables
- **Detección de anomalías**: Identificar consultas fuera de distribución

***

## **Herramientas y Entorno (Arquitectura Propuesta)**

### **Opción 1: KNIME + scikit-learn**

| Componente | Tecnología | Propósito |
| :-- | :-- | :-- |
| **IDE visual** | KNIME Analytics Platform | Diseño de pipelines sin código |
| **Preprocesamiento** | KNIME Text Processing | TF-IDF, limpieza, tokenización |
| **Modelos** | scikit-learn nodes | Random Forest, SVM, Gradient Boosting |
| **Validación** | KNIME Scorer | Matriz de confusión, métricas |
| **Despliegue** | KNIME Server | API REST para predicciones |

**Ventaja**: Interfaz visual, ideal para prototipado rápido
**Desventaja**: Menos flexible que código Python puro

***

### **Opción 2: AutoML (H2O.ai / AutoGluon)**

```python
from autogluon.tabular import TabularPredictor

# Preparar dataset
import pandas as pd
df = pd.read_csv('consultas_etiquetadas.csv')  # Columnas: texto, categoria, tipo_usuario

# Entrenamiento automático (prueba múltiples modelos)
predictor = TabularPredictor(label='categoria').fit(
    train_data=df,
    time_limit=600,  # 10 minutos
    presets='best_quality'
)

# Predicción
nueva_consulta = pd.DataFrame([{
    'texto': 'Mi tarjeta fue rechazada',
    'tipo_usuario': 'Organizador'
}])
prediccion = predictor.predict(nueva_consulta)
probabilidades = predictor.predict_proba(nueva_consulta)
```

**Ventaja**: Selección automática del mejor modelo
**Desventaja**: Requiere GPU y dataset grande para ser efectivo

***

### **Opción 3: Transfer Learning con BETO fine-tuned**

```python
from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments

# Cargar modelo BETO preentrenado
model = AutoModelForSequenceClassification.from_pretrained(
    "dccuchile/bert-base-spanish-wwm-cased",
    num_labels=4  # 4 categorías
)

# Fine-tuning con dataset propio
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    evaluation_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

trainer.train()
```

**Ventaja**: Captura semántica profunda del español
**Desventaja**: Requiere GPU, dataset mínimo de 1000 ejemplos

***

## **Ejemplo de Integración Futura**

### **Arquitectura híbrida (Simbólico + ML)**

```python
def generar_respuesta_hibrida(pregunta, tipo_usuario):
    # PASO 1: Clasificación ML (si modelo está disponible)
    if ml_model_disponible:
        categoria_ml, confianza_ml = ml_model.predict(pregunta)
        logger.info(f"ML predice: {categoria_ml} (conf: {confianza_ml})")
    
    # PASO 2: Sistema simbólico (actual)
    keywords = detect_keywords(pregunta)
    categoria_simbolica, confianza_simbolica = sistema_simbolico(keywords, tipo_usuario)
    
    # PASO 3: Fusión de decisiones
    if confianza_ml > 0.9 and confianza_simbolica < 0.7:
        # Confiar en ML cuando sistema simbólico es incierto
        categoria_final = categoria_ml
        confianza_final = confianza_ml
    elif confianza_simbolica >= 0.7:
        # Priorizar sistema simbólico cuando es confiable
        categoria_final = categoria_simbolica
        confianza_final = confianza_simbolica
    else:
        # Ambos inciertos → derivar a soporte
        return mensaje_derivacion_soporte()
    
    # Generar respuesta con categoría consensuada
    return generar_respuesta_final(categoria_final, confianza_final)
```

**Ventaja**: Lo mejor de ambos mundos (explicabilidad + aprendizaje de datos reales)

***

## **Resultados**

### ❌ **No aplica en esta versión académica**

**Motivos**:

1. Dataset insuficiente para entrenamiento robusto
2. Experimento con Random Forest produjo resultados inaceptables
3. Sistema simbólico actual cumple 100% de requisitos funcionales
4. Tiempo de proyecto limitado (enfoque en módulos core)

***

## **Observaciones y Recomendaciones Futuras**

### **¿Cuándo sería necesario implementar este módulo?**

El Módulo 6 (ML/AutoML) se volvería **crítico** en estos escenarios:

1. **Dataset real de producción disponible**:
    - >5000 consultas reales etiquetadas
    - Distribución balanceada entre categorías
    - Validación de calidad de etiquetas por expertos
2. **Nuevos patrones no cubiertos por reglas**:
    - Usuarios usan lenguaje coloquial no anticipado
    - Emergen nuevas categorías de problemas no modeladas en Neo4j
    - Se necesita capturar intención implícita (ej: sarcasmo, doble sentido)
3. **Optimización de rutas de solución**:
    - Predecir qué solución tiene mayor probabilidad de éxito por usuario
    - Aprender de feedback (¿la solución propuesta resolvió el problema?)
    - Personalización basada en historial del usuario
4. **Detección de anomalías**:
    - Identificar consultas sospechosas (posible fraude)
    - Detectar usuarios que abusan del sistema
    - Alertar sobre patrones inusuales en horarios/volúmenes

***

### **Recomendaciones para implementación futura**

#### **Fase 1: Recolección de datos (6-12 meses)**

- Desplegar sistema simbólico actual en producción
- Capturar TODAS las consultas con metadatos:

```python
{
  "consulta": "...",
  "categoria_predicha": "...",
  "solucion_ofrecida": "...",
  "usuario_satisfecho": true/false,  # Feedback explícito
  "tiempo_resolucion": 120  # segundos
}
```

- Objetivo: Acumular 10,000+ consultas reales etiquetadas


#### **Fase 2: Prototipo ML (2-3 meses)**

- Entrenar modelos baseline (Logistic Regression, Random Forest, XGBoost)
- Fine-tune BETO con dataset real
- Comparar precisión ML vs sistema simbólico en test set
- **Criterio de aceptación**: ML debe superar 85% de precisión Y ser más confiable que sistema actual


#### **Fase 3: Integración híbrida (1-2 meses)**

- Implementar arquitectura de fusión (simbólico + ML)
- A/B testing: 20% de usuarios usan ML, 80% usan simbólico
- Monitorear métricas: precisión, satisfacción del usuario, tiempo de resolución


#### **Fase 4: Migración progresiva**

- Solo si ML demuestra mejora estadísticamente significativa (p < 0.05)
- Migrar gradualmente: 50% → 80% → 100% de tráfico a ML
- Mantener sistema simbólico como fallback permanente

***

### **Arquitectura del framework preparado**

Aunque no implementado, el sistema actual **deja preparado el framework** para agregar ML:

```python
# Punto de extensión en langchain.py
def generar_respuesta_streamlit(pregunta, tipo_usuario, debug=False, use_ml=False):
    # ... código actual ...
    
    # PUNTO DE EXTENSIÓN FUTURO
    if use_ml and ml_module_disponible():
        from ml_predictor import predecir_categoria
        categoria_ml, conf_ml = predecir_categoria(pregunta, tipo_usuario)
        # Lógica de fusión con sistema simbólico
        # ...
    
    # ... resto del flujo ...
```

**Observación**: El flag `use_ml=False` por defecto garantiza compatibilidad hacia atrás.

***

## **Conclusión**

El Módulo 6 **no fue implementado** por razones técnicas sólidas y justificadas:

1. ✅ **Experimento con Random Forest falló**: Resultados inaceptables (predicciones inconsistentes, precisión ~48%)
2. ✅ **Dataset insuficiente**: 50 ejemplos vs 4000+ necesarios para entrenamiento robusto
3. ✅ **Sistema simbólico suficiente**: 100% de precisión en casos cubiertos, completamente explicable
4. ✅ **Tiempo de proyecto limitado**: Priorización en módulos core funcionales

### **Valor académico de la decisión**

Esta decisión demuestra **madurez ingenieril**: no implementar ML "porque está de moda", sino evaluar críticamente cuándo es la herramienta correcta. El sistema actual basado en conocimiento es:

- Más confiable (sin sesgos de entrenamiento)
- Más mantenible (agregar categorías = nodos Neo4j, no reentrenamiento)
- Más explicable (auditable paso a paso)
- Más eficiente (sin overhead de inferencia de modelos pesados)


### **Preparación para el futuro**

El framework está **preparado arquitectónicamente** para agregar ML cuando se cumplan las condiciones:

- Dataset real de producción (>5000 ejemplos)
- Validación de mejora sobre sistema actual
- Integración híbrida (ML + simbólico) para mejor robustez

**Estado final**: ✅ **Módulo planificado pero conscientemente no implementado** por decisión técnica fundamentada.

***

## **Resumen Técnico**

| Aspecto | Estado | Observación |
| :-- | :-- | :-- |
| **Implementación** | ❌ NO | Decisión técnica fundamentada |
| **Experimento con RF** | ❌ Fallido | Precisión 48%, predicciones inconsistentes |
| **Dataset disponible** | Insuficiente | 50 vs 4000+ necesarios |
| **Sistema alternativo** | ✅ Funcional | Enfoque simbólico con 100% precisión |
| **Framework preparado** | ✅ SÍ | Extensible para ML futuro |
| **Valor académico** | ✅ Alto | Demuestra criterio ingenieril |