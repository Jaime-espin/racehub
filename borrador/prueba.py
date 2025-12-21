import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tavily import TavilyClient

# Cargar las llaves del archivo .env
load_dotenv()

# 1. Configurar el buscador (Cliente oficial de Tavily)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 2. Configurar el cerebro (Groq)
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def probar_flujo(nombre_carrera):
    print(f"--- Buscando información de: {nombre_carrera} ---")
    
    try:
        # Usamos el cliente oficial para buscar
        # 'search_depth="advanced"' ayuda a encontrar datos más precisos
        respuesta_busqueda = tavily.search(query=nombre_carrera, search_depth="advanced")
        
        # Extraemos solo el contenido de los resultados para el LLM
        contexto = "\n---\n".join([res['content'] for res in respuesta_busqueda['results']])
        
        print(f"Búsqueda finalizada. Analizando contenido con IA...")

        prompt = f"""
        Eres un asistente experto en deportes de resistencia. 
        Analiza el siguiente texto extraído de varias webs sobre la carrera '{nombre_carrera}':
        
        {contexto}
        
        Extrae y resume:
        - Nombre oficial:
        - Fecha:
        - Lugar:
        - Distancias:
        - URL de inscripción:
        """
        
        respuesta_ia = llm.invoke(prompt)
        print("\n--- Resultado Final ---")
        print(respuesta_ia.content)
        
    except Exception as e:
        print(f"Se produjo un error: {e}")

if __name__ == "__main__":
    probar_flujo("Maratón de Madrid 2025")
    
#load_dotenv(): Lee tu archivo secreto y carga las llaves en la memoria del programa.
#TavilySearchResults: Hace el trabajo sucio de buscar en Google y traerte el texto relevante.
#ChatGroq: Envía ese texto a los servidores de Groq para que Llama 3 lo procese.