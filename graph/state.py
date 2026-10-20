"""Esquema de estado compartido del grafo financiero (LangGraph).

FinancialState es el unico objeto que viaja entre nodos.
El reducer add_messages gestiona automaticamente la lista de mensajes,
acumulando HumanMessage, AIMessage y ToolMessage sin sobreescrituras.
"""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class PerfilFinanciero(TypedDict):
    """Datos financieros del usuario activos en la sesion."""

    ingreso_mensual: float
    meta_ahorro_porcentaje: float
    presupuesto: dict  # {categoria: limite_mensual}


class FinancialState(TypedDict):
    # Reducer automatico: acumula HumanMessage, AIMessage y ToolMessage
    messages: Annotated[list[BaseMessage], add_messages]

    perfil: PerfilFinanciero        # Perfil financiero del usuario
    ruta: str                       # 'conceptual' | 'herramientas'
    motivo: str                     # Justificacion del enrutador
    herramientas_usadas: list[str]  # Nombres de tools invocadas
    pasos_ejecutados: list[str]     # Traza de nodos recorridos
