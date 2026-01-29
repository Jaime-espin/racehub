#Este script constituye el núcleo del sistema de ingesta 
#de datos. Utiliza un Agente de IA (Llama 3.3 vía Groq) y
#el motor de búsqueda Tavily para automatizar la extracción
#de información deportiva. Los datos son validados mediante
#Pydantic y persistidos en PostgreSQL, implementando una 
#lógica de control de duplicados basada en restricciones de
#integridad referencial.

import os
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from dateutil import parser
from sqlalchemy.orm import Session
from database import SessionLocal, CarreraDB

load_dotenv()

# Validación de variables de entorno requeridas
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("❌ ERROR: TAVILY_API_KEY no está configurada en el archivo .env")
if not GROQ_API_KEY:
    raise ValueError("❌ ERROR: GROQ_API_KEY no está configurada en el archivo .env")

# --- 1. SCHEMA ---
#Obliga a la IA a que su respuesta tenga una estructura fija.
# Si la IA intenta responder con un párrafo,
# Pydantic lanzará un error.
# Field(description=...): La IA lee estas descripciones 
# para saber qué tipo de contenido debe poner en cada variable.

class CarreraSchema(BaseModel):
    nombre_oficial: str = Field(description="Nombre oficial", min_length=3)
    deporte: str = Field(description="Obligatorio: Running, Trail, Ciclismo, Gravel o Triatlón")
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
            # Validar que sea parseable como fecha
            parser.parse(v)
            return v
        except:
            raise ValueError("La fecha debe estar en formato válido (preferentemente YYYY-MM-DD)")
    
    @validator('deporte')
    def validar_deporte(cls, v):
        deportes_validos = ['running', 'trail', 'ciclismo', 'gravel', 'triatlón', 'triatlon', 'snow running']
        if v.lower() not in deportes_validos:
            # Aceptar el valor pero advertir
            print(f"⚠️ Advertencia: Deporte '{v}' no está en la lista estándar")
        return v

#---Motores---
tavily = TavilyClient(api_key=TAVILY_API_KEY)
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0, api_key=GROQ_API_KEY)
llm_estructurado = llm.with_structured_output(CarreraSchema)
#Convierte a un modelo de lenguaje (que es un generador de
#texto probabilístico) en una función de software 
#determinista que devuelve un objeto Python.

# --- 2. FUNCIÓN DE GUARDADO ---
def guardar_en_db(datos_ia: CarreraSchema):
    db: Session = SessionLocal()
    try:
        fecha_objeto = parser.parse(datos_ia.fecha).date()

        nueva_carrera = CarreraDB(
            nombre=datos_ia.nombre_oficial,
            deporte=datos_ia.deporte, # Ahora sí lo pasamos
            fecha=fecha_objeto,
            localizacion=datos_ia.lugar,
            distancia_resumen=", ".join(datos_ia.distancias),
            url_oficial=datos_ia.url_oficial,
            estado_inscripcion=datos_ia.estado_inscripcion.lower() # Normalizamos a minúsculas
        )

        db.add(nueva_carrera) #mete la carrera en una lista de espera
        db.commit() #Escribe
        print(f"✅ Guardada: {datos_ia.nombre_oficial} ({datos_ia.deporte})")
    
    except Exception as e:
        #Si intentas insertar una carrera duplicada (misma fecha y nombre), la base de datos lanzará un error.
        db.rollback()
        if "unique_violation" in str(e).lower() or "duplicate key" in str(e).lower():
            print(f"⚠️ Aviso: La carrera '{datos_ia.nombre_oficial}' ya existe para esa fecha.")
        else:
            print(f"❌ Error al guardar: {e}")
    finally:
        db.close()

