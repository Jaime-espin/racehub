# Script del sistema de ingesta de datos.
# Utiliza un agente LLM via Groq y el motor de busqueda Tavily
# para automatizar la extraccion de informacion deportiva.
# Los datos son validados con Pydantic y persistidos en base de datos.

import os
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from dateutil import parser
from sqlalchemy.orm import Session
from src.database import SessionLocal, CarreraDB, ResultadoDB

load_dotenv()

# Validacion de variables de entorno requeridas
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("ERROR: TAVILY_API_KEY no esta configurada en el archivo .env")
if not GROQ_API_KEY:
    raise ValueError("ERROR: GROQ_API_KEY no esta configurada en el archivo .env")

# --- 1. SCHEMAS ---

class CarreraSchema(BaseModel):
    nombre_oficial: str = Field(description="Nombre oficial", min_length=3)
    deporte: str = Field(description="Obligatorio: Running, Trail, Ciclismo, Gravel o Triatlon")
    fecha: str = Field(description="Formato YYYY-MM-DD")
    lugar: str = Field(min_length=2)
    distancias: List[str] = Field(min_items=1)
    url_oficial: Optional[str] = None
    estado_inscripcion: str = Field(description="Solo puede ser: 'abierta', 'cerrada' o 'pendiente'")
    
    @validator('estado_inscripcion')
    def validar_estado(cls, v):
        estados_validos = ['abierta', 'cerrada', 'pendiente']
        v_lower = v.lower()
        if v_lower not in estados_validos:
            raise ValueError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
        return v_lower
    
    @validator('fecha')
    def validar_formato_fecha(cls, v):
        try:
            parser.parse(v)
            return v
        except (ValueError, TypeError) as e:
            raise ValueError("La fecha debe estar en formato valido (preferentemente YYYY-MM-DD)") from e
    
    @validator('deporte')
    def validar_deporte(cls, v):
        deportes_validos = ['running', 'trail', 'ciclismo', 'gravel', 'triatlon', 'triatlon', 'snow running']
        if v.lower() not in deportes_validos:
            print(f"Advertencia: Deporte '{v}' no esta en la lista estandar")
        return v

class ResultadoSchema(BaseModel):
    tiempo_oficial: Optional[str] = Field(None, description="Tiempo Oficial (ej: '1:30:45'). Si no se encuentra, dejar null")
    posicion_general: Optional[int] = Field(None, description="Posicion numerica absoluta. Null si no hay datos.")
    posicion_categoria: Optional[int] = Field(None, description="Posicion en su categoria. Null si no hay datos.")
    ritmo_medio: Optional[str] = Field(None, description="Ritmo medio (ej: '4:30 min/km'). Null si no hay datos.")
    confianza: Optional[float] = Field(0.5, description="Nivel de confianza (0.0-1.0). 0.9 = alta confianza regex, 0.65 = baja confianza LLM")

    @validator('tiempo_oficial', pre=True)
    def parse_tiempo_flexible(cls, v):
        if v is None or str(v).strip().lower() in ['n/a', 'na', 'none', 'null', '-', 'undefined', 'no encontrado', '']:
            return None
        return str(v).strip()

    @validator('posicion_general', 'posicion_categoria', pre=True)
    def parse_posicion_flexible(cls, v):
        if v is None or v == '' or str(v).lower() in ['n/a', 'na', 'none', 'null', '-', 'undefined']:
            return None
        import re
        m = re.search(r'\d+', str(v))
        return int(m.group(0)) if m else None

# --- MOTORES DE BUSQUEDA E IA ---
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def _crear_llm_estructurado(schema_cls):
    """
    Inicializa el LLM de Groq con structured output y cadena de fallback
    para garantizar disponibilidad ante limites de tasa o variaciones de catalogo.
    """
    modelo_principal = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    modelos_candidatos = [
        modelo_principal,
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
    ]
    modelos_unicos = list(dict.fromkeys(modelos_candidatos))

    principal = ChatGroq(
        model_name=modelos_unicos[0],
        temperature=0,
        api_key=GROQ_API_KEY,
        max_retries=2
    ).with_structured_output(schema_cls)

    if len(modelos_unicos) > 1:
        fallbacks = [
            ChatGroq(model_name=m, temperature=0, api_key=GROQ_API_KEY, max_retries=2).with_structured_output(schema_cls)
            for m in modelos_unicos[1:]
        ]
        return principal.with_fallbacks(fallbacks)
    return principal

