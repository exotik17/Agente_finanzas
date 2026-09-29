"""Integracion del asistente financiero con la API de Gemini.

Este modulo configura el cliente de Gemini y proporciona las funciones
necesarias para construir el contexto del asistente y generar respuestas
a partir de los mensajes del usuario.

El asistente utiliza el perfil financiero del usuario, la memoria reciente
de la conversacion y herramientas externas para responder consultas financieras.
Toda la logica de flujo (inversiones, deudas, alertas de presupuesto) vive
en el system prompt, no en codigo Python separado.
"""

from typing import TypedDict
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import tool

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from tools.ahorro_metas_tool import calcular_fondo_emergencia, proyectar_meta_ahorro
from tools.calculos_tool import calcular_balance, evaluar_deuda
from tools.transacciones_tool import consultar_transacciones
from prompts.academic_prompt import SYSTEM_PROMPT
from chains.router import clasificar_consulta
from chains.response import generar_respuesta_simple
from chains.prioritization_chain import priorizar_situacion
from core.state import registrar_ejecucion



class Perfil(TypedDict):
    """Representa el perfil financiero del usuario en sesion."""

    ingreso_mensual: float
    meta_ahorro_porcentaje: float
    presupuesto: dict


    presupuesto: dict


def construir_contexto(perfil: Perfil, memoria: str) -> str:
    """Construye las instrucciones de contexto para el asistente financiero.

    Combina el perfil financiero actual del usuario con la memoria reciente
    de la conversacion. El system prompt codifica el flujo de decisiones
    definido en el diagrama del proyecto.

    Args:
        perfil: Perfil financiero actual del usuario en sesion.
        memoria: Representacion textual de los mensajes recientes.

    Returns:
        Instruccion de sistema que se enviara al modelo Gemini como contexto.
    """
    presupuesto = perfil["presupuesto"]
    categorias_texto = "\n".join(
        f"  - {cat}: ${monto:,.0f}" for cat, monto in presupuesto.items()
    )

    return SYSTEM_PROMPT.format(
        ingreso_mensual=perfil["ingreso_mensual"],
        meta_ahorro_porcentaje=perfil["meta_ahorro_porcentaje"],
        meta_monto=perfil["ingreso_mensual"] * perfil["meta_ahorro_porcentaje"] / 100,
        categorias_texto=categorias_texto,
        memoria=memoria,
    ).strip()

def responder(
    mensaje_usuario: str,
    perfil: Perfil,
    memoria: str,
) -> str:
    """Genera una respuesta del asistente financiero mediante LangChain."""
    
    # 1. Clasificar consulta (Router)
    start_time = time.time()
    categoria = clasificar_consulta(mensaje_usuario)
    registrar_ejecucion("Router Chain", time.time() - start_time)

    # 2. Despacho inteligente
    if categoria == "GENERAL":
        # Cadena directa sin herramientas pesadas
        start_time = time.time()
        respuesta = generar_respuesta_simple(query=mensaje_usuario, categoria=categoria)
        registrar_ejecucion("Response Chain", time.time() - start_time)
        return respuesta

    # Si no es GENERAL, evaluar prioridades e instanciar el agente con herramientas
    start_time = time.time()
    
    # Podriamos obtener prioridades si es una consulta compleja
    # prioridades = priorizar_situacion(mensaje_usuario)
    
    contexto = construir_contexto(perfil, memoria)
    
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.0
    )
    
    # Convertimos a tools de LangChain
    herramientas = [
        tool(consultar_transacciones),
        tool(calcular_balance),
        tool(evaluar_deuda),
        tool(proyectar_meta_ahorro),
        tool(calcular_fondo_emergencia)
    ]
    
    agent_executor = create_agent(llm, herramientas, contexto)
    
    try:
        resultado = agent_executor.invoke({"input": mensaje_usuario})
        respuesta = resultado["output"]
    except Exception as e:
        respuesta = f"Error en la ejecucion del agente: {e}"
        
    registrar_ejecucion("Agent Executor", time.time() - start_time)
    
    return respuesta
