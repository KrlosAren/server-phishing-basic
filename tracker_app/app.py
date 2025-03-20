from fastapi import FastAPI
from fastapi.responses import FileResponse


app = FastAPI()


@app.get("/file")
def get_file():
    """return a file when click on URL"""
    file_path = "./files/Descuentos_SENATI_Colaboradores_Marzo 2025.docx"
    return FileResponse(path=file_path, filename=file_path)