llm_estructurado_carreras = _crear_llm_estructurado(CarreraSchema)
llm_estructurado_resultado = _crear_llm_estructurado(ResultadoSchema)

# --- 2. PERSISTENCIA EN BASE DE DATOS ---
def guardar_en_db(datos_ia: CarreraSchema, user_id: int = 1):
    db: Session = SessionLocal()
    try:
        fecha_objeto = parser.parse(datos_ia.fecha).date()

        nueva_carrera = CarreraDB(
            user_id=user_id,
            nombre=datos_ia.nombre_oficial,
            deporte=datos_ia.deporte, 
            fecha=fecha_objeto,
            localizacion=datos_ia.lugar,
            distancia_resumen=", ".join(datos_ia.distancias),
            url_oficial=datos_ia.url_oficial,
            estado_inscripcion=datos_ia.estado_inscripcion.lower(),
            estado_planificacion="candidata"
        )

        db.add(nueva_carrera) 
        db.commit() 
        print(f"[OK] Guardada: {datos_ia.nombre_oficial} (User {user_id})")
    
    except ValueError as e:
        db.rollback()
        if "unique_violation" in str(e).lower() or "duplicate key" in str(e).lower():
            print(f"[Aviso] La carrera '{datos_ia.nombre_oficial}' ya existe para esa fecha.")
        else:
            print(f"[Error de validacion] {e}")
    except Exception as e:
        db.rollback()
        print(f"[Error de base de datos] {e}")
    finally:
        db.close()

# --- 3. EXTRACCION CENTRALIZADA ---
def buscar_y_extraer_datos(nombre_a_buscar: str, max_results: int = 6):
    """
    Busca en internet y extrae datos estructurados de la carrera.
    Retorna el objeto CarreraSchema.
    """
    if not nombre_a_buscar or not nombre_a_buscar.strip():
        raise ValueError("ERROR: El nombre de la carrera no puede estar vacio")
    
    año_actual = datetime.now().year
    query_optimizada = f"fecha celebracion y distancias oficiales carrera {nombre_a_buscar} {año_actual}"
    print(f"Buscando datos maestros de: {nombre_a_buscar}...")
    
    try:
        busqueda = tavily.search(query=query_optimizada, search_depth="advanced", max_results=max_results)
        
        if not busqueda.get('results'):
            raise ValueError(f"No se encontraron resultados para '{nombre_a_buscar}'")
            
        contexto = "\n---\n".join([res['content'] for res in busqueda['results']])
        
        if not contexto.strip():
            raise ValueError("El contexto de busqueda esta vacio")
        
    except Exception as e:
        print(f"[Error en busqueda Tavily] {e}")
        raise
    
    prompt = f"""
    Eres un analista experto en datos de competiciones deportivas.
    Tu objetivo es extraer informacion oficial, precisa y verificada de la carrera: {nombre_a_buscar}.
    
    Contexto encontrado en internet:
    {contexto}
    
    INSTRUCCIONES OBLIGATORIAS:
    1. FUENTES OFICIALES: Prioriza siempre plataformas oficiales de cronometraje (Global Tempo, Cruzando la Meta, Sportmaniacs, DorsalChip, CronoRacer, ChampionChip, etc.) y webs oficiales de ayuntamientos u organizadores. Descarta texto informal o publicaciones de redes sociales si contradicen los datos de los portales tecnicos.
    2. FECHA DE CELEBRACION (DIA DE LA CARRERA): 
       - Extrae la fecha exacta en la que se DISPUTA la carrera (el dia en que los atletas toman la salida) en formato YYYY-MM-DD.
       - NO la confundas con la fecha de cierre de inscripciones, la fecha de recogida de dorsales ni la fecha de publicacion del cartel/noticia.
       - Si una plataforma oficial de cronometraje (Cruzando La Meta, Global Tempo, etc.) o el reglamento indica la fecha de celebracion (por ejemplo '4 de octubre de 2026' o '25 de octubre de 2026'), utiliza exactamente esa fecha del evento (2026-10-04 o 2026-10-25).
       - NUNCA muevas arbitrariamente el ano hacia el futuro si la prueba consultada o documentada tiene fecha en {año_actual}.
       - Respeta la edicion y el ano de la convocatoria consultada.
    3. DISTANCIAS: Extrae todas las distancias en una lista (ejemplo: ['27 km', '12.5 km', '15 km']). No inventes kilometrajes.
    4. DEPORTE: Identifica correctamente: Running, Trail, Ciclismo, Gravel o Triatlon.
    5. LUGAR: Municipio y provincia oficial.
    6. URL OFICIAL: Si encuentras el enlace del portal de inscripcion o web del evento, incluyelo en url_oficial.
    """
    
    try:
        datos_extraidos = llm_estructurado_carreras.invoke(prompt)
        return datos_extraidos
    except ValueError as e:
        raise
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower():
            print("Limite de cuota excedido (Groq 429).")
            raise ValueError("El servicio de IA esta temporalmente saturado (Rate Limit 429). Por favor espera un minuto antes de intentar de nuevo.") from e
        
        print(f"[Error al procesar con el LLM] {e}")
        raise

