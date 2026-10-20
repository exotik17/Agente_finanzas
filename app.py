"""Interfaz principal del agente financiero con LangGraph y trazabilidad pedagogica.

Muestra en la barra lateral:
- Thread ID activo de la sesion
- Secuencia de nodos recorridos en la ultima invocacion
- Diagrama Mermaid de la arquitectura del grafo
- Perfil financiero y panel de gastos del usuario
"""

import streamlit as st
from langchain_core.messages import HumanMessage

from config.settings import validar_configuracion
from core.session import obtener_config, obtener_o_crear_thread_id
from core.state import (
    actualizar_perfil,
    agregar_mensaje,
    inicializar_estado,
    reiniciar_estado,
)
from graph.state import FinancialState
from graph.workflow import crear_grafo_financiero


# ---------------------------------------------------------------------------
# Funcion auxiliar de invocacion
# ---------------------------------------------------------------------------

def _extraer_contenido(content) -> str:
    """Normaliza el contenido del mensaje a string.

    Gemini puede devolver content como str o como lista de bloques
    [{type, text, ...}] cuando usa structured/thinking output.
    Esta funcion garantiza siempre retornar texto plano.

    Args:
        content: str o list[dict] con el contenido del AIMessage.

    Returns:
        Texto extraido como string.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = [bloque.get("text", "") for bloque in content if bloque.get("type") == "text"]
        return "\n".join(partes).strip()
    return str(content)


def _invocar_con_resultado(mensaje: str, grafo) -> dict:
    """Invoca el grafo financiero y retorna la respuesta y la traza de nodos.

    Args:
        mensaje: Texto del usuario.
        grafo: Grafo compilado por crear_grafo_financiero().

    Returns:
        Diccionario con 'respuesta' (str) y 'pasos' (list[str]).
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
    mensajes = resultado.get("messages", [])
    respuesta = _extraer_contenido(mensajes[-1].content) if mensajes else "Sin respuesta."
    return {"respuesta": respuesta, "pasos": resultado.get("pasos_ejecutados", [])}


# ---------------------------------------------------------------------------
# Configuracion de pagina
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Agente Financiero",
    page_icon="💰",
    layout="wide",
)

# Validacion y estado inicial
try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()

inicializar_estado()

if "grafo" not in st.session_state:
    st.session_state.grafo = crear_grafo_financiero()

if "ultima_traza" not in st.session_state:
    st.session_state.ultima_traza = []


# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------

with st.sidebar:

    # 1. Thread ID activo
    st.subheader("🔗 Sesion LangGraph")
    thread_id = obtener_o_crear_thread_id()
    st.code(thread_id, language=None)
    st.caption("Identificador unico del hilo de conversacion (MemorySaver).")

    st.divider()

    # 2. Traza de nodos recorridos
    st.subheader("🗺️ Nodos recorridos")
    traza = st.session_state.ultima_traza
    if traza:
        ruta_texto = " ➔ ".join(["START"] + traza + ["END"])
        st.success(ruta_texto)
    else:
        st.caption("Aun no hay ejecuciones en esta sesion.")

    st.divider()

    # 3. Diagrama Mermaid de la arquitectura
    with st.expander("📐 Arquitectura del grafo", expanded=False):
        st.markdown("""
`mermaid
flowchart TD
    START([START]) --> enrutador
    enrutador -->|conceptual| nodo_conceptual
    enrutador -->|herramientas| agente_financiero
    nodo_conceptual --> END_C([END])
    agente_financiero -->|tool_calls| herramientas
    agente_financiero -->|sin tools| END_A([END])
    herramientas --> agente_financiero
`
        """)

    st.divider()

    # 4. Perfil financiero del usuario
    st.subheader("👤 Mi perfil financiero")
    perfil = st.session_state.perfil
    transacciones = st.session_state.transacciones

    ingreso = perfil["ingreso_mensual"]
    meta_pct = perfil["meta_ahorro_porcentaje"]
    meta_monto = ingreso * meta_pct / 100

    st.metric("Ingreso mensual", f"${ingreso:,.0f}")
    st.metric("Meta de ahorro", f"${meta_monto:,.0f} ({meta_pct:.1f}%)")

    st.caption("Presupuesto por categoria")
    for categoria, limite in perfil["presupuesto"].items():
        st.write(f"**{categoria.capitalize()}:** ${limite:,.0f}")

    if transacciones:
        st.divider()
        st.caption("Gastos registrados en esta sesion")
        for t in transacciones:
            st.write(f"- {t['categoria'].capitalize()}: ${t['monto']:,.0f}")

    st.divider()
    if st.button("🔄 Reiniciar conversacion"):
        reiniciar_estado()
        st.session_state.ultima_traza = []
        st.session_state.pop("thread_id", None)
        st.session_state.pop("grafo", None)
        st.rerun()


# ---------------------------------------------------------------------------
# Area principal: chat
# ---------------------------------------------------------------------------

st.title("💰 Agente Financiero Personal")
st.caption("Potenciado por LangGraph + Gemini · Memoria persistente por sesion.")

# Historial de mensajes
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# Entrada del usuario
prompt = st.chat_input("Escribe tu consulta financiera...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    actualizar_perfil(prompt)
    agregar_mensaje("user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("Procesando..."):
            try:
                resultado_raw = _invocar_con_resultado(prompt, st.session_state.grafo)
                respuesta = resultado_raw["respuesta"]
                st.session_state.ultima_traza = resultado_raw["pasos"]
            except Exception as error:
                respuesta = f"Ocurrio un error: {error}"
                st.session_state.ultima_traza = []
        st.markdown(respuesta)

    agregar_mensaje("assistant", respuesta)
    st.rerun()
