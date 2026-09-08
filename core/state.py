"""Gestion del estado de sesion y memoria del usuario en Streamlit.

Este modulo administra el perfil financiero del usuario y el historial
de mensajes almacenados en st.session_state.

Tambien incluye utilidades para identificar datos financieros a partir
de texto libre, construir una memoria reciente de la conversacion y
reiniciar el estado de la sesion.
"""

import json
import re
from pathlib import Path

import streamlit as st


# Ruta al perfil financiero base cargado desde disco al iniciar.
PERFIL_FILE = Path(__file__).resolve().parents[1] / "data" / "perfil.json"


def _cargar_perfil_base() -> dict:
    """Carga el perfil financiero inicial desde el archivo JSON.

    Returns:
        Diccionario con ingreso mensual, meta de ahorro y presupuesto por categoria.
    """
    with PERFIL_FILE.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def inicializar_estado() -> None:
    """Inicializa las variables necesarias en el estado de sesion.

    Crea el perfil financiero y el historial de mensajes unicamente
    cuando dichas variables aun no existen en st.session_state.
    """
    if "perfil" not in st.session_state:
        st.session_state.perfil = _cargar_perfil_base()

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []


def actualizar_perfil(texto: str) -> None:
    """Actualiza los datos financieros del usuario identificados en un texto.

    Analiza el contenido recibido para detectar el ingreso mensual y la
    meta de ahorro mencionados por el usuario.

    Args:
        texto: Mensaje escrito por el usuario del cual se intentara
            extraer informacion financiera.
    """
    texto_lower = texto.lower()

    # Detecta ingreso: "gano 2000000", "mi ingreso es 1500000", "recibo 1800000"
    patron_ingreso = r"(?:gano|ingreso|recibo|salario de|sueldo de)\s+\$?\s*([\d.,]+)"
    coincidencia = re.search(patron_ingreso, texto_lower)
    if coincidencia:
        valor_str = coincidencia.group(1).replace(".", "").replace(",", "")
        try:
            st.session_state.perfil["ingreso_mensual"] = float(valor_str)
        except ValueError:
            pass

    # Detecta meta de ahorro: "quiero ahorrar el 20%", "meta de ahorro 15%"
    patron_meta = r"(?:ahorrar|meta de ahorro)[^\d]*(\d+)\s*%"
    coincidencia_meta = re.search(patron_meta, texto_lower)
    if coincidencia_meta:
        try:
            st.session_state.perfil["meta_ahorro_porcentaje"] = float(
                coincidencia_meta.group(1)
            )
        except ValueError:
            pass


def agregar_mensaje(role: str, content: str) -> None:
    """Agrega un mensaje al historial de conversacion de la sesion.

    Args:
        role: Rol asociado al mensaje, por ejemplo "user" o "assistant".
        content: Contenido textual del mensaje que se desea almacenar.
    """
    st.session_state.mensajes.append({"role": role, "content": content})


def obtener_memoria(limite: int = 6) -> str:
    """Construye una representacion textual de los mensajes recientes.

    Args:
        limite: Numero maximo de mensajes recientes que se incluiran.
            Por defecto se utilizan los ultimos 6 mensajes.

    Returns:
        Cadena con los mensajes recientes en formato "role: content",
        separados por saltos de linea. Devuelve cadena vacia si no
        existen mensajes almacenados.
    """
    mensajes = st.session_state.mensajes[-limite:]
    return "\n".join(
        f"{m['role']}: {m['content']}" for m in mensajes
    )


def reiniciar_estado() -> None:
    """Restablece la informacion de la sesion a sus valores iniciales.

    Elimina el historial de conversacion y recarga el perfil financiero
    desde el archivo JSON base.
    """
    st.session_state.mensajes = []
    st.session_state.perfil = _cargar_perfil_base()
