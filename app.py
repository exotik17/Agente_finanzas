"""Interfaz principal del agente financiero con LangGraph y trazabilidad pedagogica."""

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


def _extraer_contenido(content) -> str:
    """Normaliza el contenido del mensaje de Gemini a texto plano."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = [bloque.get("text", "") for bloque in content if bloque.get("type") == "text"]
        return "\n".join(partes).strip()
    return str(content)


def _invocar_con_resultado(mensaje: str, grafo) -> dict:
    """Invoca el grafo financiero y retorna la respuesta y los pasos ejecutados."""
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


st.set_page_config(
    page_title="Agente Financiero",
    page_icon="💰",
    layout="wide",
)

try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

    :root {
        --ink: #172a22;
        --muted: #64746b;
        --green: #176b52;
        --green-dark: #124d3c;
        --mint: #e6f2eb;
        --canvas: #f5f8f4;
        --line: #dce6dd;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; color: var(--ink); }
    .stApp { background: var(--canvas); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] { padding-top: 2rem; max-width: 1180px; }
    [data-testid="stSidebar"] { background: #edf3ee; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] > div { padding-top: 1.5rem; }
    [data-testid="stMetric"] {
        background: #fff; border: 1px solid var(--line); border-radius: 8px;
        padding: .8rem .9rem;
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--green-dark); font-family: 'Manrope', sans-serif; }
    div[data-testid="stChatMessage"] {
        background: #fff; border: 1px solid var(--line); border-radius: 8px;
        padding: .85rem 1rem; margin-bottom: .65rem;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: var(--mint); border-color: #c9dfd0;
    }
    [data-testid="stChatInput"] { border-color: #bfd2c4; }
    .stButton > button {
        border-radius: 7px; border-color: #b7d1c0; color: var(--green-dark);
        background: #fff; font-weight: 600; min-height: 2.7rem;
    }
    .stButton > button:hover { border-color: var(--green); color: var(--green-dark); }
    .brand-kicker {
        color: var(--green); font-size: .75rem; font-weight: 700;
        letter-spacing: .08em; text-transform: uppercase; margin-bottom: .45rem;
    }
    .welcome-panel {
        background: linear-gradient(115deg, #e5f1e8, #fff 72%);
        border: 1px solid var(--line); border-left: 4px solid var(--green);
        border-radius: 8px; padding: 1.25rem 1.4rem; margin: .75rem 0 1.2rem;
    }
    .welcome-panel p { color: var(--muted); margin: .35rem 0 0; }
    .conversation-label {
        color: var(--muted); font-size: .78rem; font-weight: 700;
        text-transform: uppercase; margin: 1.4rem 0 .6rem;
    }
    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem .85rem 2rem; }
        .welcome-panel { padding: 1rem; }
        div[data-testid="stChatMessage"] { padding: .7rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

inicializar_estado()
if "grafo" not in st.session_state:
    st.session_state.grafo = crear_grafo_financiero()
if "ultima_traza" not in st.session_state:
    st.session_state.ultima_traza = []


with st.sidebar:
    st.markdown('<div class="brand-kicker">Tu espacio de finanzas</div>', unsafe_allow_html=True)
    st.subheader("Resumen personal")

    with st.expander("Detalles de sesión", expanded=False):
        st.caption("Identificador de conversación")
        st.code(obtener_o_crear_thread_id(), language=None)
        if st.session_state.ultima_traza:
            st.caption("Ruta de procesamiento")
            st.success(" ➔ ".join(["Inicio"] + st.session_state.ultima_traza + ["Fin"]))
        else:
            st.caption("La ruta de procesamiento aparecerá después de tu primera consulta.")

    with st.expander("Cómo funciona el agente", expanded=False):
        st.markdown(
            """
