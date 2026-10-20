"""Nodos de transformacion del grafo financiero (LangGraph).

Cada funcion recibe FinancialState y devuelve un diccionario parcial
con los campos modificados; LangGraph aplica el merge automaticamente.
"""

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool as lc_tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from graph.state import FinancialState
from prompts.academic_prompt import (
    AGENT_SYSTEM_TEMPLATE,
    CONCEPTUAL_SYSTEM_PROMPT,
    ROUTER_SYSTEM_PROMPT,
)
from tools import TOOLS_FINANCIERAS


# --- LLM base -----------------------------------------------------------
_modelo = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    temperature=0.0,
)


# --- Esquema de salida del enrutador ------------------------------------
class DecisionEnrutador(BaseModel):
    """Resultado estructurado del nodo enrutador."""

    ruta: str = Field(description="Ruta elegida: 'conceptual' o 'herramientas'")
    motivo: str = Field(description="Justificacion breve de la clasificacion")


_modelo_estructurado = _modelo.with_structured_output(DecisionEnrutador)

# Convertimos las funciones Python planas a LangChain tools para ToolNode
_tools_lc = [lc_tool(fn) for fn in TOOLS_FINANCIERAS]


# --- Nodo 1: Enrutador --------------------------------------------------
def enrutador_node(state: FinancialState) -> dict:
    """Clasifica la consulta entre 'conceptual' y 'herramientas'."""
    decision = _modelo_estructurado.invoke(
        [SystemMessage(content=ROUTER_SYSTEM_PROMPT), *state["messages"]]
    )
    return {
        "ruta": decision.ruta,
        "motivo": decision.motivo,
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["enrutador"],
    }


# --- Nodo 2: Respuesta conceptual ---------------------------------------
def conceptual_node(state: FinancialState) -> dict:
    """Genera una respuesta teorica sin invocar herramientas de calculo."""
    respuesta = _modelo.invoke(
        [SystemMessage(content=CONCEPTUAL_SYSTEM_PROMPT), *state["messages"]]
    )
    return {
        "messages": [respuesta],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["nodo_conceptual"],
    }


# --- Nodo 3: Agente financiero con herramientas -------------------------
def agente_financiero_node(state: FinancialState) -> dict:
    """Razona sobre el perfil del usuario e invoca herramientas si las necesita."""
    perfil = state["perfil"]
    categorias_texto = "\n".join(
        f"  - {cat}: ${monto:,.0f}" for cat, monto in perfil["presupuesto"].items()
    )
    system_prompt = AGENT_SYSTEM_TEMPLATE.format(
        ingreso_mensual=perfil["ingreso_mensual"],
        meta_ahorro_porcentaje=perfil["meta_ahorro_porcentaje"],
        meta_monto=perfil["ingreso_mensual"] * perfil["meta_ahorro_porcentaje"] / 100,
        categorias_texto=categorias_texto,
        memoria="",  # La memoria vive en messages; campo reservado para uso futuro
    )
    modelo_con_tools = _modelo.bind_tools(_tools_lc)
    respuesta = modelo_con_tools.invoke(
        [SystemMessage(content=system_prompt), *state["messages"]]
    )
    return {
        "messages": [respuesta],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["agente_financiero"],
    }


# --- Nodo 4: Ejecutor nativo de herramientas ----------------------------
_ejecutor_tools = ToolNode(_tools_lc)


def herramientas_node(state: FinancialState) -> dict:
    """Ejecuta las herramientas solicitadas por el agente y retorna sus resultados."""
    resultado = _ejecutor_tools.invoke(state)
    return {
        "messages": resultado["messages"],
        "pasos_ejecutados": state.get("pasos_ejecutados", []) + ["herramientas"],
    }
