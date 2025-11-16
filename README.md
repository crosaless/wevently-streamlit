# Wevently - Asistente Inteligente para Consultas de Pagos y Generales

<div align="center">

![Wevently](https://img.shields.io/badge/Wevently-IA%202025-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9%2B-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

**Proyecto Integrador IA 2025 – Grupo 13 (UTN FRM)**  
*Comisión 5K10 – Ciclo 2025*

[📖 Documentación](#-documentación-técnica) • [🚀 Instalación](#-instalación-y-configuración) • [💬 Uso](#-uso-del-sistema) • [🧪 Pruebas](#-pruebas-y-validación)

</div>

---

## 📖 Descripción General

Sistema experto **multimodal** basado en procesamiento de lenguaje natural, análisis de sentimientos, lógica difusa y base de datos en grafos, diseñado para proporcionar asistencia contextualizada a organizadores, prestadores de servicios y propietarios de lugares en la plataforma Wevently.

Implementa un chatbot inteligente que integra técnicas avanzadas de inteligencia artificial simbólica y conexionista para gestionar consultas relacionadas con eventos privados, transacciones de pago y operaciones de la plataforma.

### ✨ Características Principales

- ✅ **Análisis de sentimientos** con modelo BETO (8 emociones)
- ✅ **Extracción de palabras clave** mediante spaCy
- ✅ **Categorización difusa** de problemas (scikit-fuzzy)
- ✅ **Base de conocimiento** en Neo4j (grafos semánticos)
- ✅ **Generación de respuestas** con Ollama/LangChain
- ✅ **Interfaz interactiva** tipo WhatsApp en Streamlit
- ✅ **Logs y métricas** de rendimiento por módulo

---

## 🏗️ Estructura del Proyecto

```plaintext
wevently-streamlit/
├── src/
│   ├── streamlit_app.py                    # Interfaz principal
│   ├── langchain.py                        # Orquestación NLP y BD
│   └── neo4j_connection.py                 # Gestor de conexiones Neo4j
├── Documentacion_Tecnica/                  # 📁 Fichas técnicas
│   ├── INDICE_TECNICO.md                   # Índice general
│   ├── Modulo_1_Red_Procesos.md            # Red de procesos
│   ├── Modulo_2_Red_Semantica.md           # Modelo conceptual
│   ├── Modulo_3_Frames_Difusos.md          # Lógica difusa
│   ├── Modulo_4_Base_Grafos.md             # Neo4j y Cypher
│   ├── Modulo_5_Flujo_Planificacion.md     # Orquestación
│   ├── Modulo_6_Aprendizaje_Integracion.md # KNIME/AutoML
│   ├── Modulo_7_NLP_Integration.md         # spaCy, BETO
│   ├── Modulo_8_Generativo.md              # Ollama, LangChain
│   └── Modulo_9_API_Asistente.md           # API REST
├── tests/
│   └── test_app.py                         # Pruebas unitarias
├── .streamlit/
│   └── config.toml                         # Configuración Streamlit
├── .env                                    # Variables de entorno
├── .gitignore                              # Archivos excluidos
├── requirements.txt                        # Dependencias Python
├── pruebas_wevently.log                    # Registro de ejecuciones
├── resultados_pruebas.json                 # Métricas de pruebas
└── README.md                               # Este archivo
```

---

## 🧩 Arquitectura del Sistema

El asistente inteligente está compuesto por **9 módulos integrados** que trabajan secuencialmente para procesar consultas y generar respuestas:

<table>
<thead>
<tr>
<th align="center">#</th>
<th>Módulo</th>
<th>Descripción</th>
<th>Herramientas</th>
</tr>
</thead>
<tbody>
<tr>
<td align="center"><strong>1</strong></td>
<td>Red de Procesos</td>
<td>Define flujos de decisión y reglas de negocio</td>
<td>Diagramas, reglas lógicas</td>
</tr>
<tr>
<td align="center"><strong>2</strong></td>
<td>Red Semántica</td>
<td>Ontología del dominio: entidades y relaciones</td>
<td>Grafos conceptuales, RDF</td>
</tr>
<tr>
<td align="center"><strong>3</strong></td>
<td>Frames Difusos</td>
<td>Categorización probabilística</td>
<td>scikit-fuzzy, funciones membresía</td>
</tr>
<tr>
<td align="center"><strong>4</strong></td>
<td>Base Orientada a Grafos</td>
<td>Almacenamiento de conocimiento estructurado</td>
<td>Neo4j, Cypher, langchain_neo4j</td>
</tr>
<tr>
<td align="center"><strong>5</strong></td>
<td>Flujo de Planificación</td>
<td>Orquestación de módulos y scheduling</td>
<td>Decoradores, logging</td>
</tr>
<tr>
<td align="center"><strong>6</strong></td>
<td>Aprendizaje e Integración</td>
<td>Entrenamiento y evaluación de modelos</td>
<td>KNIME, AutoML, scikit-learn</td>
</tr>
<tr>
<td align="center"><strong>7</strong></td>
<td>Integración NLP</td>
<td>Procesamiento de texto y sentimientos</td>
<td>spaCy, transformers, BETO-TASS</td>
</tr>
<tr>
<td align="center"><strong>8</strong></td>
<td>Integración Generativa</td>
<td>Generación de respuestas contextualizadas</td>
<td>Ollama (gpt-oss:20b), LangChain</td>
</tr>
<tr>
<td align="center"><strong>9</strong></td>
<td>API del Asistente</td>
<td>Interfaz de usuario y endpoints</td>
<td>Streamlit, FastAPI (futuro)</td>
</tr>
</tbody>
</table>

📖 **[Ver fichas técnicas detalladas →](./Documentacion_Tecnica/INDICE_TECNICO.md)**

---

## 📚 Documentación Técnica

Cada módulo cuenta con una **ficha técnica completa** que incluye:

- ✅ Propósito del componente dentro del sistema
- ✅ Entradas y salidas esperadas (datos, formatos)
- ✅ Herramientas y entorno (dependencias, configuración)
- ✅ Código relevante o enlaces al repositorio
- ✅ Capturas y ejemplos de funcionamiento
- ✅ Resultados de pruebas (métricas, validación)
- ✅ Observaciones y sugerencias de mejora

| Recurso | Enlace |
|---------|--------|
| 📂 **Documentación Técnica** | [`Documentacion_Tecnica/`](./Documentacion_Tecnica/) |
| 📑 **Índice General** | [INDICE_TECNICO.md](./Documentacion_Tecnica/INDICE_TECNICO.md) |
| 📄 **Informe Ejecutivo** | [Google Docs](https://docs.google.com/document/d/1vE4u0X6DqhP2HihL0aKoJxm_wPohcHuP-SNYT1M-juk/edit) |

---

## 🚀 Instalación y Configuración

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/crosaless/wevently-streamlit.git
cd wevently-streamlit
```

### 2️⃣ Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

### 4️⃣ Configurar Variables de Entorno

Completa el archivo `.env` con tus credenciales:

```env
# Neo4j (Aura Cloud o local)
NEO4J_URI=neo4j+s://xxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=tu_contraseña_segura
NEO4J_URL=bolt://localhost:7687

# Ollama Cloud
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_API_KEY=tu_api_key_ollama

# HuggingFace (para modelo BETO)
HUGGINGFACE_HUB_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

### 5️⃣ Ejecutar la Aplicación

```bash
streamlit run src/streamlit_app.py
```

La aplicación estará disponible en **`http://localhost:8501`**

---

## 💬 Uso del Sistema

### Flujo de Interacción

1. **Selecciona tu rol**: Organizador, Prestador o Propietario
2. **Escribe tu consulta** en el campo de texto
3. **Recibe respuesta contextualizada** con:
   - Palabras clave detectadas (spaCy)
   - Emoción identificada (BETO)
   - Nivel de confianza (lógica difusa)
   - Solución recuperada de Neo4j
   - Respuesta generada por Ollama

### 📋 Ejemplo de Flujo Completo

<details>
<summary><b>👤 Usuario (Organizador):</b> "Mi tarjeta fue rechazada dos veces, ¿qué hago?"</summary>

```plaintext
🔄 Procesamiento del Sistema:
├─ [Módulo 7] Extrae keywords: ['tarjeta', 'rechazar', 'hacer']
├─ [Módulo 7] Detecta emoción: "enojo" (score: 0.82)
├─ [Módulo 3] Calcula confianza: 0.90 (lógica difusa)
├─ [Módulo 4] Consulta Neo4j → Categoría: "Demora en acreditación"
└─ [Módulo 8] Genera respuesta con tono serio y conciliador

🤖 Respuesta del Asistente:
"¡Hola estimado organizador! Entendemos tu frustración. Te recomendamos 
verificar que los datos de tu tarjeta estén actualizados y reintentar. 
Si el problema persiste, contacta a soporte (weventlyempresa@gmail.com) 
con el número de transacción."
```

</details>

---

## 🧪 Pruebas y Validación

### Ejecutar Tests Unitarios

```bash
pytest tests/test_app.py -v
```

### Archivos de Resultados

- **`pruebas_wevently.log`**: Registro detallado de ejecuciones con timestamps
- **`resultados_pruebas.json`**: Métricas de desempeño por módulo

### 📊 Métricas Típicas Observadas

| Métrica | Valor | Descripción |
|---------|-------|-------------|
| ⏱️ **Latencia Total** | 3-8 seg | 90% dominada por LLM |
| 🎯 **Precisión Keywords** | Alta | spaCy es_core_news_sm |
| 😊 **F1-score Emociones** | 0.78-0.85 | Modelo BETO |
| 🔍 **Confianza Promedio** | 0.70-0.95 | Lógica difusa |

---

## 📦 Dependencias Principales

<table>
<thead>
<tr>
<th>Categoría</th>
<th>Paquete</th>
<th>Versión</th>
<th>Propósito</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Interfaz</strong></td>
<td><code>streamlit</code></td>
<td>≥1.28.0</td>
<td>Frontend web interactivo</td>
</tr>
<tr>
<td><strong>NLP</strong></td>
<td><code>spacy</code></td>
<td>≥3.6.0</td>
<td>Tokenización y extracción</td>
</tr>
<tr>
<td><strong>NLP</strong></td>
<td><code>transformers</code></td>
<td>≥4.35.0</td>
<td>Modelos BETO</td>
</tr>
<tr>
<td><strong>BD Grafos</strong></td>
<td><code>neo4j</code></td>
<td>≥5.14.0</td>
<td>Cliente Neo4j oficial</td>
</tr>
<tr>
<td><strong>BD Grafos</strong></td>
<td><code>langchain-neo4j</code></td>
<td>≥0.0.3</td>
<td>Integración LangChain-Neo4j</td>
</tr>
<tr>
<td><strong>LLM</strong></td>
<td><code>langchain-ollama</code></td>
<td>≥0.1.0</td>
<td>Integración Ollama Cloud</td>
</tr>
<tr>
<td><strong>Lógica Difusa</strong></td>
<td><code>scikit-fuzzy</code></td>
<td>≥0.4.2</td>
<td>Sistema de inferencia</td>
</tr>
<tr>
<td><strong>ML</strong></td>
<td><code>torch</code></td>
<td>≥2.1.0</td>
<td>Backend transformer</td>
</tr>
<tr>
<td><strong>Utilidades</strong></td>
<td><code>python-dotenv</code></td>
<td>≥1.0.0</td>
<td>Variables de entorno</td>
</tr>
</tbody>
</table>

📋 **[Ver lista completa →](./requirements.txt)**

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para colaborar:

1. **Fork** el repositorio
2. Crea una rama: `git checkout -b feature/mi-mejora`
3. Haz commit: `git commit -m "Agrega mi mejora"`
4. Push: `git push origin feature/mi-mejora`
5. Abre un **Pull Request**

### 🎯 Áreas de Mejora Prioritarias

- [ ] Gestión de contexto conversacional (memoria de chat)
- [ ] Despliegue local de LLM (Llama 2, Mistral)
- [ ] Expansión de escenarios en base de conocimiento Neo4j
- [ ] API REST con FastAPI para integración con otros sistemas
- [ ] Tests de integración end-to-end

---

## 📄 Licencia

Este proyecto está bajo licencia **MIT**. Consulta el archivo [`LICENSE`](./LICENSE) para más detalles.

---

## 📞 Contacto y Soporte

| Recurso | Enlace |
|---------|--------|
| 📖 **Documentación Técnica** | [Documentacion_Tecnica/](./Documentacion_Tecnica/) |
| 📊 **Informe Ejecutivo** | [Google Docs](https://docs.google.com/document/d/1vE4u0X6DqhP2HihL0aKoJxm_wPohcHuP-SNYT1M-juk/edit) |
| 🐛 **Reportar Issues** | [GitHub Issues](https://github.com/crosaless/wevently-streamlit/issues) |
| 💬 **Contacto** | [@crosaless](https://github.com/crosaless) |

---

## 🎓 Contexto Académico

Este proyecto fue desarrollado como **Proyecto Integrador Final** de la materia **Inteligencia Artificial** de la carrera de Ingeniería en Sistemas de Información de la **Universidad Tecnológica Nacional - Facultad Regional Mendoza**, ciclo lectivo 2025.

**Grupo 13 - Comisión 5K10**

---

<div align="center">

**⭐ Si este proyecto te resultó útil, considera darle una estrella**

[⬆ Volver al inicio](#wevently---asistente-inteligente-para-consultas-de-pagos-y-generales)

</div>