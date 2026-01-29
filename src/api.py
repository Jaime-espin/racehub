from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, CarreraDB
from pydantic import BaseModel
from datetime import date
from main import buscar_y_extraer_datos, guardar_en_db, CarreraSchema
from pathlib import Path

app = FastAPI(title="RaceHub API")

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Servir archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 1. Definimos cómo queremos enviar los datos al navegador
class CarreraOut(BaseModel):
    id: int
    nombre: str
    deporte: str
    fecha: date
    localizacion: str | None
    distancia_resumen: str | None
    url_oficial: str | None
    estado_inscripcion: str | None

    class Config:
        from_attributes = True

# 2. Función para obtener la conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Modelos para recibir datos desde la web ---
class SolicitudCarrera(BaseModel):
    nombre: str

class ConfirmacionCarrera(BaseModel):
    nombre_oficial: str
    deporte: str
    fecha: str
    lugar: str
    distancias: List[str]
    url_oficial: str | None
    estado_inscripcion: str

# --- Endpoint para buscar (sin guardar) ---
@app.post("/carreras/buscar")
def buscar_carrera(solicitud: SolicitudCarrera):
    try:
        # Solo buscamos y extraemos, NO guardamos
        resultado = buscar_y_extraer_datos(solicitud.nombre, max_results=5)
        return {
            "nombre_oficial": resultado.nombre_oficial,
            "deporte": resultado.deporte,
            "fecha": resultado.fecha,
            "lugar": resultado.lugar,
            "distancias": resultado.distancias,
            "url_oficial": resultado.url_oficial,
            "estado_inscripcion": resultado.estado_inscripcion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint para confirmar y guardar ---
@app.post("/carreras/confirmar")
def confirmar_carrera(datos: ConfirmacionCarrera):
    try:
        # Convertimos los datos confirmados a CarreraSchema y guardamos
        carrera_schema = CarreraSchema(
            nombre_oficial=datos.nombre_oficial,
            deporte=datos.deporte,
            fecha=datos.fecha,
            lugar=datos.lugar,
            distancias=datos.distancias,
            url_oficial=datos.url_oficial,
            estado_inscripcion=datos.estado_inscripcion
        )
        guardar_en_db(carrera_schema)
        return {"mensaje": "Carrera guardada correctamente", "nombre": datos.nombre_oficial}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 3. El "Endpoint": La dirección URL donde estarán tus carreras
@app.get("/carreras", response_model=List[CarreraOut])
def listar_carreras(db: Session = Depends(get_db)):
    # Esta línea es puro SQLAlchemy: "Tráeme todas las carreras"
    carreras = db.query(CarreraDB).all()
    return carreras

# --- Endpoint para eliminar una carrera ---
@app.delete("/carreras/{carrera_id}")
def eliminar_carrera(carrera_id: int, db: Session = Depends(get_db)):
    carrera = db.query(CarreraDB).filter(CarreraDB.id == carrera_id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")
    
    nombre = carrera.nombre
    db.delete(carrera)
    db.commit()
    return {"mensaje": f"Carrera '{nombre}' eliminada correctamente"}

@app.get("/compartir", response_class=HTMLResponse)
async def ver_calendario_publico(request: Request):
    # Esta ruta carga el HTML que NO tiene botones de edición
    return templates.TemplateResponse("public.html", {"request": request})