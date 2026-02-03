from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import shortuuid
from src.database import SessionLocal, CarreraDB, UserDB, ResultadoDB
from pydantic import BaseModel
from datetime import date
from src.main import buscar_y_extraer_datos, guardar_en_db, CarreraSchema, buscar_resultado_usuario, guardar_resultado_db
from pathlib import Path

app = FastAPI(title="RaceHub API")

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Servir archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --- Helper de Autenticación (Simulado) ---
def get_current_user(db: Session):
    # En esta fase, simulamos que siempre es el usuario ID 1
    # Si no existe, lo creamos
    user = db.query(UserDB).filter(UserDB.id == 1).first()
    if not user:
        user = UserDB(id=1, nombre_completo="Usuario Demo", email="demo@racehub.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# 1. Schemas de Respuesta
class ResultadoOut(BaseModel):
    id: int
    tiempo_oficial: str | None
    posicion_general: int | None
    ritmo_medio: str | None
    comentarios: str | None

    class Config:
        from_attributes = True

class CarreraOut(BaseModel):
    id: int
    nombre: str
    deporte: str
    fecha: date
    localizacion: str | None
    distancia_resumen: str | None
    url_oficial: str | None
    estado_inscripcion: str | None
    resultados: List[ResultadoOut] = []

    class Config:
        from_attributes = True

# 2. Función para obtener la conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Modelos para recibir datos ---
class UsuarioUpdate(BaseModel):
    nombre_completo: str

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

class SolicitudResultado(BaseModel):
    nombre_carrera: str
    anio: int
    # nombre_corredor ya no es obligatorio si el usuario tiene perfil
    nombre_corredor: Optional[str] = None

# --- Gestión de Perfil ---
@app.get("/perfil")
def obtener_perfil(db: Session = Depends(get_db)):
    user = get_current_user(db)
    return {"nombre": user.nombre_completo, "email": user.email}

@app.post("/perfil")
def actualizar_perfil(datos: UsuarioUpdate, db: Session = Depends(get_db)):
    user = get_current_user(db)
    user.nombre_completo = datos.nombre_completo
    db.commit()
    return {"mensaje": "Perfil actualizado", "nombre": user.nombre_completo}

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
def confirmar_carrera(datos: ConfirmacionCarrera, db: Session = Depends(get_db)):
    try:
        user = get_current_user(db)
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
        guardar_en_db(carrera_schema, user_id=user.id)
        return {"mensaje": "Carrera guardada correctamente", "nombre": datos.nombre_oficial}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint para buscar y guardar Resultados ---
@app.post("/resultados/buscar")
def buscar_resultado(solicitud: SolicitudResultado, db: Session = Depends(get_db)):
    try:
        user = get_current_user(db)
        nombre_busqueda = solicitud.nombre_corredor
        
        # Si no viene nombre, usamos el del perfil
        if not nombre_busqueda:
            nombre_busqueda = user.nombre_completo

        # 1. Buscamos el resultado con la IA
        datos_resultado = buscar_resultado_usuario(solicitud.nombre_carrera, solicitud.anio, nombre_busqueda)
        
        # 2. Guardamos solo si encontramos algo útil, o guardamos "No encontrado"
        guardar_resultado_db(datos_resultado, solicitud.nombre_carrera, solicitud.anio, user_id=user.id)
        
        # 3. Verificamos si realmente se encontró info
        if not datos_resultado.tiempo_oficial:
             return {
                "encontrado": False,
                "mensaje": "No se encontraron tiempos exactos en las webs públicas.",
                "corredor": nombre_busqueda
            }

        return {
            "encontrado": True,
            "mensaje": "Búsqueda completada",
            "corredor": nombre_busqueda,
            "tiempo": datos_resultado.tiempo_oficial,
            "posicion": datos_resultado.posicion_general,
            "posicion_categoria": datos_resultado.posicion_categoria,
            "ritmo": datos_resultado.ritmo_medio
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 3. El "Endpoint": La dirección URL donde estarán tus carreras
@app.get("/carreras", response_model=List[CarreraOut])
def listar_carreras(db: Session = Depends(get_db)):
    user = get_current_user(db)
    # Filtramos por el usuario actual
    carreras = db.query(CarreraDB).filter(CarreraDB.user_id == user.id).all()
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

# --- Share Feature ---

@app.get("/share/token")
def get_share_token(db: Session = Depends(get_db)):
    user = get_current_user(db)
    if not user.share_token:
        # Generate token using shortuuid
        user.share_token = shortuuid.ShortUUID().random(length=10)
        db.commit()
        db.refresh(user)
    
    # Construct full URL (request.base_url could be used in real scenarios)
    return {"share_token": user.share_token, "share_url": f"/share/{user.share_token}"}

@app.get("/share/{share_token}", response_class=HTMLResponse)
async def public_calendar_view(request: Request, share_token: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.share_token == share_token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Calendario no encontrado")
    
    # We pass the token to the template so JS can use it to fetch data
    return templates.TemplateResponse("public.html", {
        "request": request, 
        "share_token": share_token, 
        "owner_name": user.nombre_completo
    })

@app.get("/api/share/{share_token}/carreras", response_model=List[CarreraOut])
def list_public_carreras(share_token: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.share_token == share_token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    carreras = db.query(CarreraDB).filter(CarreraDB.user_id == user.id).all()
    return carreras