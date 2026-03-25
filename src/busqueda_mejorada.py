# Módulo mejorado para búsqueda de resultados
# Reemplaza la función buscar_resultado_usuario() en main.py

import os
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from tavily import TavilyClient
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# --- CLIENTE DE BÚSQUEDA MEJORADO ---

class ResultadoSchema(BaseModel):
    tiempo_oficial: Optional[str] = Field(None, description="Tiempo Oficial (ej: '1:30:45'). Si no se encuentra, dejar null")
    posicion_general: Optional[int] = Field(None, description="Posición numérica absoluta. Null si no hay datos.")
    posicion_categoria: Optional[int] = Field(None, description="Posición en su categoría. Null si no hay datos.")
    ritmo_medio: Optional[str] = Field(None, description="Ritmo medio (ej: '4:30 min/km'). Null si no hay datos.")

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0, 
    api_key=os.getenv("GROQ_API_KEY"),
    max_retries=3
)
llm_estructurado_resultado = llm.with_structured_output(ResultadoSchema)

# --- ESTRATEGIA 1: URLs ALTERNATIVAS COMUNES ---

def generar_urls_alternativas(nombre_carrera: str, dominio_base: str) -> List[str]:
    """
    Genera URLs comunes donde podrían estar los resultados
    Ej: si el sitio es 'ejemplo.com/carrera', intenta:
    - ejemplo.com/resultados/
    - ejemplo.com/clasificación/
    - ejemplo.com/standings/
    """
    urls = []
    
    # Rutas comunes de resultados
    rutas_comunes = [
        '/resultados/',
        '/resultados',
        '/classification/',
        '/clasificacion/',
        '/clasificación/',
        '/standings/',
        '/scores/',
        '/timing/',
        '/finishers/',
        '/participantes/',
        '/corredores/',
        '/runners/',
        '/resultados.html',
        '/resultados/index.html',
        '/descargas/',
        '/downloads/',
    ]
    
    # Intentar agregar los tipos de extensión comúnmente usados
    base = dominio_base.rstrip('/')
    
    for ruta in rutas_comunes:
        urls.append(f"{base}{ruta}")
    
    # Para búsqueda por nombre de archivo
    slug_carrera = nombre_carrera.lower().replace(' ', '-')
    urls.append(f"{base}/resultados/{slug_carrera}/")
    urls.append(f"{base}/resultados-{slug_carrera}/")
    
    return urls

def extraer_dominio(url: str) -> str:
    """Extrae el dominio base de una URL"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

# --- ESTRATEGIA 2: BÚSQUEDA MEJORADA CON FALLBACKS ---

def buscar_resultado_usuario_v2(nombre_carrera: str, año: int, nombre: str, url_oficial: Optional[str] = None):
    """
    Versión mejorada de búsqueda:
    1. Intenta URLs oficiales alternativas si se proporciona URL
    2. Búsqueda con Tavily (web indexada)
    3. Búsqueda en portales conocidos
    4. Fallback a búsqueda general
    """
    
    # PASO 1: Si hay URL oficial, intentar rutas alternativas primero
    contexto = ""
    encontrado = False
    
    if url_oficial:
        print(f"🌐 Intentando búsqueda en dominio oficial: {url_oficial}")
        dominio = extraer_dominio(url_oficial)
        urls_alternativas = generar_urls_alternativas(nombre_carrera, dominio)
        
        for url in urls_alternativas[:5]:  # Limitar a 5 intentos
            try:
                print(f"  → Intentando: {url}")
                import requests
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200 and len(resp.text) > 100:
                    contexto = f"--- FUENTE OFICIAL: {url} ---\n{resp.text[:3000]}\n"
                    encontrado = True
                    break
            except Exception as e:
                print(f"    ❌ {e}")
                continue
    
    # PASO 2: Búsqueda mejorada con Tavily
    print(f"🔎 Búsqueda en web (Tavily)...")
    
    # Intentar múltiples queries con diferentes palabras clave
    queries = [
        f"{nombre_carrera} {año} clasificación resultados {nombre}",
        f"{nombre_carrera} {año} resultados {nombre} tiempo",
        f"{nombre_carrera} '{año}' {nombre} posición",
        f"\"{nombre_carrera}\" {año} {nombre}",
        f"{nombre_carrera.split()[0]} {año} results {nombre}",
    ]
    
    for query in queries:
        try:
            busqueda = tavily.search(query=query, search_depth="advanced", max_results=10)
            
            if busqueda.get('results') and len(busqueda['results']) > 0:
                print(f"  ✅ Encontrados {len(busqueda['results'])} resultados")
                contexto += "\n".join([
                    f"--- FUENTE: {res['url']} ---\nTÍTULO: {res['title']}\nCONTENIDO: {res['content'][:1500]}\n" 
                    for res in busqueda['results'][:5]
                ])
                encontrado = True
                break
        except Exception as e:
            print(f"  ⚠️ Query '{query[:50]}...' falló: {e}")
            continue
    
    # Si aún no hay contexto, intenta búsqueda muy general
    if not encontrado:
        print(f"⚠️ Búsqueda específica sin resultados. Intentando general...")
        try:
            busqueda_general = tavily.search(
                query=f"{nombre_carrera} {año} pdf resultados",
                search_depth="basic",
                max_results=5
            )
            if busqueda_general.get('results'):
                contexto = "\n".join([
                    f"--- {res['url']} ---\n{res['content'][:1000]}\n" 
                    for res in busqueda_general['results']
                ])
        except Exception as e:
            print(f"❌ Error en búsqueda general: {e}")
    
    # Si aún no hay nada, devolver vacío
    if not contexto:
        return ResultadoSchema(
            tiempo_oficial=None,
            posicion_general=None,
            posicion_categoria=None,
            ritmo_medio=None
        )
    
    # PASO 3: Procesar con IA
    print(f"🤖 Extrayendo datos con IA...")
    
    prompt = f"""
