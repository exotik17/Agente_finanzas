"""Interfaz principal del agente financiero desarrollado con Streamlit.

Este modulo configura y ejecuta la interfaz web del asistente financiero.
Gestiona la visualizacion del perfil del usuario, el historial de
conversacion y la interaccion entre el usuario y el agente basado en Gemini.

El flujo principal de la aplicacion incluye:

- Validacion de la configuracion requerida.
- Inicializacion del estado de sesion.
- Visualizacion del perfil financiero del usuario en el sidebar.
- Renderizado del historial de conversacion.
- Captura de nuevos mensajes del usuario.
- Actualizacion del perfil y la memoria conversacional.
- Generacion de respuestas mediante el agente financiero.
- Reinicio de la conversacion cuando el usuario lo solicita.
"""

import streamlit as st

from config.settings import validar_configuracion
from core.agent import responder
from core.state import (
    actualizar_perfil,
    agregar_mensaje,
    inicializar_estado,
    obtener_memoria,
    reiniciar_estado,
)


st.set_page_config(
    page_title="Agente Financiero",
    page_icon="💰",
)


# Valida que las variables necesarias para utilizar Gemini esten configuradas.
try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()


# Inicializa el estado persistente de la sesion de Streamlit.
inicializar_estado()


# Encabezado principal de la aplicacion.
st.title("Agente Financiero Personal")
st.caption("Tu asistente para entender y mejorar tus finanzas.")
st.write("MVP con Gemini, perfil financiero, memoria, estado y herramientas de calculo.")


# Panel lateral con el resumen financiero del usuario.
with st.sidebar:
    st.subheader("Mi perfil financiero")

    perfil = st.session_state.perfil

    ingreso = perfil["ingreso_mensual"]
    meta_pct = perfil["meta_ahorro_porcentaje"]
    meta_monto = ingreso * meta_pct / 100

    st.metric("Ingreso mensual", f"${ingreso:,.0f}")
    st.metric("Meta de ahorro", f"${meta_monto:,.0f} ({meta_pct}%)")

    st.divider()
    st.caption("Presupuesto por categoria")
    for categoria, limite in perfil["presupuesto"].items():
        st.write(f"**{categoria.capitalize()}:** ${limite:,.0f}")

    st.divider()

    if st.button("Reiniciar conversacion"):
        reiniciar_estado()
        st.rerun()


# Renderiza el historial de mensajes almacenados en la sesion.
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])


# Captura una nueva consulta del usuario.
prompt = st.chat_input("Escribe tu consulta financiera...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    actualizar_perfil(prompt)
    agregar_mensaje("user", prompt)

    try:
        respuesta = responder(
            mensaje_usuario=prompt,
            perfil=st.session_state.perfil,
            memoria=obtener_memoria(),
        )
    except Exception as error:
        respuesta = f"Ocurrio un error al consultar Gemini: {error}"

    with st.chat_message("assistant"):
        st.markdown(respuesta)

    agregar_mensaje("assistant", respuesta)

    st.rerun()
