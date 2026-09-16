import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoCheck API")

# Configuración de CORS para permitir peticiones desde Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "ok", "message": "AutoCheck API activa"}

@app.get("/consultar")
async def consultar(dominio: str):
    if not dominio:
        raise HTTPException(status_code=400, detail="El parámetro dominio es requerido")
    
    dominio_clean = dominio.strip().upper()
    
    # AQUÍ VA TU LÓGICA DE SCRAPING / BÚSQUEDA EXISTENTE
    # Asegúrate de mantener tus funciones de extracción aquí
    
    try:
        # Ejemplo de respuesta estructurada
        # Reemplaza 'datos_obtenidos' por la variable con la que extraes los datos
        return {
            "dominio": dominio_clean,
            "datos": {
                "Estado": "Consulta realizada con éxito",
                "Dominio": dominio_clean
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("autocheck:app", host="0.0.0.0", port=port)
