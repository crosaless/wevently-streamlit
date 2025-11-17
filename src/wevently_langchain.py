import logging
import time
import json
from functools import wraps
from datetime import datetime
import spacy
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langchain_neo4j import Neo4jGraph
from langchain_ollama import OllamaLLM
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from neo4j_connection import get_graph
import os
import joblib

# --- Parámetros/paths para cargar modelo ML entrenado ---
MODEL_FOLDER = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_FOLDER, "mejor_modelo_RandomForest.joblib")
VECTORIZER_PATH = os.path.join(MODEL_FOLDER, "vectorizador_tfidf.joblib")
MODEL_METADATA_PATH = os.path.join(MODEL_FOLDER, "metadata.json")
modelo_rf = joblib.load(MODEL_PATH)
vectorizador_tfidf = joblib.load(VECTORIZER_PATH)
if os.path.exists(MODEL_METADATA_PATH):
    with open(MODEL_METADATA_PATH, "r") as f:
        METADATA = json.load(f)
        ML_CONFIDENCE_THRESHOLD = float(METADATA.get("umbral_ood", 0.1))
else:
    ML_CONFIDENCE_THRESHOLD = 0.1

# --- Palabras clave del dominio soporte ---
DOMAIN_KEYWORDS = {
    'pago','pagos','pagar','pagué','pague','acreditar','acredita','acreditación','acreditacion', 
    'calendario', 'no', 'anda', 'fallo', 'falló',
    'transferencia', 'transaccion', 'transacción', 'tarjeta', 'debito', 'débito', 'credito', 'crédito',
    'comision', 'comisión', 'comisiones', 'cobro', 'cobran', 'tarifa', 'devolución', 'devolucion',
    'rechazar', 'rechazo', 'rechazado', 'servicio', 'proveedor', 'prestador', 'reclamo',
    'cancelacion', 'cancelación', 'transacción', 'evento', 'eventos', 'rechazó', 'rechaza', 'reintentar'
}

# --- Logging global ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pruebas_wevently.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def medir_tiempo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        duracion = time.time() - inicio
        logger.info(f"{func.__name__} ejecutado en {duracion:.4f}s")
        return resultado, duracion
    return wrapper

# --- Modelos NLP y HuggingFace ---
def load_nlp_models():
    model_id = "raulgdp/Analisis-sentimientos-BETO-TASS-2025-II"
    hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN", None)
    # spaCy
    nlp_local = spacy.load("es_core_news_sm")
    # Transformer
    tokenizer_local = AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_token)
    model_local = AutoModelForSequenceClassification.from_pretrained(model_id, use_auth_token=hf_token)
    return nlp_local, tokenizer_local, model_local
nlp, tokenizer, emo_model = load_nlp_models()

# --- Neo4j y Ollama LLM ---
graph = get_graph()
llm = OllamaLLM(
    model="gpt-oss:20b-cloud",
    base_url="https://ollama.com"
)

# --- Emoción (BETO) ---
emotion_id2label = {0: "alegría", 1: "enojo", 2: "asco", 3: "miedo", 4: "tristeza", 5: "sorpresa"}
@medir_tiempo
def detect_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        logits = emo_model(**inputs).logits
    scores = torch.softmax(logits, dim=-1).detach().cpu().numpy()[0]
    emo_idx = int(np.argmax(scores))
    emo = emotion_id2label[emo_idx]
    return emo, float(scores[emo_idx])

# --- Keywords (spaCy) ---
@medir_tiempo
def detect_keywords(text):
    doc = nlp(text)
    keywords = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]
    return keywords

# --- Modelo ML predictivo ---
def clasificar_categoria_ml(texto):
    """
    Clasifica el mensaje usando el modelo ML y retorna categoria y confianza.
    Si la confianza < umbral, devuelve categoría NoRepresentaAlDominio.
    """
    vec = vectorizador_tfidf.transform([texto])
    proba = modelo_rf.predict_proba(vec)[0]
    categoria_predicha = modelo_rf.classes_[np.argmax(proba)]
    confianza = float(np.max(proba))
    if confianza < ML_CONFIDENCE_THRESHOLD:
        return "NoRepresentaAlDominio", confianza
    return categoria_predicha, confianza

# --- Planificador dinámico (PG3) ---
def planificar_flujo(pregunta, tipo_usuario, historial_sesion):
    categoria_ml, confianza_ml = clasificar_categoria_ml(pregunta)
    keywords, _ = detect_keywords(pregunta)
    kw_set = set(keywords)
    domain_match = kw_set.intersection(DOMAIN_KEYWORDS)

    plan = {
        "categoria_ml": categoria_ml,
        "confianza_ml": confianza_ml,
        "keywords": keywords,
        "ejecutar_flujo_completo": True,
        "justificacion": []
    }
    if categoria_ml == "NoRepresentaAlDominio":
        plan["ejecutar_flujo_completo"] = False
        plan["justificacion"].append(f"Categoría ML: NoRepresentaAlDominio o confianza baja {confianza_ml:.2f}. Fallback inmediato.")
        return plan
    if confianza_ml < ML_CONFIDENCE_THRESHOLD:
        plan["ejecutar_flujo_completo"] = False
        plan["justificacion"].append(f"Confianza ML ({confianza_ml:.2f}) < umbral ({ML_CONFIDENCE_THRESHOLD:.2f}). Fallback inmediato.")
        return plan
    if not domain_match:
        plan["ejecutar_flujo_completo"] = False
        plan["justificacion"].append(f"Sin keywords relevantes de dominio. Fallback.")
        return plan
    plan["justificacion"].append("Confianza ML suficiente y keywords relevantes en dominio. Ejecuto flujo completo.")
    return plan

