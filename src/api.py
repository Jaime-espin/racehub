from fastapi import FastAPI, Depends, Request, HTTPException, Response, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import shortuuid
from src.database import SessionLocal, CarreraDB, UserDB, ResultadoDB
from pydantic import BaseModel
from datetime import date
from src.busqueda_realista import buscar_resultado_realista, buscar_en_archivo_local, generar_instrucciones_usuario
from pathlib import Path
import tempfile
import os
from src.main import buscar_y_extraer_datos, guardar_en_db, CarreraSchema, ResultadoSchema, guardar_resultado_db

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
    url_oficial: Optional[str] = None

class EstadoPlanificacionUpdate(BaseModel):
    estado: str

class InscripcionUpdate(BaseModel):
    fecha_inscripcion: Optional[date] = None

class ResultadoManualIn(BaseModel):
    nombre_carrera: str
    anio: int
    tiempo_oficial: str
    posicion_general: int
    posicion_categoria: Optional[int] = None
    ritmo_medio: Optional[str] = None

class ResultadoOut(BaseModel):
    id: int
    tiempo_oficial: Optional[str] = None
    posicion_general: Optional[int] = None
    ritmo_medio: Optional[str] = None
    comentarios: Optional[str] = None
    confianza: Optional[int] = None
    posicion_categoria: Optional[int] = None

    class Config:
        from_attributes = True

class ActualizarCarrera(BaseModel):
    nombre: Optional[str] = None
    deporte: Optional[str] = None
    fecha: Optional[date] = None
    localizacion: Optional[str] = None
    distancia_resumen: Optional[str] = None
    url_oficial: Optional[str] = None
    estado_inscripcion: Optional[str] = None
    estado_planificacion: Optional[str] = None

