"""Gestor de sesion y threads para la integracion entre Streamlit y LangGraph.

Cada usuario recibe un thread_id unico almacenado en st.session_state.
LangGraph usa este identificador para aislar los checkpoints de cada sesion,
permitiendo que MemorySaver persista el historial de mensajes por usuario.
"""

import uuid

import streamlit as st
from langchain_core.messages import HumanMessage

from graph.state import FinancialState


# ---------------------------------------------------------------------------
# Thread ID
# ---------------------------------------------------------------------------

def obtener_o_crear_thread_id() -> str:
    """Devuelve el thread_id de la sesion actual, creandolo si no existe.

    Returns:
        UUID en formato string que identifica de forma unica la sesion.
    """
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    return st.session_state.thread_id


def obtener_config() -> dict:
    """Construye el diccionario de configuracion requerido por LangGraph.

    Returns:
        Diccionario con el thread_id listo para pasarse como config= en invoke().
    """
    return {"configurable": {"thread_id": obtener_o_crear_thread_id()}}


# ---------------------------------------------------------------------------
# Invocacion del grafo
# ---------------------------------------------------------------------------

def invocar_grafo(mensaje: str, grafo) -> str:
    """Invoca el grafo financiero con el mensaje del usuario y su perfil.

    Construye el estado inicial a partir del perfil almacenado en la sesion
    de Streamlit, ejecuta el grafo y extrae el texto de la ultima respuesta.

    Args:
        mensaje: Texto introducido por el usuario en el chat.
        grafo: Grafo compilado retornado por crear_grafo_financiero().

    Returns:
        Texto de la respuesta generada por el asistente.
    """
    config = obtener_config()

    estado_inicial: FinancialState = {
        "messages": [HumanMessage(content=mensaje)],
        "perfil": st.session_state.perfil,
        "ruta": "",
        "motivo": "",
        "herramientas_usadas": [],
        "pasos_ejecutados": [],
    }

    resultado = grafo.invoke(estado_inicial, config=config)
    return _extraer_respuesta(resultado)


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _extraer_respuesta(resultado: dict) -> str:
    """Extrae el contenido textual del ultimo AIMessage del estado final.

    Args:
        resultado: Estado final devuelto por grafo.invoke().

    Returns:
        Texto de la ultima respuesta del asistente, o mensaje de error.
    """
    mensajes = resultado.get("messages", [])
    if not mensajes:
        return "No se genero ninguna respuesta."
    return mensajes[-1].content


def obtener_pasos(resultado: dict) -> list[str]:
    """Retorna la traza de nodos recorridos en la ultima ejecucion.

    Args:
        resultado: Estado final devuelto por grafo.invoke().

    Returns:
        Lista con los nombres de los nodos ejecutados en orden.
    """
    return resultado.get("pasos_ejecutados", [])
