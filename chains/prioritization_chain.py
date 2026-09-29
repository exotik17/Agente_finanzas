"""Cadena de priorizacion para evaluar multiples objetivos financieros."""

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from config.settings import GEMINI_API_KEY, GEMINI_MODEL


class Prioridad(BaseModel):
    """Representa una unica prioridad financiera."""
    orden: int = Field(description="Nivel de prioridad (1 es lo mas urgente)")
    tema: str = Field(description="Accion a tomar, ej: 'Pagar deuda de tarjeta', 'Ahorrar fondo emergencia'")
    razon: str = Field(description="Explicacion breve de por que es prioridad")


class ResultadoPriorizacion(BaseModel):
    """Lista ordenada de prioridades financieras."""
    prioridades: list[Prioridad]


def obtener_cadena_priorizacion():
    """Construye y retorna la cadena de priorizacion."""
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.0,
    )
    
    llm_estructurado = llm.with_structured_output(ResultadoPriorizacion)
    
    prompt = PromptTemplate.from_template(
        """Eres un asesor financiero experto evaluando prioridades.
        
El usuario tiene las siguientes inquietudes, metas o situacion:
{situacion}

Evalua cual debe ser su prioridad financiera basandote en principios basicos (Ej: pagar deudas con alto interes ANTES de invertir, armar fondo de emergencia basico ANTES de lujos).
Devuelve una lista ordenada de prioridades.
"""
    )
    
    return prompt | llm_estructurado


def priorizar_situacion(situacion: str) -> list[Prioridad]:
    """Evalua y devuelve las prioridades financieras de una situacion.
    
    Args:
        situacion: Texto describiendo las deudas, metas o inquietudes del usuario.
        
    Returns:
        Lista de objetos Prioridad ordenados.
    """
    cadena = obtener_cadena_priorizacion()
    resultado = cadena.invoke({"situacion": situacion})
    return resultado.prioridades
