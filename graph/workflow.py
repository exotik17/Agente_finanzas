"""Topologia del grafo financiero: nodos, aristas y compilacion (LangGraph).

crear_grafo_financiero() ensambla el StateGraph, define las bifurcaciones
condicionales, el bucle ciclico agente->herramientas->agente y adjunta
MemorySaver para persistencia de conversaciones multi-turno.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from graph.nodes import (
    agente_financiero_node,
    conceptual_node,
    enrutador_node,
    herramientas_node,
)
from graph.state import FinancialState


def crear_grafo_financiero():
    """Construye y compila el grafo del asistente financiero.

    Returns:
        Grafo compilado con MemorySaver como checkpointer.
    """
    builder = StateGraph(FinancialState)

    # --- Registro de nodos ----------------------------------------------
    builder.add_node("enrutador", enrutador_node)
    builder.add_node("nodo_conceptual", conceptual_node)
    builder.add_node("agente_financiero", agente_financiero_node)
    builder.add_node("herramientas", herramientas_node)

    # --- Arista inicial --------------------------------------------------
    builder.add_edge(START, "enrutador")

    # --- Bifurcacion del enrutador ---------------------------------------
    builder.add_conditional_edges(
        "enrutador",
        lambda s: "nodo_conceptual" if s.get("ruta") == "conceptual" else "agente_financiero",
    )

    # --- Arista condicional: invocar herramientas o finalizar ------------
    def evaluar_tools(state: FinancialState):
        """Decide si el agente pidio ejecutar herramientas o ya termino."""
        ultimo = state["messages"][-1]
        if hasattr(ultimo, "tool_calls") and ultimo.tool_calls:
            return "herramientas"
        return END

    builder.add_conditional_edges(
        "agente_financiero",
        evaluar_tools,
        {"herramientas": "herramientas", END: END},
    )

    # --- Bucle ciclico: herramientas retorna al agente ------------------
    builder.add_edge("herramientas", "agente_financiero")

    # --- Nodo conceptual siempre finaliza --------------------------------
    builder.add_edge("nodo_conceptual", END)

    return builder.compile(checkpointer=MemorySaver())
