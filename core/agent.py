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

from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from tools.calculos_tool import calcular_balance, evaluar_deuda
from tools.transacciones_tool import consultar_transacciones


class Perfil(TypedDict):
    """Representa el perfil financiero del usuario en sesion."""

    ingreso_mensual: float
    meta_ahorro_porcentaje: float
    presupuesto: dict


# Cliente utilizado para realizar solicitudes a la API de Gemini.
client = genai.Client(api_key=GEMINI_API_KEY)


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

    return f"""
Eres un asistente financiero personal. Ayudas al usuario a entender y mejorar sus finanzas.

PERFIL DEL USUARIO:
- Ingreso mensual: ${perfil["ingreso_mensual"]:,.0f}
- Meta de ahorro: {perfil["meta_ahorro_porcentaje"]}% del ingreso (${perfil["ingreso_mensual"] * perfil["meta_ahorro_porcentaje"] / 100:,.0f}/mes)
- Presupuesto por categoria:
{categorias_texto}

MEMORIA RECIENTE:
{memoria}

HERRAMIENTAS DISPONIBLES:
- consultar_transacciones: usa cuando el usuario pregunte por sus gastos, historial o transacciones.
- calcular_balance: usa cuando el usuario pregunte por su balance, cuanto ha gastado o cuanto puede ahorrar.
- evaluar_deuda: usa cuando el usuario mencione creditos, deudas, cuotas o prestamos.

FLUJO DE DECISION (siguelo siempre):
1. Si el usuario pregunta sobre INVERSIONES (acciones, criptomonedas, fondos, bolsa):
   Informa que ese tema requiere asesoria especializada. No opines sobre si es buena o mala idea.

2. Si el usuario menciona una DEUDA o credito:
   Usa evaluar_deuda para calcular cuota, total a pagar, intereses y % del ingreso comprometido.
   Si alerta_compromiso_alto es True, advierte que supera el 30% del ingreso y sugiere hablar con un asesor.
   NUNCA digas si la deuda es buena o mala. Solo muestra los numeros.

3. Si necesitas datos de transacciones antes de responder:
   Usa consultar_transacciones con el filtro adecuado.

4. Para gastos o consultas de presupuesto:
   Usa calcular_balance y compara contra el presupuesto de la categoria.
   Si un gasto supera el limite de su categoria, genera una alerta clara.

5. Siempre termina mostrando visibilidad: balance actual, meta de ahorro, observacion util.

RESTRICCIONES:
- No ejecutes pagos ni transacciones reales.
- No decidas por el usuario. Muestra la informacion, el decide.
- Se breve, claro y sin jerga financiera compleja.
""".strip()


def responder(
    mensaje_usuario: str,
    perfil: Perfil,
    memoria: str,
) -> str:
    """Genera una respuesta del asistente financiero mediante Gemini.

    Args:
        mensaje_usuario: Mensaje enviado por el usuario.
        perfil: Perfil financiero actual del usuario en sesion.
        memoria: Representacion textual de los mensajes recientes.

    Returns:
        Respuesta textual generada por Gemini. Si el modelo no devuelve
        contenido textual, se retorna un mensaje predeterminado.
    """
    contexto = construir_contexto(perfil, memoria)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=mensaje_usuario,
        config=types.GenerateContentConfig(
            system_instruction=contexto,
            tools=[consultar_transacciones, calcular_balance, evaluar_deuda],
        ),
    )

    return response.text or "No fue posible generar una respuesta."
