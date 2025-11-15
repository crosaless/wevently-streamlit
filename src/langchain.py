# filepath: wevently-streamlit/src/langchain.py

import streamlit as st
import spacy
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langchain_neo4j import Neo4jGraph
from langchain_ollama import OllamaLLM
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import os
from dotenv import load_dotenv
load_dotenv()

# --------- 2. Configuración del modelo cloud Ollama ---------
# Read Ollama API key from environment instead of hardcoding it here.
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
if OLLAMA_API_KEY:
    os.environ['OLLAMA_API_KEY'] = OLLAMA_API_KEY
else:
    # Do not crash on missing key; warn the user in Streamlit UI.
    try:
        st.warning('No se encontró OLLAMA_API_KEY en las variables de entorno. Ollama LLM puede fallar si requiere autenticación.')
    except Exception:
        # If Streamlit UI isn't available yet, silently continue.
        pass


# ---------- 1. Configuración modelos NLP y dependencias ----------
# We'll load heavy HF models lazily so Streamlit can start even if auth fails.
nlp = None
tokenizer = None
emo_model = None


@st.cache_resource
def load_nlp_models():
    # Use the selected Hugging Face model and pass the HF token from .env
    model_id = "raulgdp/Analisis-sentimientos-BETO-TASS-2025-II"
    hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN", None)

    # Load spaCy Spanish model first (lighter) and HF tokenizer/model using token if present
    nlp_local = spacy.load("es_core_news_sm")
    tokenizer_local = AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_token)
    model_local = AutoModelForSequenceClassification.from_pretrained(model_id, use_auth_token=hf_token)
    return nlp_local, tokenizer_local, model_local


def _ensure_models():
    """Ensure NLP and HF models are loaded. If loading from Hugging Face fails
    (e.g. private/gated repo or missing token), we keep a graceful fallback.
    """
    global nlp, tokenizer, emo_model
    if nlp is not None and tokenizer is not None and emo_model is not None:
        return
    try:
        nlp, tokenizer, emo_model = load_nlp_models()
    except Exception as e:
        # Don't crash Streamlit — show a warning and fallback to lighter behavior.
        try:
            if nlp is None:
                nlp = spacy.load("es_core_news_sm")
        except Exception:
            nlp = None
        tokenizer = None
        emo_model = None
        st.warning("No se pudieron cargar los modelos de Hugging Face. El análisis de emoción usará un fallback simple.\n" + str(e))

# ---------- 2. Configuración Neo4j y Ollama LLM ----------
@st.cache_resource
def get_graph_llm():
    graph = Neo4jGraph(
        url="bolt://localhost:7687",
        username="neo4j",
        password="admin1234"
    )
    llm = OllamaLLM(
        model="gpt-oss:20b-cloud", 
        base_url="https://ollama.com"
    )
    return graph, llm
graph, llm = get_graph_llm()

# ---------- 3. Sentiment analysis BETO/RoBERTuito----------
emotion_id2label = {0: "alegría", 1: "enojo", 2: "asco", 3: "miedo", 4: "tristeza", 5: "sorpresa"}
def detect_emotion(text):
    # Ensure models are loaded; if HF model isn't available use a simple fallback
    _ensure_models()
    if emo_model is None or tokenizer is None:
        txt = text.lower()
        # Simple keyword heuristics as fallback
        if any(w in txt for w in ["feliz", "gracias", "genial", "bien", "excelente"]):
            return "alegría", 0.8
        if any(w in txt for w in ["irrit", "molest", "enojo", "enoj", "rabia", "no funciona", "fallo", "error"]):
            return "enojo", 0.6
        if any(w in txt for w in ["triste", "deprim", "llor", "lament"]):
            return "tristeza", 0.6
        return "neutral", 0.0
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        logits = emo_model(**inputs).logits
    scores = torch.softmax(logits, dim=-1).detach().cpu().numpy()[0]
    emo_idx = int(np.argmax(scores))
    emo = emotion_id2label[emo_idx]
    return emo, float(scores[emo_idx])

