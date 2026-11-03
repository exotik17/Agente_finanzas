# Agente Financiero

Asistente financiero desarrollado con Streamlit, LangChain y LangGraph. Permite conversar sobre conceptos financieros, consultar herramientas de cálculo y conservar el contexto durante la sesión.

## Requisitos

- Windows 10 u 11.
- Python 3.10 o posterior.
- Una API key de Gemini con acceso a un modelo habilitado para Gemini API.

## Instalación

Abre PowerShell o CMD en la carpeta del proyecto y crea un entorno virtual:

```powershell
py -m venv venv
```

Actívalo según la terminal que estés usando.

En PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

En CMD:

```cmd
venv\Scripts\activate.bat
```

Con el entorno activado, instala las dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell impide activar el entorno por la política de ejecución, puedes usar CMD con el comando anterior o permitir la ejecución de scripts para tu usuario. No es necesario cambiar la política del equipo.

## Configuración de Gemini

Crea un archivo llamado `.env` en la carpeta principal del proyecto y agrega tu clave:

```dotenv
GEMINI_API_KEY=pega_aqui_tu_clave
GEMINI_MODEL=gemini-3.8-flash
```

La variable `GEMINI_MODEL` es opcional; si no se incluye, la aplicación usa el modelo predeterminado definido en `config/settings.py`. Si eliges otro modelo, asegúrate de que esté disponible para tu proyecto y tenga cuota. No subas el archivo `.env` a Git ni compartas capturas donde se vea la clave.

## Ejecución

Con el entorno virtual activado, desde la carpeta del proyecto ejecuta:

```powershell
streamlit run app.py
```

Streamlit mostrará una dirección local, normalmente `http://localhost:8501`. Ábrela en el navegador. Para detener la aplicación, vuelve a la terminal y presiona `Ctrl+C`.

Si cambias el modelo o la clave en `.env` mientras la aplicación está abierta, detenla y vuelve a iniciarla para que lea la configuración nueva.

## Comprobaciones manuales

Estas consultas sirven para recorrer las partes principales del agente. Los resultados pueden variar en la redacción, pero las cifras y el flujo esperado deben coincidir.

| Prueba | Consulta | Qué comprobar |
|---|---|---|
| Concepto financiero | `¿Qué es un fondo de emergencia?` | Respuesta explicativa; en los detalles de sesión, la ruta pasa por `enrutador` y `nodo_conceptual`. |
| Proyección de ahorro | `Quiero ahorrar $600000 y puedo guardar $100000 al mes. ¿Cuántos meses tardaré en alcanzar la meta, sin considerar rendimientos?` | La respuesta indica 6 meses y la traza incluye `agente_financiero` y `herramientas`. |
| Cálculo de deuda | `Calcula una deuda de $1200000 a 12 cuotas, con tasa mensual de 0%, y un ingreso mensual de $600000. ¿Cuál sería mi cuota y qué porcentaje del ingreso representa?` | Cuota de $100000, intereses de $0 y compromiso aproximado de 16,67%; la traza muestra el uso de herramientas. |
| Contexto entre turnos | Primero: `Gano $600000 al mes y quiero ahorrar el 10%.` Después: `Con esos datos, ¿cuánto debería separar al mes?` | El agente mantiene el contexto y calcula $60000 mensuales. No reinicies la conversación entre ambos mensajes. |
| Reinicio | Pulsa `Reiniciar conversación`. | Se vacía el historial de la sesión y se restablece el perfil en memoria. |

Las Tools deterministas también pueden comprobarse directamente con pruebas automatizadas o llamadas controladas a sus funciones. En cambio, las respuestas del modelo requieren conexión y cuota disponibles.

## Errores habituales

- **Falta `GEMINI_API_KEY`:** confirma que `.env` está en la carpeta principal y que la variable tiene una clave válida.
- **Error `429 RESOURCE_EXHAUSTED`:** se agotó la cuota o el límite de solicitudes del modelo. Revisa la cuota del proyecto, usa un modelo disponible para esa cuenta o vuelve a intentar cuando se renueve el límite.
- **No se reconoce `streamlit`:** comprueba que el entorno virtual esté activado e instala las dependencias con `pip install -r requirements.txt`.
- **El puerto ya está ocupado:** inicia Streamlit en otro puerto, por ejemplo `streamlit run app.py --server.port 8502`.

## Evidencias de validación

Guarda las capturas de la pantalla inicial, una respuesta conceptual, una consulta que use una herramienta, el intercambio de dos turnos y la vista móvil. Si documentas un error y su corrección, conserva una captura de cada estado. Evita incluir claves, tokens u otros datos privados.