# --- 4. CLI INTERACTIVO ---
def ejecutar_proyecto(nombre_a_buscar, user_id: int = 1):
    datos_extraidos = buscar_y_extraer_datos(nombre_a_buscar)
    
    print("\n" + "="*30)
    print("DATOS ENCONTRADOS")
    print("="*30)
    print(f"Nombre: {datos_extraidos.nombre_oficial}")
    print(f"Deporte: {datos_extraidos.deporte}")
    print(f"Fecha: {datos_extraidos.fecha}")
    print(f"Lugar: {datos_extraidos.lugar}")
    print(f"Distancias: {', '.join(datos_extraidos.distancias)}")
    print(f"URL: {datos_extraidos.url_oficial}")
    print(f"Estado: {datos_extraidos.estado_inscripcion}")
    print("="*30)
    
    confirmacion = input("\n¿Los datos son correctos? (s/n): ").lower()

    if confirmacion == 's':
        user_id = int(input("ID de usuario (1 para demo): ") or 1)
        guardar_en_db(datos_extraidos, user_id)
    else:
        print("Operacion cancelada por el usuario. Los datos no se han guardado.")

# --- 5. FUNCION PARA API WEB ---
def procesar_carrera_desde_web(nombre_a_buscar: str, user_id: int = 1):
    print(f"Solicitud web de busqueda: {nombre_a_buscar}...")
    try:
        datos_extraidos = buscar_y_extraer_datos(nombre_a_buscar, max_results=5)
        guardar_en_db(datos_extraidos, user_id)
        return datos_extraidos
    except Exception as e:
        print(f"[Error procesando carrera desde web] {e}")
        raise

def buscar_resultado_usuario(nombre_carrera: str, año: int, nombre: str):
    query_principal = f"{nombre_carrera} {año} clasificacion {nombre}"
    print(f"Buscando clasificacion: {query_principal}...")
    
    try:
        busqueda = tavily.search(query=query_principal, search_depth="advanced", max_results=10)
        
        if not busqueda.get('results'):
            print("Busqueda especifica sin resultados, probando listados generales...")
            query_general = f"{nombre_carrera} {año} resultados pdf completo"
            busqueda = tavily.search(query=query_general, search_depth="advanced", max_results=5)
             
        if not busqueda.get('results'):
            return ResultadoSchema(tiempo_oficial=None, posicion_general=None, posicion_categoria=None, ritmo_medio=None)
            
        contexto = "\n".join([
            f"--- FUENTE: {res['url']} ---\nTITULO: {res['title']}\nCONTENIDO: {res['content']}\n" 
            for res in busqueda['results']
        ])
        
    except Exception as e:
        print(f"[Error en busqueda Tavily] {e}")
        raise
    
    prompt = f"""
    Eres un experto rastreador de resultados deportivos.
    
    OBJETIVO: Encontrar el tiempo de "{nombre}" en "{nombre_carrera}" del año {año}.
    
    CONTEXTO (Resultados de busqueda):
    {contexto}
    
    INSTRUCCIONES DE EXTRACCION:
    1. FLEXIBILIDAD DE NOMBRE: Busca "{nombre}" pero acepta variaciones como:
       - "Apellidos, Nombre" (Ej: "Espin Rodriguez, Jaime")
       - Mayusculas/Minusculas
       - Falta de tildes (Ej: "Jaime Espin")
    
    2. SI ENCUENTRAS EL DATO:
       - Extrae Tiempo (hh:mm:ss), Posicion General y Categoria si existen.
       - Ritmo (min/km).
    
    3. SI NO ENCUENTRAS AL CORREDOR EXACTO:
       - Devuelve null en los campos. 
       - NO inventes datos.
       
    4. IMPORTANTE: Muchas veces los resultados estan en formato "Pos. Nombre Tiempo". Busca ese patron.
    """
    
    try:
        datos_extraidos = llm_estructurado_resultado.invoke(prompt)
        return datos_extraidos
    except ValueError as e:
        raise
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower():
            print("Limite de cuota excedido (Groq 429).")
            raise ValueError("El servicio de IA esta temporalmente saturado (Rate Limit 429). Intenta mas tarde.") from e
        print(f"[Error al procesar con el LLM] {e}")
        raise