Eres un experto rastreador de resultados deportivos. Tu tarea es EXTREMADAMENTE RIGUROSA.

OBJETIVO: Encontrar datos de "{nombre}" en la carrera "{nombre_carrera}" ({año}).

CONTEXTO (Resultados de búsqueda web):
{contexto[:4000]}

INSTRUCCIONES:
1. FLEXIBILIDAD DE NOMBRE (crucial):
   - Busca variaciones: "Apellidos, Nombre", "NOMBRE APELLIDO", sin tildes, mayúsculas/minúsculas
   - Ej: "{nombre}" → "Espin Rodríguez" → "ESPIN, JAIME" → "Rodríguez Espín"

2. FORMATO TÍPICO DE RESULTADOS:
   - Pos. | Nombre | Tiempo | Ritmo | Categoría
   - #123 NombreCorrector 1:30:45 4:30/km 40-50M
   - En ocasiones: "Rodríguez,Juan | 1:30:45 | 1º Cat"

3. EXTRAE SI ENCUENTRAS:
   - ⏱️ Tiempo: formato HH:MM:SS o similar
   - 🏆 Pos. General: número entero
   - 📊 Pos. Categoría: número o si dice "1º Cat" extrae 1
   - ⚡ Ritmo: formato MIN:SS/km o MIN:SS/mi

4. SI NO ENCUENTRAS DATOS EXACTOS:
   - Devuelve NULL
   - NO ALUCINES NI INVENTES DATOS BAJO NINGUNA CIRCUNSTANCIA
   - Es mejor devolver null que datos falsos

5. CONTEXTO: Ten en cuenta que hoy es {datetime.now().year}, así que {año} fue hace {datetime.now().year - año} años.
"""
    
    try:
        datos_extraidos = llm_estructurado_resultado.invoke(prompt)
        return datos_extraidos
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Rate limit" in error_str:
            print(f"⏳ Límite de cuota excedido (Groq 429).")
            raise ValueError("⚠️ El servicio está saturado. Intenta más tarde.")
        print(f"❌ Error al procesar con IA: {e}")
        raise


# --- ESTRATEGIA 3: SUBIDA DE ARCHIVO (Para agregar a API después) ---

def buscar_resultado_en_archivo(archivo_path: str, nombre: str, año: int) -> ResultadoSchema:
    """
    Busca resultado en un archivo local (PDF o CSV)
    
    Uso: permitir que usuario suba PDF/CSV de resultados directamente
    Requiere: pip install pypdf python-docx
    """
    
    # Determinar tipo de archivo
    if archivo_path.endswith('.pdf'):
        contenido = _extraer_pdf(archivo_path)
    elif archivo_path.endswith('.csv'):
        contenido = _extraer_csv(archivo_path)
    elif archivo_path.endswith('.xlsx'):
        contenido = _extraer_excel(archivo_path)
    else:
        contenido = open(archivo_path, 'r', encoding='utf-8').read()
    
    # Procesar con IA igual que búsqueda web
    prompt = f"""
Eres un experto en extracción de datos deportivos.

Archivo contenido:
{contenido[:3000]}

Busca datos de "{nombre}" en el año {año}:
- Tiempo oficial
- Posición general
- Posición en categoría
- Ritmo promedio

Si no encuentras al corredor exacto, devuelve NULL.
NO ALUCINES DATOS.
"""
    
    try:
        return llm_estructurado_resultado.invoke(prompt)
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return ResultadoSchema()

def _extraer_pdf(archivo_path: str) -> str:
    """Extrae texto de PDF"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(archivo_path)
        texto = ""
        for page_num in range(min(10, len(reader.pages))):  # Primeras 10 páginas
            page = reader.pages[page_num]
            texto += page.extract_text() + "\n"
        return texto
    except ImportError:
        return "[PDF - Requiere pip install PyPDF2]"

def _extraer_csv(archivo_path: str) -> str:
    """Extrae contenido de CSV"""
    try:
        import csv
        contenido = []
        with open(archivo_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            contenido = ['\t'.join(row) for row in reader]
        return '\n'.join(contenido[:100])
    except Exception as e:
        return f"[Error leyendo CSV: {e}]"

def _extraer_excel(archivo_path: str) -> str:
    """Extrae contenido de Excel"""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(archivo_path)
        contenido = []
        for row in wb.active.iter_rows(max_row=50):
            contenido.append('\t'.join([str(cell.value) for cell in row]))
        return '\n'.join(contenido)
    except ImportError:
        return "[Excel - Requiere pip install openpyxl]"


# Para usar en api.py, simplemente reemplazar la función:
# from src.busqueda_mejorada import buscar_resultado_usuario_v2
# y cambiar "buscar_resultado_usuario" por "buscar_resultado_usuario_v2"
