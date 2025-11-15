import os
import sys
import datetime
import re
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(__file__))
import streamlit as st
from langchain import generar_respuesta_streamlit

st.set_page_config(page_title="Wevently Chatbot", page_icon=":robot_face:", layout="wide")
st.title("Asistente Inteligente Wevently")

def save_chat_to_localstorage(chat_history):
    st.session_state['last_saved'] = datetime.datetime.now()
    st.session_state['chat_history_saved'] = chat_history

def get_chat_from_localstorage():
    if 'last_saved' in st.session_state:
        now = datetime.datetime.now()
        if (now - st.session_state['last_saved']).seconds < 1800:
            return st.session_state.get('chat_history_saved', [])
    return []

def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

# Inicializa historial y variable de rol actual
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = get_chat_from_localstorage()
if 'current_rol' not in st.session_state:
    st.session_state['current_rol'] = None

# CSS para layout tipo mensajería
st.markdown("""
    <style>
    .chat-container-main {
        height: 500px;
        overflow-y: auto !important;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        background-color: #f9f9f9;
        margin-bottom: 0.7rem;
    }
    .bubble-user {
        background-color: #0084ff;
        color: white;
        border-radius: 18px 18px 5px 18px;
        padding: 10px 14px;
        margin: 6px 0;
        max-width: 70%;
        align-self: flex-end;
        word-break: break-word;
        font-size: 15px;
        box-shadow: 0 2px 4px rgb(0 0 0 / 12%);
    }
    .bubble-assistant {
        background-color: #e5e5ea;
        color: #222;
        border-radius: 18px 18px 18px 5px;
        padding: 10px 14px;
        margin: 6px 0;
        max-width: 70%;
        align-self: flex-start;
        word-break: break-word;
        font-size: 15px;
        box-shadow: 0 2px 4px rgb(0 0 0 / 8%);
    }
    .meta-info {
        font-size: 11px;
        opacity: 0.7;
        margin-top: 2px;
        font-style: italic;
    }
    .chat-row {display: flex; flex-direction: row; margin-bottom:0;}
    .chat-row.right {justify-content: flex-end;}
    .chat-row.left {justify-content: flex-start;}
    </style>
""", unsafe_allow_html=True)

# --- Selector de rol arriba, borra chat al cambiar ---
rol = st.selectbox("Selecciona tu rol:", ["Organizador", "Prestador", "Propietario"], key="rol")
if rol != st.session_state['current_rol']:
    st.session_state['chat_history'] = []
    st.session_state['current_rol'] = rol
    st.rerun()

# ---- Chat scrolleable central ----
st.markdown("#### Chat")
chat_html = '<div class="chat-container-main">'
for msg in st.session_state.chat_history:
    # Sanitiza para evitar render HTML accidental y muestra sólo texto plano
    user_text = strip_html_tags(str(msg['mensaje']))
    assistant_text = strip_html_tags(str(msg['respuesta']))
    chat_html += f"""
    <div class='chat-row right'>
        <div class='bubble-user'>
            {user_text}
            <div class='meta-info' style='text-align:right;'>{msg['hora']} | {msg['usuario']}</div>
        </div>
    </div>
    <div class='chat-row left'>
        <div class='bubble-assistant'>
            {assistant_text}
            <div class='meta-info'>
                {msg['hora']} | Asistente<br>
                <span style='font-size:9.5px'>KW: {', '.join(msg['keywords'])} — Emo: {msg['emocion']} — Confianza: {msg['confianza']:.2f}</span>
            </div>
        </div>
    </div>
    """
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# ---- Input y botón enviar al pie ----
with st.container():
    col1, col2 = st.columns([0.88, 0.12])
    with col1:
        mensaje = st.text_input("Tu consulta:", key="mensaje_input", placeholder="Escribe tu mensaje...")
    with col2:
        enviar = st.button("Enviar", type="primary", use_container_width=True)

if enviar and mensaje:
    mensaje_clean = strip_html_tags(mensaje)
    response, kwds, emo, conf = generar_respuesta_streamlit(mensaje_clean, tipo_usuario=rol, debug=True)
    response_clean = strip_html_tags(response)
    st.session_state.chat_history.append({
        'usuario': rol,
        'mensaje': mensaje_clean,
        'respuesta': response_clean,
        'keywords': kwds,
        'emocion': emo,
        'confianza': conf,
        'hora': datetime.datetime.now().strftime('%H:%M')
    })
    save_chat_to_localstorage(st.session_state.chat_history)
    st.rerun()
