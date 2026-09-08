"""Utilidades para calculos financieros deterministas.

Este modulo proporciona funciones para calcular balances, evaluar
el impacto de una deuda y calcular el porcentaje de presupuesto usado.
No emite opiniones ni recomendaciones: solo devuelve numeros.
"""


def calcular_balance(
    transacciones: list,
    ingreso_mensual: float,
    meta_ahorro_porcentaje: float,
) -> dict:
    """Calcula el balance financiero a partir de una lista de transacciones.

    Args:
        transacciones: Lista de transacciones con campos monto y tipo.
        ingreso_mensual: Ingreso mensual declarado por el usuario.
        meta_ahorro_porcentaje: Porcentaje de ahorro que el usuario desea alcanzar.

    Returns:
        Diccionario con totales, balance actual y comparacion con la meta de ahorro.
    """
    if isinstance(transacciones, dict):
        transacciones = transacciones.get("transacciones", [])

    total_ingresos = sum(
        t["monto"] for t in transacciones if t["tipo"] == "ingreso"
    )
    total_gastos = sum(
        t["monto"] for t in transacciones if t["tipo"] == "gasto"
    )

    balance = total_ingresos - total_gastos
    meta_ahorro = ingreso_mensual * (meta_ahorro_porcentaje / 100)

    return {
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance": balance,
        "ahorro_posible": balance,
        "meta_ahorro": meta_ahorro,
    }


def evaluar_deuda(
    monto_total: float,
    cuotas: int,
    tasa_interes_mensual: float,
    ingreso_mensual: float,
) -> dict:
    """Calcula el impacto financiero de una deuda usando amortizacion simple.

    No emite juicio sobre si la deuda es buena o mala. Solo calcula y
    alerta si el porcentaje comprometido supera el 30% del ingreso mensual.

    Args:
        monto_total: Valor total del credito o deuda.
        cuotas: Numero de cuotas mensuales.
        tasa_interes_mensual: Tasa de interes mensual en porcentaje (ej: 2.0).
        ingreso_mensual: Ingreso mensual del usuario para calcular el compromiso.

    Returns:
        Diccionario con cuota mensual, total a pagar, intereses totales,
        porcentaje del ingreso comprometido y bandera de alerta.
    """
    tasa = tasa_interes_mensual / 100

    if tasa == 0:
        cuota_mensual = monto_total / cuotas
    else:
        cuota_mensual = monto_total * (tasa * (1 + tasa) ** cuotas) / ((1 + tasa) ** cuotas - 1)

    total_a_pagar = cuota_mensual * cuotas
    total_intereses = total_a_pagar - monto_total
    porcentaje_comprometido = (cuota_mensual / ingreso_mensual) * 100 if ingreso_mensual > 0 else 0

    return {
        "cuota_mensual": round(cuota_mensual, 2),
        "total_a_pagar": round(total_a_pagar, 2),
        "total_intereses": round(total_intereses, 2),
        "porcentaje_ingreso_comprometido": round(porcentaje_comprometido, 2),
        "alerta_compromiso_alto": porcentaje_comprometido > 30,
    }
