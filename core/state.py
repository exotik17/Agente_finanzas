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

    Crea el perfil financiero, transacciones y el historial de mensajes unicamente
    cuando dichas variables aun no existen en st.session_state.
    """
    if "perfil" not in st.session_state:
        st.session_state.perfil = _cargar_perfil_base()

    if "transacciones" not in st.session_state:
        st.session_state.transacciones = []

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []


def actualizar_perfil(texto: str) -> None:
    """Actualiza los datos financieros del usuario identificados en un texto.

    Analiza el contenido recibido para detectar el ingreso mensual, la
    meta de ahorro, presupuestos y gastos mencionados por el usuario.

    Args:
        texto: Mensaje escrito por el usuario del cual se intentara
            extraer informacion financiera.
    """
    texto_lower = texto.lower()

    # Detecta ingreso
    patron_ingreso = r"(?:gano|ingreso|recibo|salario de|sueldo de)\s+\$?\s*([\d.,]+)(?:\s*(millon|millones|millón|mil|miles))?"
    coincidencia = re.search(patron_ingreso, texto_lower)
    if coincidencia:
        valor_str = coincidencia.group(1).replace(".", "").replace(",", ".")
        es_multiplicador = coincidencia.group(2)
        try:
            valor = float(valor_str)
            if es_multiplicador:
                if es_multiplicador in ["millon", "millones", "millón"]:
                    valor *= 1000000
                elif es_multiplicador in ["mil", "miles"]:
                    valor *= 1000
            st.session_state.perfil["ingreso_mensual"] = valor
        except ValueError:
            pass

    # Detecta meta de ahorro
    patron_meta = r"(?:ahorrar|meta de ahorro)[^\d]*([\d.,]+)(?:\s*(%)|\s*(millon|millones|millón|mil|miles))?"
    coincidencia_meta = re.search(patron_meta, texto_lower)
    if coincidencia_meta:
        valor_str = coincidencia_meta.group(1).replace(".", "").replace(",", ".")
        es_porcentaje = coincidencia_meta.group(2) == "%"
        es_multiplicador = coincidencia_meta.group(3)
        try:
            valor = float(valor_str)
            if es_porcentaje:
                st.session_state.perfil["meta_ahorro_porcentaje"] = valor
            else:
                if es_multiplicador:
                    if es_multiplicador in ["millon", "millones", "millón"]:
                        valor *= 1000000
                    elif es_multiplicador in ["mil", "miles"]:
                        valor *= 1000
                
                ingreso = st.session_state.perfil.get("ingreso_mensual", 0)
                if ingreso > 0:
                    st.session_state.perfil["meta_ahorro_porcentaje"] = (valor / ingreso) * 100
        except ValueError:
            pass

    # Detecta presupuesto
    patron_presupuesto = r"(?:presupuesto|limite|destinar|para)(?: de| en)?\s+(vivienda|alimentacion|transporte|ocio|otros)[^\d]*([\d.,]+)(?:\s*(millon|millones|millón|mil|miles))?"
    for coincidencia in re.finditer(patron_presupuesto, texto_lower):
        categoria = coincidencia.group(1)
        valor_str = coincidencia.group(2).replace(".", "").replace(",", ".")
        es_multiplicador = coincidencia.group(3)
        try:
            valor = float(valor_str)
            if es_multiplicador:
                if es_multiplicador in ["millon", "millones", "millón"]:
                    valor *= 1000000
                elif es_multiplicador in ["mil", "miles"]:
                    valor *= 1000
            st.session_state.perfil["presupuesto"][categoria] = valor
        except ValueError:
            pass

    # Detecta gastos: "gaste 50 mil en transporte"
    patron_gasto = r"(?:gast[eé]|pagu[eé]|compr[eé]|gasto de)\s+(?:unos\s+)?\$?\s*([\d.,]+)(?:\s*(millon|millones|millón|mil|miles))?\s+(?:en|por|para)\s+([a-zA-Záéíóú]+)"
    for coincidencia in re.finditer(patron_gasto, texto_lower):
        valor_str = coincidencia.group(1).replace(".", "").replace(",", ".")
        es_multiplicador = coincidencia.group(2)
        categoria_gasto = coincidencia.group(3).lower()
        try:
            valor = float(valor_str)
            if es_multiplicador:
                if es_multiplicador in ["millon", "millones", "millón"]:
                    valor *= 1000000
                elif es_multiplicador in ["mil", "miles"]:
                    valor *= 1000
            
            # Guardamos el gasto en memoria
            st.session_state.transacciones.append({
                "fecha": "Hoy",
                "descripcion": f"Gasto registrado en chat",
                "monto": valor,
                "categoria": categoria_gasto,
                "tipo": "gasto"
            })
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

    Elimina el historial de conversacion, recarga el perfil y limpia transacciones.
    """
    st.session_state.mensajes = []
    st.session_state.transacciones = []
    st.session_state.perfil = _cargar_perfil_base()