def guardar_resultado_db(datos_ia: ResultadoSchema, nombre_carrera: str, año: int, user_id: int):
    if not datos_ia or not datos_ia.tiempo_oficial or datos_ia.tiempo_oficial == "No encontrado":
        return

    import unicodedata
    import re

    def _sin_acentos_local(texto: str) -> str:
        return ''.join(
            c for c in unicodedata.normalize('NFD', str(texto))
            if unicodedata.category(c) != 'Mn'
        ).lower()

    db: Session = SessionLocal()
    try:
        carreras_usuario = db.query(CarreraDB).filter(CarreraDB.user_id == user_id).all()
        nb = _sin_acentos_local(nombre_carrera)

        carrera_existente = None
        # 1. Coincidencia directa o contenida completa
        for c in carreras_usuario:
            nc = _sin_acentos_local(c.nombre)
            if nc == nb or nb in nc or nc in nb:
                carrera_existente = c
                break

        # 2. Coincidencia por palabras clave nucleares (evitando genericas)
        if not carrera_existente:
            tokens = [
                t for t in re.sub(r'[^\w\s]', ' ', nb).split()
                if len(t) >= 4 and t not in ['carrera', 'trail', 'media', 'maraton', 'edicion', 'prueba', 'popular', 'granada', 'totalenergies']
            ]
            if tokens:
                for c in carreras_usuario:
                    nc = _sin_acentos_local(c.nombre)
                    if all(t in nc for t in tokens):
                        carrera_existente = c
                        break
                if not carrera_existente:
                    for c in carreras_usuario:
                        nc = _sin_acentos_local(c.nombre)
                        if any(t in nc for t in tokens):
                            carrera_existente = c
                            break

        if not carrera_existente:
            print(f"Aviso: La carrera '{nombre_carrera}' no se pudo asociar a ninguna registrada del usuario {user_id}.")
            return

        resultado_existente = db.query(ResultadoDB).filter(ResultadoDB.carrera_id == carrera_existente.id).first()

        if resultado_existente:
            resultado_existente.tiempo_oficial = datos_ia.tiempo_oficial
            resultado_existente.posicion_general = datos_ia.posicion_general
            resultado_existente.posicion_categoria = datos_ia.posicion_categoria
            resultado_existente.ritmo_medio = datos_ia.ritmo_medio
            resultado_existente.confianza = int(datos_ia.confianza * 100) if datos_ia.confianza else None
            resultado_existente.comentarios = f"Auto {año}"
        else:
            nuevo_resultado = ResultadoDB(
                carrera_id=carrera_existente.id,
                tiempo_oficial=datos_ia.tiempo_oficial,
                posicion_general=datos_ia.posicion_general,
                posicion_categoria=datos_ia.posicion_categoria,
                ritmo_medio=datos_ia.ritmo_medio,
                confianza=int(datos_ia.confianza * 100) if datos_ia.confianza else None,
                comentarios=f"Auto {año}"
            )
            db.add(nuevo_resultado)

        db.commit()
        print(f"[OK] Resultado guardado para: {nombre_carrera}")

    except Exception as e:
        db.rollback()
        print(f"[Error al guardar resultado] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    carrera = input("Carrera a añadir: ")
    user_id = int(input("ID de usuario (1 para demo): ") or 1)
    ejecutar_proyecto(carrera, user_id)
