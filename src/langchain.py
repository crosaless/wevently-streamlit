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

# Palabras que indican queries dentro del dominio de soporte (pagos, transacciones, proveedores, eventos)
DOMAIN_KEYWORDS = {
    'pago','pagos','pagar','pagué','pague','acreditar','acredita','acreditación','acreditacion', 'calendario', 'no', 'anda', 'fallo', 'falló',
    'transferencia','transaccion','transacción','tarjeta','debito','débito','credito','crédito',
    'comision','comisión','comisiones','cobro','cobran','tarifa','devolución','devolucion','rechazar','rechazo','rechazado',
    'servicio','proveedor','prestador','reclamo','cancelacion','cancelación','transacción','evento','eventos', 'rechazó', 'rechaza', 'reintentar'
}

# Logging global
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pruebas_wevently.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Decorador para timing
def medir_tiempo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        duracion = time.time() - inicio
        logger.info(f"{func.__name__} ejecutado en {duracion:.4f}s")
        return resultado, duracion
    return wrapper

# Carga modelos NLP y HuggingFace
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

# Neo4j y Ollama LLM
# Neo4j (via fallback connector) y Ollama LLM
graph = get_graph()
llm = OllamaLLM(
    model="gpt-oss:20b-cloud",
    base_url="https://ollama.com"
)

# Emoción (BETO)
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

# Keywords (spaCy)
@medir_tiempo
def detect_keywords(text):
    doc = nlp(text)
    keywords = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]
    return keywords

# Lógica difusa (scikit-fuzzy)
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

# Cypher
def cypher_query(keywords, tipo_usuario):
    # Build a more robust Cypher: compare lowercase, unwind keywords, allow optional TipoUsuario
    # Order by number of matched keywords first (more relevant), then by confianzaDecision if present.
    # Note: keywords will be inlined as a list literal; ensure they are lowercased for comparison.
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

# Detalles por rol
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

