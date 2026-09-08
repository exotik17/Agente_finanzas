"""Utilidades para consultar el historial de transacciones financieras.

Este modulo proporciona funciones para cargar y filtrar las transacciones
almacenadas en el archivo JSON de datos de la aplicacion.
"""

import json
from pathlib import Path


# Ruta al archivo que contiene el historial de transacciones.
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "transacciones.json"


def consultar_transacciones(filtro: str) -> dict:
    """Busca transacciones en el historial segun un criterio de busqueda.

    La busqueda no distingue entre mayusculas y minusculas y permite
    coincidencias parciales por categoria, descripcion o tipo.

    Args:
        filtro: Categoria, descripcion, tipo (gasto/ingreso) o fragmento
            de texto utilizado como criterio de busqueda. Usar "todas"
            para obtener todas las transacciones.

    Returns:
        Diccionario con la clave 'transacciones' que contiene la lista
        de coincidencias. Devuelve la lista completa si el filtro es "todas".

    Raises:
        FileNotFoundError: Si el archivo de transacciones no existe.
        json.JSONDecodeError: Si el archivo contiene un JSON invalido.
    """
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        transacciones = json.load(archivo)

    criterio = filtro.lower().strip()

    if criterio == "todas":
        return {"transacciones": transacciones}

    resultados = [
        t
        for t in transacciones
        if criterio in t["categoria"].lower()
        or criterio in t["descripcion"].lower()
        or criterio in t["tipo"].lower()
    ]
    return {"transacciones": resultados}
