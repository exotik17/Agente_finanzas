"""Cadena de enrutamiento para clasificar las consultas del usuario.

Utiliza LangChain y el modelo Gemini para analizar la intencion 
del usuario y clasificarla, optimizando costos al evitar llamadas
complejas cuando no son necesarias.
"""

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from config.settings import GEMINI_API_KEY, GEMINI_MODEL


class ResultadoClasificacion(BaseModel):
    """Estructura esperada para la clasificacion del router."""
    categoria: str = Field(
        description="Categoria de la consulta: 'DEUDA', 'GASTOS', 'AHORRO' o 'GENERAL'"
    )


def obtener_cadena_router():
    """Construye y retorna la cadena de clasificacion."""
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.0,
    )
    
    # Aseguramos que el modelo devuelva la estructura de pydantic definida
    llm_estructurado = llm.with_structured_output(ResultadoClasificacion)
    
    prompt = PromptTemplate.from_template(
        """Eres un enrutador inteligente para un agente financiero. 
Clasifica la siguiente consulta del usuario en una de las siguientes categorias:
- DEUDA: Consultas sobre prestamos, tarjetas de credito, intereses, cuotas.
- GASTOS: Consultas sobre presupuesto, transacciones, registro de pagos, alquiler.
- AHORRO: Consultas sobre metas, fondo de emergencia, proyecciones.
- GENERAL: Saludos, preguntas teoricas, consejos que no requieren herramientas.

Consulta: {query}
"""
    )
    
    return prompt | llm_estructurado


def clasificar_consulta(query: str) -> str:
    """Clasifica la consulta del usuario.
    
    Args:
        query: Mensaje del usuario.
        
    Returns:
        String con la categoria asignada.
    """
    cadena = obtener_cadena_router()
    resultado = cadena.invoke({"query": query})
    return resultado.categoria
