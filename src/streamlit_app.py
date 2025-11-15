import os
import sys
from dotenv import load_dotenv
load_dotenv()
# Ensure the directory of this file is on sys.path so local modules (langchain.py)
# can be imported reliably when running `streamlit run src/streamlit_app.py`.
sys.path.append(os.path.dirname(__file__))

import streamlit as st
from langchain import generar_respuesta_streamlit

st.set_page_config(page_title="Wevently Chatbot", page_icon=":robot_face:", layout="centered")
st.title("Asistente Inteligente Wevently")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

rol = st.selectbox("Selecciona tu rol:", ["Organizador", "Prestador", "Propietario"], key="rol")
mensaje = st.text_input("Tu consulta:")

if st.button("Enviar", type="primary") and mensaje:
    response, kwds, emo, conf = generar_respuesta_streamlit(mensaje, tipo_usuario=rol)
    st.session_state.chat_history.append((mensaje, response, kwds, emo, conf))

st.markdown("#### Historial de chat")
for usr, bot, kw, emo, conf in st.session_state.chat_history[::-1]:
    st.info(f"**Tú:** {usr}")
    st.success(f"**Asistente:** {bot} _(Keywords: {kw} | Emoción: {emo} | Confianza: {conf:.2f})_")