```mermaid
flowchart TD
    START([START]) --> enrutador
    enrutador -->|conceptual| nodo_conceptual
    enrutador -->|herramientas| agente_financiero
    nodo_conceptual --> END_C([END])
    agente_financiero -->|tool_calls| herramientas
    agente_financiero -->|sin tools| END_A([END])
    herramientas --> agente_financiero
```
            """
        )

    st.divider()
    perfil = st.session_state.perfil
    transacciones = st.session_state.transacciones
    ingreso = perfil["ingreso_mensual"]
    meta_pct = perfil["meta_ahorro_porcentaje"]
    meta_monto = ingreso * meta_pct / 100

    if ingreso > 0:
        st.metric("Ingreso mensual", f"${ingreso:,.0f}")
        st.metric("Meta de ahorro", f"${meta_monto:,.0f}", f"{meta_pct:.1f}% del ingreso")
    else:
        st.info("Completa tu perfil contando tu ingreso mensual y tu meta de ahorro en el chat.")

    st.markdown("**Presupuesto por categoría**")
    presupuestos_configurados = 0
    for categoria, limite in perfil["presupuesto"].items():
        if limite <= 0:
            continue
        gasto_categoria = sum(
            transaccion["monto"]
            for transaccion in transacciones
            if transaccion["categoria"].lower() == categoria.lower()
        )
        presupuestos_configurados += 1
        st.caption(f"{categoria.capitalize()} · ${gasto_categoria:,.0f} de ${limite:,.0f}")
        st.progress(min(gasto_categoria / limite, 1.0))
    if not presupuestos_configurados:
        st.caption("Aún no hay límites definidos. Puedes establecerlos desde el chat.")
    if transacciones:
        st.caption(f"{len(transacciones)} gasto(s) registrado(s) en esta conversación")

    st.divider()
    if st.button("Reiniciar conversación", icon="🔄", use_container_width=True):
        reiniciar_estado()
        st.session_state.ultima_traza = []
        st.session_state.pop("thread_id", None)
        st.session_state.pop("grafo", None)
        st.rerun()


st.markdown('<div class="brand-kicker">Asistente de bienestar financiero</div>', unsafe_allow_html=True)
st.title("Tus finanzas, más claras")
st.caption("Pregunta, organiza tus gastos y avanza hacia tus metas con orientación personalizada.")

if st.session_state.mensajes:
    st.markdown(
        f'<div class="conversation-label">Conversación · {len(st.session_state.mensajes)} mensajes</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="welcome-panel">
            <strong>¿Qué te gustaría ordenar hoy?</strong>
            <p>Cuéntame sobre tus gastos, una meta de ahorro o una decisión financiera.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    consultas_sugeridas = [
        "Ayúdame a crear una meta de ahorro",
        "¿Cómo puedo organizar mis gastos?",
        "Explícame qué es un presupuesto 50/30/20",
    ]
    columnas_sugerencias = st.columns(3)
    for indice, consulta in enumerate(consultas_sugeridas):
        if columnas_sugerencias[indice].button(
            consulta, key=f"consulta_sugerida_{indice}", use_container_width=True
        ):
            st.session_state.consulta_sugerida = consulta
            st.rerun()

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        if mensaje["role"] == "assistant" and mensaje["content"].startswith("⚠️"):
            st.warning(mensaje["content"])
        else:
            st.markdown(mensaje["content"])

consulta_sugerida = st.session_state.pop("consulta_sugerida", None)
prompt = st.chat_input("Escribe tu consulta financiera...") or consulta_sugerida

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    actualizar_perfil(prompt)
    agregar_mensaje("user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("Procesando tu consulta..."):
            try:
                resultado_raw = _invocar_con_resultado(prompt, st.session_state.grafo)
                respuesta = resultado_raw["respuesta"]
                st.session_state.ultima_traza = resultado_raw["pasos"]
                ocurrio_error = False
            except Exception:
                respuesta = "⚠️ No pude completar esta consulta. Revisa tu conexión y vuelve a intentarlo."
                st.session_state.ultima_traza = []
                ocurrio_error = True

        if ocurrio_error:
            st.warning(respuesta)
        else:
            st.markdown(respuesta)

    agregar_mensaje("assistant", respuesta)
    st.rerun()
