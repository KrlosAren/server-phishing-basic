from fastapi import FastAPI, Request,Query
from fastapi.responses import FileResponse,RedirectResponse

import requests
import loguru

app = FastAPI()

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get("/debug-headers")
async def debug_headers(request: Request):
    """Endpoint para depurar cabeceras recibidas"""
    headers_dict = dict(request.headers)
    client_ip = request.headers.get("X-Forwarded-For") or request.headers.get("X-Real-IP") or request.client.host
    
    return {
        "headers": headers_dict,
        "client_ip": client_ip,
        "remote_addr": request.client.host
    }


@app.get('/files')
def get_files():
    file_path = './files/Descuentos_SENATI_Colaboradores_Marzo 2025.docx'
    return FileResponse(
        path=file_path,
        filename='Descuentos_SENATI_Colaboradores_Marzo 2025.docx',
    )

@app.get("/file")
async def get_file(request: Request, url: str = Query(...)):
    """Registra el clic en GoPhish y luego redirige al archivo"""
    file_url = "https://tracker.grandefensa.org/files"

    # Extraer los headers originales del usuario
    headers = {
        "User-Agent": request.headers.get("User-Agent", ""),
        "Referer": request.headers.get("Referer", ""),
        "X-Forwarded-For": request.headers.get("X-Forwarded-For", request.client.host),  # Obtener IP real
        "X-Real-IP": request.headers.get("X-Real-IP", request.client.host),
    }

    loguru.logger.info(f"Tracking en GoPhish con URL: {url}")
    loguru.logger.info(f"Headers reenviados: {headers}")

    # Enviar la solicitud a GoPhish para registrar el clic
    try:
        response = requests.get(url, headers=headers, timeout=5)
        loguru.logger.info(f"Respuesta de GoPhish: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        loguru.logger.error(f"Error enviando request a GoPhish: {e}")

    # Redirigir al archivo
    return RedirectResponse(url=file_url)
