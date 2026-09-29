"""Cadena para generar la respuesta final del agente financiero."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_API_KEY, GEMINI_MODEL


def obtener_cadena_respuesta():
    """Construye y retorna la cadena generadora de respuestas."""
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.7,
    )
    
    prompt = PromptTemplate.from_template(
        """Eres un asistente financiero empatico, claro y directo.

Categoria detectada: {categoria}
Prioridades a tener en cuenta (si aplica): {prioridades}

Consulta del usuario: {query}

Instrucciones:
1. Responde directamente a la consulta del usuario.
2. Si hay prioridades listadas, usalas para estructurar tu consejo (ej: "Primero deberiamos... luego podriamos...").
3. No uses jerga complicada. Manten el tono alentador.

Genera la respuesta final:"""
    )
    
    return prompt | llm | StrOutputParser()


def generar_respuesta_simple(query: str, categoria: str, prioridades: str = "Ninguna") -> str:
    """Genera una respuesta fluida para el usuario.
    
    Args:
        query: Consulta original del usuario.
        categoria: Categoria detectada por el router.
        prioridades: Texto de prioridades detectadas.
        
    Returns:
        Texto de respuesta generado por el modelo.
    """
    cadena = obtener_cadena_respuesta()
    return cadena.invoke({
        "query": query, 
        "categoria": categoria, 
        "prioridades": prioridades
    })
