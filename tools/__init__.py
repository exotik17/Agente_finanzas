from tools.transacciones_tool import consultar_transacciones
from tools.calculos_tool import calcular_balance, evaluar_deuda
from tools.ahorro_metas_tool import proyectar_meta_ahorro, calcular_fondo_emergencia

TOOLS_FINANCIERAS = [
    consultar_transacciones,
    calcular_balance,
    evaluar_deuda,
    proyectar_meta_ahorro,
    calcular_fondo_emergencia,
]
