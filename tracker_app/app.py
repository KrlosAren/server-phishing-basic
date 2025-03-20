from fastapi import FastAPI
from fastapi.responses import FileResponse

import requests
import loguru

app = FastAPI()


@app.get("/file")
def get_file(url: str):
    """return a file when click on URL"""
    file_path = "./files/Descuentos_SENATI_Colaboradores_Marzo 2025.docx"
    loguru.logger.info(f"file_path: {file_path}")
    loguru.logger.info(f"url: {url}")
    response = requests.get(url)
    return FileResponse(path=file_path, filename=file_path)