# --- 3. FUNCIÓN COMÚN DE BÚSQUEDA Y EXTRACCIÓN ---
def buscar_y_extraer_datos(nombre_a_buscar: str, max_results: int = 6):
    """
    Función centralizada que busca en internet y extrae datos estructurados.
    Retorna el objeto CarreraSchema extraído por la IA.
    """
    if not nombre_a_buscar or not nombre_a_buscar.strip():
        raise ValueError("❌ ERROR: El nombre de la carrera no puede estar vacío")
    
    año_actual = datetime.now().year
    query_optimizada = f"fecha y distancias oficiales carrera {nombre_a_buscar} {año_actual}"
    print(f"Buscando datos maestros de: {nombre_a_buscar}...")
    
    try:
        busqueda = tavily.search(query=query_optimizada, search_depth="advanced", max_results=max_results)
        
        if not busqueda.get('results'):
            raise ValueError(f"❌ No se encontraron resultados para '{nombre_a_buscar}'")
            
        contexto = "\n---\n".join([res['content'] for res in busqueda['results']])
        
        if not contexto.strip():
            raise ValueError("❌ El contexto de búsqueda está vacío")
        
    except Exception as e:
        print(f"❌ Error en la búsqueda con Tavily: {e}")
        raise
    
    prompt = f"""
    Eres un analista de datos deportivos. Tu objetivo es extraer info precisa de: {nombre_a_buscar}.
    
    Contexto encontrado en internet:
    {contexto}
    
    INSTRUCCIONES PARA EVITAR ERRORES:
    1. FECHA: Busca la fecha de la PRÓXIMA edición. Si ves fechas de 2024 o anteriores, DESCÁRTALAS. Solo acepta fechas iguales o posteriores a {año_actual}
    2. DISTANCIA: Busca el apartado de 'Recorrido' o 'Reglamento'. No inventes km. Si hay varias distancias, lístalas todas.
    3. VERIFICACIÓN: Si los datos parecen contradictorios, prioriza la fuente que parezca la web oficial (.com o .es del evento).
    4. DEPORTE: Identifica correctamente el tipo de deporte (Running, Trail, Ciclismo, Gravel, Triatlón, etc.).
    """
    
    try:
        datos_extraidos = llm_estructurado.invoke(prompt)
        return datos_extraidos
    except Exception as e:
        print(f"❌ Error al procesar con el LLM: {e}")
        raise

# --- 4. FUNCIÓN PARA EJECUCIÓN INTERACTIVA (CLI) ---
def ejecutar_proyecto(nombre_a_buscar):
    """
    Versión interactiva con confirmación humana para uso desde terminal.
    """
    datos_extraidos = buscar_y_extraer_datos(nombre_a_buscar)
    
    # Mostrar datos para validación humana
    print("\n" + "="*30)
    print("📋 DATOS ENCONTRADOS POR LA IA")
    print("="*30)
    print(f"🏆 Nombre: {datos_extraidos.nombre_oficial}")
    print(f"🚴 Deporte: {datos_extraidos.deporte}")
    print(f"📅 Fecha: {datos_extraidos.fecha}")
    print(f"📍 Lugar: {datos_extraidos.lugar}")
    print(f"📏 Distancias: {', '.join(datos_extraidos.distancias)}")
    print(f"🔗 URL: {datos_extraidos.url_oficial}")
    print(f"📝 Estado: {datos_extraidos.estado_inscripcion}")
    print("="*30)
    
    confirmacion = input("\n¿Los datos son correctos? (s/n): ").lower()

    if confirmacion == 's':
        guardar_en_db(datos_extraidos)
    else:
        print("❌ Operación cancelada por el usuario. Los datos no se han guardado.")

# --- 5. FUNCIÓN PARA API WEB (sin interacción humana) ---
def procesar_carrera_desde_web(nombre_a_buscar: str):
    """
    Función para la API web: Busca, extrae y guarda automáticamente.
    Sin preguntas de consola.
    """
    print(f"🌍 WEB solicitando búsqueda de: {nombre_a_buscar}...")
    
    try:
        datos_extraidos = buscar_y_extraer_datos(nombre_a_buscar, max_results=5)
        guardar_en_db(datos_extraidos)
        return datos_extraidos
    except Exception as e:
        print(f"❌ Error al procesar carrera desde web: {e}")
        raise

if __name__ == "__main__":
    carrera = input("Carrera a añadir: ")
    ejecutar_proyecto(carrera)