# Map detected emotion to an explicit instruction about the reply tone
EMOTION_TO_TONE = {
    "alegría": "positivo, amable y orientado a soluciones",
    "enojo": "serio, conciliador y orientado a soluciones",
    "asco": "profesional y directo",
    "miedo": "tranquilizador, empático y claro",
    "tristeza": "consolador, empático y paciente",
    "sorpresa": "informativo y claro"
}
# Función principal con logging/pruebas
def generar_respuesta_streamlit(pregunta, tipo_usuario='Prestador', debug=False):
    test_id = datetime.now().isoformat()
    logger.info(f"[TEST {test_id}] Iniciando - Usuario: {tipo_usuario}, Pregunta: {pregunta[:50]}...")
    try:
        keywords, kw_time = detect_keywords(pregunta)
        # detect_emotion is decorated with @medir_tiempo so it returns (resultado, duracion)
        # where resultado is (emocion, score). Unpack accordingly.
        (emocion, emo_score), emo_time = detect_emotion(pregunta)
        confianza, conf_time = fuzzy_problem_categorization(keywords)

        # If the detected keywords have no overlap with our support domain, do
        # not query Neo4j and return a safe fallback (no medical/legal advice etc.).
        kw_set = set(keywords or [])
        domain_match = kw_set.intersection(DOMAIN_KEYWORDS)
        if not domain_match:
            logger.info(f"No domain keywords found in input (keywords={keywords}). Skipping DB lookup.")
            respuesta = "Lo siento, no puedo ayudar con ese tipo de consulta. Por favor contacta a soporte o a un profesional adecuado."
            tipo_problema = "No definido"
            solucion = "No definida"
            # Save minimal result
            resultado_prueba = {
                "test_id": test_id,
                "entrada": pregunta,
                "tipo_usuario": tipo_usuario,
                "keywords": keywords,
                "emocion": emocion,
                "confianza": confianza,
                "tipo_problema": tipo_problema,
                "solucion": solucion,
                "matched_keywords": [],
                "respuesta": respuesta,
                "tiempos": {
                    "keywords_ms": kw_time * 1000,
                    "emocion_ms": emo_time * 1000,
                    "fuzzy_ms": conf_time * 1000,
                    "neo4j_ms": 0,
                    "llm_ms": 0,
                    "total_ms": (kw_time + emo_time + conf_time) * 1000
                }
            }
            with open('resultados_pruebas.json', 'a') as f:
                f.write(json.dumps(resultado_prueba) + '\n')
            return respuesta, keywords, emocion, confianza

        cypher = cypher_query(keywords, tipo_usuario)
        logger.info(f"Cypher query:\n{cypher}")
        inicio_neo4j = time.time()
        result = graph.query(cypher)
        logger.info(f"Neo4j result: {result}")
        neo4j_time = time.time() - inicio_neo4j

        tipo_problema = "No definido"
        solucion = "No definida"
        postdata = "No se encontró solución automática, te derivaremos a soporte. (soporte@wevently.com)"

        # If there are no domain keywords, avoid querying DB (handled earlier),
        # otherwise accept DB result if matched_count>0. Keep confidence info and
        # mark postdata when combined confidence is low.
        if result:
            r = result[0]
            # result may include has_type; prefer results that match user type
            matched_count = int(r.get('matched_count', 0) or 0)
            result_conf = float(r.get('confianza', 0) or 0)
            matched_keys = r.get('matched_keywords', [])
            logger.info(f"DB matched_count={matched_count}, DB_conf={result_conf}, matched_keys={matched_keys}")
            if matched_count > 0:
                # accept DB suggestion even if confidences are low, but flag low confidence
                tipo_problema = r.get('tipo_problema', tipo_problema)
                solucion = r.get('solucion', solucion)
                confianza = max(confianza, result_conf)
                if confianza < 0.7:
                    postdata = "Respuesta tomada de la base de conocimiento (confianza baja, verificar manualmente)."
                else:
                    postdata = "Respuesta recomendada por nuestro sistema."
            else:
                logger.info("Resultado de DB con matched_count=0, no se usará como solución automática")
        rd = role_details.get(tipo_usuario, role_details["Prestador"])
        # Choose tone based on detected emotion, fallback to role tone
        emotion_tone = EMOTION_TO_TONE.get(emocion, rd.get('tono', 'neutral'))
        prompt_llm = (
            f"Como asistente del sistema Wevently para la organización de eventos privados donde organizadores, prestadores de servicios y propietarios de lugar operan, contesta a la pregunta del usuario."
            f"{rd['saludo']}Se detectó el problema: {tipo_problema}. "
            f"Solución sugerida: {solucion}. "
            f"Por favor responde en un tono {emotion_tone}. "
            f"(Emoción detectada: {emocion}, score emoción: {emo_score:.2f}, confianza del sistema: {confianza:.2f}). "
            f"Mensaje original: {pregunta}\n"
            f"{rd['extra']}\n{postdata}"
        )
        inicio_llm = time.time()
        respuesta = llm.invoke(prompt_llm)
        llm_time = time.time() - inicio_llm
        # Guardar en archivo prueba
        resultado_prueba = {
            "test_id": test_id,
            "entrada": pregunta,
            "tipo_usuario": tipo_usuario,
            "keywords": keywords,
            "emocion": emocion,
            "confianza": confianza,
            "tipo_problema": tipo_problema,
            "solucion": solucion,
            "matched_keywords": matched_keys if 'matched_keys' in locals() else [],
            "respuesta": respuesta,
            "tiempos": {
                "keywords_ms": kw_time * 1000,
                "emocion_ms": emo_time * 1000,
                "fuzzy_ms": conf_time * 1000,
                "neo4j_ms": neo4j_time * 1000,
                "llm_ms": llm_time * 1000,
                "total_ms": (kw_time + emo_time + conf_time + neo4j_time + llm_time) * 1000
            }
        }
        with open('resultados_pruebas.json', 'a') as f:
            f.write(json.dumps(resultado_prueba) + '\n')
        if debug:
            logger.info(f"[DEBUG] {json.dumps(resultado_prueba)}")
        logger.info(f"[TEST {test_id}] Completado")
        return respuesta, keywords, emocion, confianza
    except Exception as e:
        logger.error(f"[TEST {test_id}] Error: {str(e)}", exc_info=True)
        raise