# --- Lógica difusa ---
@medir_tiempo
def fuzzy_problem_categorization(keywords):
    matched = len(keywords)
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

# --- Cypher Query ---
def cypher_query(keywords, tipo_usuario):
    kw_list = [k.lower() for k in keywords]
    kwstr = "[" + ", ".join([f"'{k}'" for k in kw_list]) + "]"
    #a la consulta le saque el LIMIT 1 para obtener todas als respuestas
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
    """

def elegir_mejor_solucion_con_llm(user_message, all_results, categoria_ml, emocion, llm):
    if not all_results:
        return None, None, None, "No hay soluciones candidatas en la base de conocimiento."
    candidates_text = "\n".join([
        f"Opción {i+1}: Tipo={r.get('tipo_problema','')}, Solución={r.get('solucion','')}, "
        f"Confianza={r.get('confianza',0):.2f}, Keywords={r.get('matched_keywords','')}"
        for i, r in enumerate(all_results)
    ])

    selection_prompt = (
        f"Como capa intermedia de un proceso de decisión para ofrecer la mejor solución al problema/consulta del usuario, debes elegir cual es la mejor solución de las ofrecidas para el problema que plantea el usuario. No modifiques la solución ni el tipo de problema"
        f"Mensaje del usuario: '{user_message}'\n"
        f"Categoría ML: {categoria_ml}\n"
        f"Emoción detectada: {emocion}\n\n"
        f"Soluciones candidatas:\n{candidates_text}\n\n"
        f"Evalúa todas las opciones y elige la más relevante para el mensaje y emoción del usuario. "
        f"Elige SOLO la opción más relevante para el mensaje y emoción del usuario. "
        "Responde exactamente con 'Opción X:' seguido de una justificación breve. "
        "Si varias opciones son similares, desempata por cantidad de keywords y confianza."
    )
    respuesta = llm.invoke(selection_prompt)
    print(respuesta)

    # Extracción del índice de opción elegida (regex robusta)
    import re
    match = re.search(r"Opción\s*(\d+)", respuesta)
    if not match:
        # Si el LLM no devuelve formato, fallback seguro
        return None, None, None, "No se pudo determinar opción de LLM. Justificación:" + respuesta
    idx = int(match.group(1)) - 1
    if idx < 0 or idx >= len(all_results):
        return None, None, None, "Índice elegido fuera de rango por el LLM."
    elegido = all_results[idx]
    justificacion = respuesta
    return elegido.get('tipo_problema'), elegido.get('solucion'), elegido, justificacion

role_details = {
    "Organizador": {
        "saludo": "¡Hola estimado organizador! ",
        "tono": "empático y resolutivo",
        "extra": "Recuerda que puedes gestionar tus eventos desde  la sección mis eventos. Cualquier duda no dudes en consultarme."
    },
    "Prestador": {
        "saludo": "Hola prestador, ",
        "tono": "enfocado en apoyo operativo y resolutivo",
        "extra": "No olvides mantener tu perfil y disponibilidad actualizados para evitar inconvenientes."
    },
    "Propietario": {
        "saludo": "Hola propietario, ",
        "tono": "informativo, estratégico y resolutivo",
        "extra": "No olvides mantener tu perfil y disponibilidad actualizados para evitar inconvenientes."
    }
}

EMOTION_TO_TONE = {
    "alegría": "positivo, amable y orientado a soluciones",
    "enojo": "serio, conciliador y orientado a soluciones",
    "asco": "profesional y directo",
    "miedo": "tranquilizador, empático y claro",
    "tristeza": "consolador, empático y paciente",
    "sorpresa": "informativo y claro"
}

def generar_respuesta_streamlit(pregunta, tipo_usuario='Prestador', debug=False):
    test_id = datetime.now().isoformat()
    logger.info(f"[TEST {test_id}] Iniciando - Usuario: {tipo_usuario}, Pregunta: {pregunta[:50]}...")
    try:
        plan = planificar_flujo(pregunta, tipo_usuario, [])
        logger.info(f"PLANIFICACIÓN: {plan}")

        if not plan["ejecutar_flujo_completo"]:
            respuesta = "Lo siento, no puedo ayudar con ese tipo de consulta."
            resultado_prueba = {
                "test_id": test_id,
                "entrada": pregunta,
                "tipo_usuario": tipo_usuario,
                "categoria_predicha_ml": plan["categoria_ml"],
                "confianza_ml": plan["confianza_ml"],
                "keywords": plan["keywords"],
                "plan": plan,
                "respuesta": respuesta,
            }
            with open('resultados_pruebas.json', 'a') as f:
                f.write(json.dumps(resultado_prueba) + '\n')
            logger.info(f"[TEST {test_id}] Fallback por ML")
            return respuesta, [], "N/A", plan["confianza_ml"]

        # --- EJECUCIÓN DEL FLUJO COMPLETO ---
        keywords, kw_time = detect_keywords(pregunta)
        (emocion, emo_score), emo_time = detect_emotion(pregunta)
        confianza_fuzzy, conf_time = fuzzy_problem_categorization(keywords)
        kw_set = set(keywords or [])
        domain_match = kw_set.intersection(DOMAIN_KEYWORDS)
        if not domain_match:
            logger.info(f"No domain keywords found. Skipping DB lookup.")
            respuesta = "Lo siento, no puedo ayudar con ese tipo de consulta. "
            tipo_problema = "No definido"
            solucion = "No definida"
            matched_keys = []
            neo4j_time = 0
            llm_time = 0
        else:
            cypher = cypher_query(keywords, tipo_usuario)
            logger.info(f"Cypher query:\n{cypher}")
            inicio_neo4j = time.time()
            result = graph.query(cypher)
            neo4j_time = time.time() - inicio_neo4j
            tipo_problema = "No definido"
            solucion = "No definida"
            matched_keys = []
            postdata = "No se encontró solución automática, te derivaremos a soporte. (weventlyempresa@gmail.com)"
            if result:
                r = result[0]
                matched_count = int(r.get('matched_count', 0) or 0)
                result_conf = float(r.get('confianza', 0) or 0)
                matched_keys = r.get('matched_keywords', [])
                if matched_count > 0:
                    tipo_problema = r.get('tipo_problema', tipo_problema)
                    solucion = r.get('solucion', solucion)
                    confianza_fuzzy = max(confianza_fuzzy, result_conf)
                    postdata = "Respuesta recomendada por nuestro sistema." if confianza_fuzzy >= 0.7 else "Respuesta tomada de la base de conocimiento (confianza baja, verificar manualmente)."
            tipo_problema_llm, solucion_llm, elegido_result, justificacion_llm = elegir_mejor_solucion_con_llm(pregunta, result, plan['categoria_ml'], emocion, llm)
            rd = role_details.get(tipo_usuario, role_details["Prestador"])
            emotion_tone = EMOTION_TO_TONE.get(emocion, rd.get('tono', 'neutral'))
            prompt_llm = (
                f"Como asistente del sistema Wevently para la organización de eventos privados donde organizadores, prestadores de servicios y propietarios de lugar operan, contesta a la pregunta del usuario."
                f"{rd['saludo']}Se detectó el problema: {tipo_problema_llm}. "
                f"Solución sugerida: {solucion_llm + justificacion_llm}. "
                f"Por favor responde en un tono {emotion_tone}. "
                f"(Categoría ML: {plan['categoria_ml']}, Emoción detectada: {emocion}, score emoción: {emo_score:.2f}, confianza ML: {plan['confianza_ml']:.2f}, confianza fuzzy: {confianza_fuzzy:.2f}). "
                f"Mensaje original: {pregunta}\n"
                f"{rd['extra']}\n{postdata}"
            )
            inicio_llm = time.time()
            respuesta = llm.invoke(prompt_llm)
            llm_time = time.time() - inicio_llm

        resultado_prueba = {
            "test_id": test_id,
            "entrada": pregunta,
            "tipo_usuario": tipo_usuario,
            "categoria_predicha_ml": plan["categoria_ml"],
            "confianza_ml": plan["confianza_ml"],
            "keywords": keywords,
            "emocion": emocion,
            "confianza_fuzzy": confianza_fuzzy,
            "tipo_problema": tipo_problema_llm,
            "solucion": solucion_llm,
            "matched_keywords": matched_keys,
            "respuesta": respuesta,
            "plan": plan,
            "tiempos": {
                "keywords_ms": kw_time * 1000,
                "emocion_ms": emo_time * 1000,
                "fuzzy_ms": conf_time * 1000,
                "neo4j_ms": neo4j_time * 1000 if domain_match else 0,
                "llm_ms": llm_time * 1000 if domain_match else 0,
                "total_ms": (kw_time + emo_time + conf_time + (neo4j_time if domain_match else 0) + (llm_time if domain_match else 0)) * 1000
            }
        }
        with open('resultados_pruebas.json', 'a') as f:
            f.write(json.dumps(resultado_prueba) + '\n')

        if debug:
            logger.info(f"[DEBUG] {json.dumps(resultado_prueba)}")
        logger.info(f"[TEST {test_id}] Completado")
        return respuesta, keywords, emocion, confianza_fuzzy
    except Exception as e:
        logger.error(f"[TEST {test_id}] Error: {str(e)}", exc_info=True)
        raise
