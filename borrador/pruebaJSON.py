import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tavily import TavilyClient
from pydantic import BaseModel, Field # <-- Librería para estructurar datos

load_dotenv()

# 1. Definimos el "molde" de la carrera
class CarreraSchema(BaseModel):
    nombre_oficial: str = Field(description="Nombre completo de la carrera")
    fecha: str = Field(description="Fecha en formato YYYY-MM-DD. Si no tiene año, asume 2025.")
    lugar: str = Field(description="Ciudad y país")
    distancias: List[str] = Field(description="Lista de distancias (ej: ['10K', '42K'])")
    url_oficial: Optional[str] = Field(description="URL de la página de inscripciones o web oficial")

# 2. Configuración
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Esto es la magia: obligamos al LLM a seguir el esquema de la clase CarreraSchema
llm_estructurado = llm.with_structured_output(CarreraSchema)

def obtener_carrera_estructurada(nombre_busqueda):
    print(f"--- Procesando: {nombre_busqueda} ---")
    
    # Búsqueda
    respuesta_busqueda = tavily.search(query=nombre_busqueda, search_depth="advanced")
    contexto = "\n---\n".join([res['content'] for res in respuesta_busqueda['results']])
    
    # Extracción
    print("Extrayendo datos estructurados...")
    
    # Ahora invocamos al modelo estructurado
    resultado = llm_estructurado.invoke(f"Extrae la info de la carrera basándote en: {contexto}")
    
    return resultado

if __name__ == "__main__":
    carrera = obtener_carrera_estructurada("Maratón de Madrid 2025")
    
    print("\n--- OBJETO PYTHON RECUPERADO ---")
    print(f"Nombre: {carrera.nombre_oficial}")
    print(f"Fecha: {carrera.fecha}")
    print(f"Distancias: {', '.join(carrera.distancias)}")
    print(f"URL: {carrera.url_oficial}")

#BaseModel: Hemos creado una clase que define exactamente qué campos queremos.
#with_structured_output: Esta función de LangChain cambia el comportamiento del modelo. En lugar de generar texto, el modelo genera un JSON interno y LangChain lo convierte automáticamente en un objeto de Python.
#Tipado de datos: Fíjate que distancias es una List[str]. La IA ahora meterá cada distancia en una lista de Python, lo cual es perfecto para procesarlo luego.