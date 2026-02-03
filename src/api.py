from fastapi import FastAPI, Depends, Request, HTTPException, Response
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

# --- Dependencia de Base de Datos ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Modelos Pydantic (Definidos ANTES de ser usados) ---
class UsuarioLogin(BaseModel):
    email: str

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
    nombre_corredor: Optional[str] = None

class CarreraOut(BaseModel):
    id: int
    nombre: str
    deporte: str
    fecha: Optional[date]
    localizacion: Optional[str]
    distancia_resumen: Optional[str]
    url_oficial: Optional[str]
    estado_inscripcion: Optional[str]

    class Config:
        from_attributes = True

# --- Configuración de la App ---
app = FastAPI(title="RaceHub API")

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --- Helper de Autenticación ---
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_email = request.cookies.get("user_email")
    if not user_email:
        raise HTTPException(status_code=401, detail="No has iniciado sesión")
    
    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no válido")
    return user

# --- Endpoints de Autenticación ---
@app.post("/auth/login")
def login(datos: UsuarioLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == datos.email).first()
    if not user:
        nombre_publico = datos.email.split('@')[0]
        user = UserDB(nombre_completo=nombre_publico, email=datos.email)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    response.set_cookie(key="user_email", value=user.email, max_age=31536000)
    return {"mensaje": "Login exitoso", "user": user.email}

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("user_email")
    return {"mensaje": "Logout exitoso"}

@app.get("/auth/me")
def check_auth(user: UserDB = Depends(get_current_user)):
    return {"email": user.email, "nombre": user.nombre_completo}

# --- Gestión de Perfil ---
@app.get("/perfil")
def obtener_perfil(user: UserDB = Depends(get_current_user)):
    return {"nombre": user.nombre_completo, "email": user.email}

@app.post("/perfil")
def actualizar_perfil(datos: UsuarioUpdate, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    user.nombre_completo = datos.nombre_completo
    db.commit()
    return {"mensaje": "Perfil actualizado", "nombre": user.nombre_completo}

# --- Búsqueda de Carreras ---
@app.post("/carreras/buscar")
def buscar_carrera(solicitud: SolicitudCarrera):
    try:
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

@app.post("/carreras/confirmar")
def confirmar_carrera(datos: ConfirmacionCarrera, user: UserDB = Depends(get_current_user)):
    try:
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

# --- Resultados ---
@app.post("/resultados/buscar")
def buscar_resultado(solicitud: SolicitudResultado, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        nombre_busqueda = solicitud.nombre_corredor
        if not nombre_busqueda:
            nombre_busqueda = user.nombre_completo

        datos_resultado = buscar_resultado_usuario(solicitud.nombre_carrera, solicitud.anio, nombre_busqueda)
        guardar_resultado_db(datos_resultado, solicitud.nombre_carrera, solicitud.anio, user_id=user.id)
        
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

# --- Listado y Gestión de Carreras ---
@app.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/carreras", response_model=List[CarreraOut])
def listar_carreras(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    carreras = db.query(CarreraDB).filter(CarreraDB.user_id == user.id).all()
    return carreras

@app.delete("/carreras/{carrera_id}")
def eliminar_carrera(carrera_id: int, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    carrera = db.query(CarreraDB).filter(CarreraDB.id == carrera_id, CarreraDB.user_id == user.id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada o no te pertenece")
    
    nombre = carrera.nombre
    db.delete(carrera)
    db.commit()
    return {"mensaje": f"Carrera '{nombre}' eliminada correctamente"}

# --- Share Feature ---
@app.get("/share/token")
def get_share_token(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.share_token:
        user.share_token = shortuuid.ShortUUID().random(length=10)
        db.commit()
        db.refresh(user)
    return {"share_token": user.share_token, "share_url": f"/share/{user.share_token}"}

@app.get("/share/{share_token}", response_class=HTMLResponse)
async def public_calendar_view(request: Request, share_token: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.share_token == share_token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Calendario no encontrado")
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
