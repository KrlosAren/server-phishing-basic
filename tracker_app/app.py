from fastapi import FastAPI, Request, Query
from fastapi.responses import FileResponse, RedirectResponse

import requests
import loguru

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug-headers")
async def debug_headers(request: Request):
    """Endpoint para depurar cabeceras recibidas"""
    headers_dict = dict(request.headers)
    client_ip = (
        request.headers.get("X-Forwarded-For")
        or request.headers.get("X-Real-IP")
        or request.client.host
    )

    return {
        "headers": headers_dict,
        "client_ip": client_ip,
        "remote_addr": request.client.host,
    }


@app.get("/files")
def get_files():
    file_path = "./files/Descuentos_SENATI_Colaboradores_Marzo 2025.docx"
    return FileResponse(
        path=file_path,
        filename="Descuentos_SENATI_Colaboradores_Marzo 2025.docx",
    )


@app.get("/file")
async def get_file(request: Request, url: str = Query(...)):
    """Registra el clic en GoPhish y luego redirige al archivo"""
    file_url = "https://tracker.grandefensa.org/files"

    # Obtener la IP real del cliente
    client_ip = (
        request.headers.get("X-Forwarded-For")
        or request.headers.get("X-Real-IP")
        or request.client.host
    )

    # Si X-Forwarded-For contiene múltiples IPs, tomar la primera (la del cliente original)
    if client_ip and "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()

    # Modificar la URL para incluir la IP real como parámetro
    # GoPhish usa el parámetro "rid" para identificar el registro, pero necesitamos pasarle la IP
    # de una forma que GoPhish pueda reconocer

    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    # Parsear la URL original
    parsed_url = urlparse(url)

    # Obtener los parámetros existentes
    params = parse_qs(parsed_url.query)

    # Agregar un parámetro personalizado que GoPhish pueda reconocer
    # Este es el truco: añadir un parámetro especial que GoPhish puede usar
    if "ip" not in params:
        params["ip"] = [client_ip]

    # Reconstruir la query string
    new_query = urlencode(params, doseq=True)

    # Reconstruir la URL
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )

    # Extraer headers originales del usuario
    headers = {
        "User-Agent": request.headers.get("User-Agent", ""),
        "Referer": request.headers.get("Referer", ""),
        "X-Forwarded-For": client_ip,
        "X-Real-IP": client_ip,
        # Esta es una técnica común para forzar que los servidores lean la IP remota
        "Client-IP": client_ip,
        "True-Client-IP": client_ip,
        "X-Originating-IP": client_ip,
    }

    payload = {"details": {"ip": client_ip, "url": url, "headers": headers}}

    loguru.logger.info(f"Tracking en GoPhish con URL modificada: {new_url}")
    loguru.logger.info(f"IP del cliente: {client_ip}")
    loguru.logger.info(f"Headers reenviados: {headers}")

    # Enviar la solicitud a GoPhish para registrar el clic
    try:
        response = requests.get(new_url, json=payload, headers=headers, timeout=5)
        loguru.logger.info(
            f"Respuesta de GoPhish: {response.status_code} - {response.text}"
        )
    except requests.exceptions.RequestException as e:
        loguru.logger.error(f"Error enviando request a GoPhish: {e}")

    # Redirigir al archivo
    return RedirectResponse(url=file_url)