class CarreraOut(BaseModel):
    id: int
    nombre: str
    deporte: str
    fecha: Optional[date]
    localizacion: Optional[str]
    distancia_resumen: Optional[str]
    url_oficial: Optional[str]
    estado_inscripcion: Optional[str]
    estado_planificacion: Optional[str] = "candidata"
    fecha_inscripcion: Optional[date] = None
    en_colision: bool = False
    colisiones_con: List[int] = []
    resultados: List[ResultadoOut] = []

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

        # VERSIÓN REALISTA: Con validación y detección de portales
        datos_resultado = buscar_resultado_realista(
            solicitud.nombre_carrera, 
            solicitud.anio, 
            nombre_busqueda,
            url_oficial=solicitud.url_oficial
        )
        
        # Guardar resultado aunque sea parcial
        guardar_resultado_db(datos_resultado, solicitud.nombre_carrera, solicitud.anio, user_id=user.id)
        
        if not datos_resultado.tiempo_oficial:
            instrucciones = generar_instrucciones_usuario(solicitud.nombre_carrera, solicitud.url_oficial)
            return {
                "encontrado": False,
                "mensaje": "No se encontraron datos exactos. Intenta estas opciones:",
                "instrucciones": instrucciones,
                "corredor": nombre_busqueda,
                "confianza": 0.0
            }

        return {
            "encontrado": True,
            "mensaje": "Búsqueda completada",
            "corredor": nombre_busqueda,
            "tiempo": datos_resultado.tiempo_oficial,
            "posicion": datos_resultado.posicion_general,
            "posicion_categoria": datos_resultado.posicion_categoria,
            "ritmo": datos_resultado.ritmo_medio,
            "confianza": datos_resultado.confianza or 0.7
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/resultados/buscar-archivo")
async def buscar_resultado_archivo(
    file: UploadFile = File(...),
    nombre_carrera: str = "",
    nombre_corredor: str = "",
    anio: int = 2024,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para subir PDF/CSV con resultados
    Sistema extraerá datos directamente del archivo
    """
    if not nombre_corredor:
        nombre_corredor = user.nombre_completo
    if not nombre_carrera:
        raise HTTPException(status_code=400, detail="Falta nombre de carrera")
    
    try:
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Procesar archivo
        datos_resultado = buscar_en_archivo_local(
            tmp_path,
            nombre_corredor,
            anio  # Usar año dinámico
        )
        
        # Limpiar archivo temporal
        os.remove(tmp_path)
        
        if not datos_resultado.tiempo_oficial:
            return {
                "encontrado": False,
                "mensaje": f"No se encontró a '{nombre_corredor}' en el archivo",
                "confianza": 0.0
            }

        guardar_resultado_db(datos_resultado, nombre_carrera, anio, user_id=user.id)
        
        return {
            "encontrado": True,
            "mensaje": f"¡Encontrado en {file.filename}!",
            "corredor": nombre_corredor,
            "tiempo": datos_resultado.tiempo_oficial,
            "posicion": datos_resultado.posicion_general,
            "posicion_categoria": datos_resultado.posicion_categoria,
            "ritmo": datos_resultado.ritmo_medio,
            "confianza": datos_resultado.confianza or 0.95
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@app.post("/resultados/manual")
def guardar_resultado_manual(
    datos: ResultadoManualIn,
    user: UserDB = Depends(get_current_user)
):
    try:
        resultado = ResultadoSchema(
            tiempo_oficial=datos.tiempo_oficial,
            posicion_general=datos.posicion_general,
            posicion_categoria=datos.posicion_categoria,
            ritmo_medio=datos.ritmo_medio,
            confianza=1.0
        )
        guardar_resultado_db(resultado, datos.nombre_carrera, datos.anio, user_id=user.id)
        return {"mensaje": "Resultado guardado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Listado y Gestión de Carreras ---
@app.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/carreras", response_model=List[CarreraOut])
def listar_carreras(user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    carreras = db.query(CarreraDB).filter(CarreraDB.user_id == user.id).all()
    estados_validos = {"candidata", "seleccionada", "inscrita", "descartada"}
    seleccionadas = []

    for carrera in carreras:
        if not carrera.estado_planificacion:
            carrera.estado_planificacion = "candidata"
        else:
            carrera.estado_planificacion = carrera.estado_planificacion.lower()
            if carrera.estado_planificacion not in estados_validos:
                carrera.estado_planificacion = "candidata"

        if carrera.estado_planificacion in {"seleccionada", "inscrita"} and carrera.fecha:
            seleccionadas.append(carrera)

    colisiones_por_fecha: dict[str, List[int]] = {}
    for carrera in seleccionadas:
        fecha_key = carrera.fecha.isoformat()
        colisiones_por_fecha.setdefault(fecha_key, []).append(carrera.id)

    for carrera in carreras:
        carrera.en_colision = False
        carrera.colisiones_con = []
        if carrera.estado_planificacion in {"seleccionada", "inscrita"} and carrera.fecha:
            fecha_key = carrera.fecha.isoformat()
            ids = colisiones_por_fecha.get(fecha_key, [])
            if len(ids) > 1:
                carrera.en_colision = True
                carrera.colisiones_con = [cid for cid in ids if cid != carrera.id]

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

@app.put("/carreras/{carrera_id}")
def actualizar_carrera(
    carrera_id: int,
    datos: ActualizarCarrera,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    carrera = db.query(CarreraDB).filter(CarreraDB.id == carrera_id, CarreraDB.user_id == user.id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada o no te pertenece")

    if datos.nombre is not None and datos.nombre.strip():
        carrera.nombre = datos.nombre.strip()
    if datos.deporte is not None and datos.deporte.strip():
        carrera.deporte = datos.deporte.strip()
    if datos.fecha is not None:
        carrera.fecha = datos.fecha
    if datos.localizacion is not None:
        carrera.localizacion = datos.localizacion.strip()
    if datos.distancia_resumen is not None:
        carrera.distancia_resumen = datos.distancia_resumen.strip()
    if datos.url_oficial is not None:
        carrera.url_oficial = datos.url_oficial.strip() or None
    if datos.estado_inscripcion is not None:
        carrera.estado_inscripcion = datos.estado_inscripcion.lower().strip()
    if datos.estado_planificacion is not None:
        carrera.estado_planificacion = datos.estado_planificacion.lower().strip()

    db.commit()
    db.refresh(carrera)
    return {"mensaje": "Carrera actualizada correctamente", "id": carrera.id}

@app.post("/carreras/{carrera_id}/estado")
def actualizar_estado_planificacion(
    carrera_id: int,
    datos: EstadoPlanificacionUpdate,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    estados_validos = {"candidata", "seleccionada", "inscrita", "descartada"}
    estado = datos.estado.lower().strip()
    if estado not in estados_validos:
        raise HTTPException(status_code=400, detail="Estado no valido")

    carrera = db.query(CarreraDB).filter(CarreraDB.id == carrera_id, CarreraDB.user_id == user.id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada o no te pertenece")

    carrera.estado_planificacion = estado
    if estado != "inscrita":
        carrera.fecha_inscripcion = None
    elif not carrera.fecha_inscripcion:
        carrera.fecha_inscripcion = date.today()

    db.commit()
    return {"mensaje": "Estado actualizado", "estado": carrera.estado_planificacion}

@app.post("/carreras/{carrera_id}/inscripcion")
def marcar_inscripcion(
    carrera_id: int,
    datos: InscripcionUpdate,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    carrera = db.query(CarreraDB).filter(CarreraDB.id == carrera_id, CarreraDB.user_id == user.id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada o no te pertenece")

    carrera.estado_planificacion = "inscrita"
    carrera.fecha_inscripcion = datos.fecha_inscripcion or date.today()
    db.commit()
    return {"mensaje": "Inscripcion registrada", "fecha_inscripcion": carrera.fecha_inscripcion}

@app.delete("/resultados/{carrera_id}")
def eliminar_resultado(carrera_id: int, user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    carrera = db.query(CarreraDB).filter(CarreraDB.id == carrera_id, CarreraDB.user_id == user.id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada o no te pertenece")

    eliminados = db.query(ResultadoDB).filter(ResultadoDB.carrera_id == carrera.id).delete()
    db.commit()

    if eliminados == 0:
        raise HTTPException(status_code=404, detail="No hay resultados para esta carrera")

    return {"mensaje": "Resultado eliminado"}

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
    return templates.TemplateResponse(
        request=request,
        name="public.html",
        context={"share_token": share_token, "owner_name": user.nombre_completo}
    )

@app.get("/api/share/{share_token}/carreras", response_model=List[CarreraOut])
def list_public_carreras(share_token: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.share_token == share_token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    carreras = db.query(CarreraDB).filter(CarreraDB.user_id == user.id).all()
    return carreras
