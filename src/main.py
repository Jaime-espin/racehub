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
from pydantic import BaseModel, Field
from typing import List, Optional
from dateutil import parser
from sqlalchemy.orm import Session
from src.database import SessionLocal, CarreraDB

load_dotenv()

# --- 1. SCHEMA ---
#Obliga a la IA a que su respuesta tenga una estructura fija.
# Si la IA intenta responder con un párrafo,
# Pydantic lanzará un error.
# Field(description=...): La IA lee estas descripciones 
# para saber qué tipo de contenido debe poner en cada variable.
class CarreraSchema(BaseModel):
    nombre_oficial: str = Field(description="Nombre oficial")
    deporte: str = Field(description="Obligatorio: Running, Trail, Ciclismo, Gravel o Triatlón")
    fecha: str = Field(description="Formato YYYY-MM-DD")
    lugar: str
    distancias: List[str]
    url_oficial: Optional[str]
    # Nuevo campo para el estado
    estado_inscripcion: str = Field(description="Solo puede ser: 'abierta', 'cerrada' o 'pendiente'")

#---Motores---
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
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

# --- 3. PROMPT ---
def ejecutar_proyecto(nombre_a_buscar):
    # Paso A:
    año_actual = datetime.now().year
    query_optimizada = f"fecha y distancias oficiales carrera {nombre_a_buscar} {año_actual}"
    print(f"Buscando datos maestros de: {nombre_a_buscar}...")
    
    busqueda = tavily.search(query=query_optimizada, search_depth="advanced", max_results=6)
    #Juntamos los resultados de 6 páginas web en un solo string de texto.
    contexto = "\n---\n".join([res['content'] for res in busqueda['results']])
    
    # Paso B: Prompt con "Cadena de Pensamiento" (Chain of Thought)
    prompt = f"""
    Eres un analista de datos deportivos. Tu objetivo es extraer info precisa de: {nombre_a_buscar}.
    
    Contexto encontrado en internet:
    {contexto}
    
    INSTRUCCIONES PARA EVITAR ERRORES:
    1. FECHA: Busca la fecha de la PRÓXIMA edición (invierno 2025 o 2026). Si ves fechas de 2024 o anteriores, DESCÁRTALAS. Solo acepta fechas iguales o posteriores a {año_actual}
    2. DISTANCIA: Busca el apartado de 'Recorrido' o 'Reglamento'. No inventes km. Si hay varias distancias, lístalas todas.
    3. VERIFICACIÓN: Si los datos parecen contradictorios, prioriza la fuente que parezca la web oficial (.com o .es del evento).
    4. DEPORTE: Para esta carrera específica, el deporte es 'Snow Running' o 'Trail'.
    """
    
    datos_extraidos = llm_estructurado.invoke(prompt)
    
    # --- NUEVO: PASO DE VALIDACIÓN HUMANA ---
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
    

if __name__ == "__main__":
    carrera = input("Carrera a añadir: ")
    ejecutar_proyecto(carrera)