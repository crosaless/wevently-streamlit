import streamlit as st
from src.langchain import generar_respuesta_streamlit

def test_generar_respuesta_streamlit():
    # Test case 1: Valid input for "Organizador"
    pregunta = "¿Cómo puedo gestionar mis eventos?"
    tipo_usuario = "Organizador"
    respuesta, keywords, emocion, confianza = generar_respuesta_streamlit(pregunta, tipo_usuario)
    
    assert isinstance(respuesta, str), "La respuesta debe ser una cadena."
    assert isinstance(keywords, list), "Las keywords deben ser una lista."
    assert isinstance(emocion, str), "La emoción debe ser una cadena."
    assert isinstance(confianza, float), "La confianza debe ser un número de punto flotante."
    
    # Test case 2: Valid input for "Prestador"
    pregunta = "¿Qué debo hacer para actualizar mi perfil?"
    tipo_usuario = "Prestador"
    respuesta, keywords, emocion, confianza = generar_respuesta_streamlit(pregunta, tipo_usuario)
    
    assert isinstance(respuesta, str), "La respuesta debe ser una cadena."
    assert isinstance(keywords, list), "Las keywords deben ser una lista."
    assert isinstance(emocion, str), "La emoción debe ser una cadena."
    assert isinstance(confianza, float), "La confianza debe ser un número de punto flotante."
    
    # Test case 3: Valid input for "Propietario"
    pregunta = "¿Cómo puedo revisar mis condiciones contractuales?"
    tipo_usuario = "Propietario"
    respuesta, keywords, emocion, confianza = generar_respuesta_streamlit(pregunta, tipo_usuario)
    
    assert isinstance(respuesta, str), "La respuesta debe ser una cadena."
    assert isinstance(keywords, list), "Las keywords deben ser una lista."
    assert isinstance(emocion, str), "La emoción debe ser una cadena."
    assert isinstance(confianza, float), "La confianza debe ser un número de punto flotante."

if __name__ == "__main__":
    test_generar_respuesta_streamlit()