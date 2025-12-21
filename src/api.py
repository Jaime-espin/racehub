from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates # Librería para HTML
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from src.database import SessionLocal, CarreraDB # Importamos tu DB
from pydantic import BaseModel
from datetime import date

app = FastAPI(title="RaceHub API")
templates = Jinja2Templates(directory="templates")

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

@app.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
# 3. El "Endpoint": La dirección URL donde estarán tus carreras
@app.get("/carreras", response_model=List[CarreraOut])
def listar_carreras(db: Session = Depends(get_db)):
    # Esta línea es puro SQLAlchemy: "Tráeme todas las carreras"
    carreras = db.query(CarreraDB).all()
    return carreras

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a RaceHub API."}