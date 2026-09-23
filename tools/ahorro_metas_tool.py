"""Utilidades para proyeccion de metas de ahorro y calculo de fondo de emergencia.

Este modulo proporciona calculos deterministas para estimar tiempos de ahorro,
rendimientos por interes compuesto sobre aportes periodicos y dimensionamiento
del fondo de emergencia sugerido segun gastos indispensables.
No emite juicios sobre inversiones: solo entrega cifras matematicas.
"""


def proyectar_meta_ahorro(
    meta_monto: float,
    ahorro_mensual: float,
    monto_actual: float = 0.0,
    tasa_rendimiento_anual: float = 0.0,
) -> dict:
    """Calcula el tiempo y la acumulacion de capital para alcanzar una meta de ahorro.

    Permite calcular cuantos meses se requieren para llegar al monto deseado,
    considerando un saldo inicial, aportes mensuales fijos y opcionalmente
    una tasa de rendimiento anual fija con capitalizacion mensual.

    Args:
        meta_monto: Monto total objetivo que se desea alcanzar.
        ahorro_mensual: Aporte o ahorro destinado mensualmente a la meta.
        monto_actual: Saldo o ahorro acumulado actualmente para la meta.
        tasa_rendimiento_anual: Tasa de rendimiento o interes anual estimada en porcentaje (ej: 8.5 para 8.5%).

    Returns:
        Diccionario con meses estimados, anios estimados, total aportado directamente,
        rendimientos totales generados, monto final acumulado y estado de la meta.
    """
    if meta_monto <= 0:
        return {
            "meses_estimados": 0,
            "anios_estimados": 0.0,
            "total_aportado": 0.0,
            "total_rendimientos": 0.0,
            "monto_final": round(monto_actual, 2),
            "meta_alcanzada": True,
            "mensaje": "El monto objetivo ya ha sido alcanzado o es cero.",
        }

    if monto_actual >= meta_monto:
        return {
            "meses_estimados": 0,
            "anios_estimados": 0.0,
            "total_aportado": 0.0,
            "total_rendimientos": 0.0,
            "monto_final": round(monto_actual, 2),
            "meta_alcanzada": True,
            "mensaje": "El monto actual ya cubre la meta requerida.",
        }

    if ahorro_mensual <= 0 and (tasa_rendimiento_anual <= 0 or monto_actual <= 0):
        return {
            "meses_estimados": None,
            "anios_estimados": None,
            "total_aportado": 0.0,
            "total_rendimientos": 0.0,
            "monto_final": round(monto_actual, 2),
            "meta_alcanzada": False,
            "mensaje": "Se requiere un ahorro mensual mayor a cero para alcanzar la meta.",
        }

    tasa_mensual = (tasa_rendimiento_anual / 100) / 12
    saldo = float(monto_actual)
    total_aportes = 0.0
    meses = 0
    limite_meses = 1200  # Limite de seguridad de 100 anios

    while saldo < meta_monto and meses < limite_meses:
        meses += 1
        saldo += ahorro_mensual
        total_aportes += ahorro_mensual
        if tasa_mensual > 0:
            rendimiento_mes = saldo * tasa_mensual
            saldo += rendimiento_mes

    total_rendimientos = max(0.0, saldo - monto_actual - total_aportes)

    return {
        "meses_estimados": meses,
        "anios_estimados": round(meses / 12, 1),
        "total_aportado": round(total_aportes, 2),
        "total_rendimientos": round(total_rendimientos, 2),
        "monto_final": round(saldo, 2),
        "meta_alcanzada": saldo >= meta_monto,
    }


def calcular_fondo_emergencia(
    gastos_mensuales: float,
    meses_cobertura: int = 6,
    ahorro_actual: float = 0.0,
) -> dict:
    """Calcula el dimensionamiento y progreso del fondo de emergencia.

    Determina el monto objetivo para cubrir entre 3 y 6 meses de gastos
    indispensables, contrastando el saldo actual disponible frente a dicho objetivo.

    Args:
        gastos_mensuales: Total de gastos o egresos indispensables por mes.
        meses_cobertura: Cantidad de meses de gastos a respaldar (habitualmente 3 a 6).
        ahorro_actual: Monto actual ahorrado o apartado para emergencias.

    Returns:
        Diccionario con monto objetivo, faltante, porcentaje cubierto y meses cubiertos hoy.
    """
    meses_validos = max(1, int(meses_cobertura))
    monto_objetivo = max(0.0, gastos_mensuales) * meses_validos
    ahorro_limpio = max(0.0, ahorro_actual)

    faltante = max(0.0, monto_objetivo - ahorro_limpio)
    porcentaje_cubierto = (ahorro_limpio / monto_objetivo * 100) if monto_objetivo > 0 else 100.0
    meses_cubiertos = (ahorro_limpio / gastos_mensuales) if gastos_mensuales > 0 else 0.0

    return {
        "monto_objetivo": round(monto_objetivo, 2),
        "ahorro_actual": round(ahorro_limpio, 2),
        "monto_faltante": round(faltante, 2),
        "porcentaje_cubierto": round(porcentaje_cubierto, 2),
        "meses_cubiertos": round(meses_cubiertos, 1),
        "meta_completada": ahorro_limpio >= monto_objetivo,
    }