# ---------- 4. Detección de keywords ----------
def detect_keywords(text):
    # Ensure spaCy is loaded; if not, use a lightweight fallback tokenizer.
    _ensure_models()
    if nlp is None:
        import re
        txt = text.lower()
        # quick word extraction (basic, handles accents and ñ)
        words = re.findall(r"\b[áéíóúüñA-Za-z0-9]+\b", txt)
        stopwords = {
            'y','o','el','la','los','las','un','una','unos','unas','de','del','que','en',
            'por','para','con','sin','se','es','esta','está','al','como','su','sus','le',
            'les','lo','me','te','mi','tu','si','no','pero','porque','cuando','donde',
            'a','ante','bajo','contra','sobre','tras','entre','hasta','desde','durante'
        }
        keywords = [w for w in words if w.isalpha() and len(w) > 2 and w not in stopwords]
        return keywords
    doc = nlp(text)
    keywords = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]
    return keywords

# ---------- 5. Fuzzy logic para categoría y confianza ----------
def fuzzy_problem_categorization(keywords):
    # Variables de entrada y output
    matched = len(keywords)  # keywords detectadas relevantes (input a difusa)
    # Fuzzificación
    kw_input = ctrl.Antecedent(np.arange(0, 6, 1), 'num_keywords')
    conf_output = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'confianza')

    kw_input['bajo'] = fuzz.trimf(kw_input.universe, [0, 0, 2])
    kw_input['medio'] = fuzz.trimf(kw_input.universe, [1, 3, 5])
    kw_input['alto'] = fuzz.trimf(kw_input.universe, [3, 5, 5])

    conf_output['baja'] = fuzz.trimf(conf_output.universe, [0, 0, 0.7])
    conf_output['alta'] = fuzz.trimf(conf_output.universe, [0.6, 1, 1])

    rule1 = ctrl.Rule(kw_input['bajo'], conf_output['baja'])
    rule2 = ctrl.Rule(kw_input['medio'], conf_output['baja'])
    rule3 = ctrl.Rule(kw_input['alto'], conf_output['alta'])

    confianza_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    confianza_sim = ctrl.ControlSystemSimulation(confianza_ctrl)

    confianza_sim.input['num_keywords'] = matched
    confianza_sim.compute()
    return float(confianza_sim.output['confianza'])

# ---------- 6. Cypher query con categoría problemática ----------
def cypher_query(keywords, tipo_usuario):
    kwstr = "[" + ", ".join([f"'{k}'" for k in keywords]) + "]"
    return f"""
    MATCH (c:CategoriaProblema)-[:DISPARA]-(k:PalabraClave)
    WHERE k.nombre IN {kwstr}
    MATCH (c)-[:AGRUPA]->(t:TipoProblema)-[:RESUELTO_POR]->(s:Solucion)
    MATCH (c)-[:TIENE_UN]->(tu:TipoUsuario {{nombre:'{tipo_usuario}'}})
    RETURN DISTINCT
        t.nombre AS tipo_problema,
        s.accion AS solucion,
        c.confianzaDecision AS confianza
    ORDER BY confianza DESC
    LIMIT 1
    """

# ---------- 7. Lógica de generación de respuesta por rol ----------
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

def generar_respuesta_streamlit(pregunta, tipo_usuario='Prestador'):
    keywords = detect_keywords(pregunta)
    emocion, emo_score = detect_emotion(pregunta)
    confianza = fuzzy_problem_categorization(keywords)
    cypher = cypher_query(keywords, tipo_usuario)
    result = graph.query(cypher)
    if not result or confianza < 0.7:
        tipo_problema, solucion, postdata = "No definido", "No definida", "No se encontró solución automática, te derivaremos a soporte. (soporte@wevently.com)"
    else:
        r = result[0]
        tipo_problema = r['tipo_problema']
        solucion = r['solucion']
        postdata = "Respuesta recomendada por nuestro sistema."

    rd = role_details.get(tipo_usuario, role_details["Prestador"])

    prompt_llm = (
        f"{rd['saludo']}Se detectó el problema: {tipo_problema}. "
        f"Solución sugerida: {solucion}. "
        f"Tono: {rd['tono']}, {emocion} (confianza análisis: {confianza:.2f}/{emo_score:.2f}). "
        f"Mensaje original: {pregunta}\n"
        f"{rd['extra']}\n{postdata}"
    )
    respuesta = llm.invoke(prompt_llm)
    return respuesta, keywords, emocion, confianza