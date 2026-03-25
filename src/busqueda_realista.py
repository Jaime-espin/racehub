# Búsqueda mejorada v2 - Enfoque realista
# Con soporte para portales conocidos + subida de archivos

import os
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Optional, List, Dict
from tavily import TavilyClient
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# --- CLIENTE DE BÚSQUEDA ---

class ResultadoSchema(BaseModel):
    tiempo_oficial: Optional[str] = Field(None, description="Tiempo Oficial (ej: '1:30:45')")
    posicion_general: Optional[int] = Field(None, description="Posición numérica absoluta")
    posicion_categoria: Optional[int] = Field(None, description="Posición en su categoría")
    ritmo_medio: Optional[str] = Field(None, description="Ritmo medio (ej: '4:30 min/km')")
    confianza: Optional[float] = Field(None, description="Nivel de confianza 0-1")

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0, 
    api_key=os.getenv("GROQ_API_KEY"),
    max_retries=3
)
llm_estructurado = llm.with_structured_output(ResultadoSchema)

# --- 1. BASE DE DATOS DE PORTALES CONOCIDOS ---

PORTALES_CONOCIDOS = {
    "sportmaniacs": {
        "dominios": ["sportmaniacs.com", "sportmaniacs.es"],
        "patron": r"(?P<nombre>[A-Z][a-záéíóú\s]*)\s+(?P<tiempo>\d{1,2}:\d{2}:\d{2})\s+(?P<posicion>\d+)",
        "url_buscar": "https://www.sportmaniacs.com/es/carreras",
        "indicios": ["sportmaniacs", "clasificacion", "corredor"]
    },
    "chronoempresa": {
        "dominios": ["chronoempresa.com"],
        "patron": r"(\d+)\s+([A-Z][a-záéíóú\s]+)\s+(\d{1,2}:\d{2}:\d{2})",
        "url_buscar": "https://www.chronoempresa.com",
        "indicios": ["chrono", "clasificacion"]
    },
    "mylaps": {
        "dominios": ["mylaps.com", "timing.mylaps.com"],
        "patron": r"(?P<posicion>\d+)\s+(?P<nombre>[A-Z][a-z\s]+)\s+(?P<tiempo>\d{1,2}:\d{2}:\d{2})",
        "indicios": ["mylaps", "competicion"]
    },
    "chipiming": {
        "dominios": ["chiptiming.com"],
        "patron": r"(?P<posicion>\d+)\s+(?P<nombre>[A-Z][a-z\s]+)\s+(?P<tiempo>\d{1,2}:\d{2}:\d{2})",
        "indicios": ["chip", "timing"]
    }
}

# --- 2. VALIDACIÓN RIGUROSA DE DATOS ---

def validar_tiempo(tiempo_str: Optional[str]) -> bool:
    """Valida que el tiempo tenga un formato razonable"""
    if not tiempo_str:
        return False
    # Formato: HH:MM:SS
    if not re.match(r'^\d{1,2}:\d{2}:\d{2}$', tiempo_str):
        return False
    # Validar que sea un tiempo razonable (no > 5 horas para running)
    partes = tiempo_str.split(':')
    horas = int(partes[0])
    return 0 < horas < 6  # Asumiendo eventos de hasta 5 horas

def validar_posicion(pos: Optional[int]) -> bool:
    """Valida que la posición sea lógica"""
    if pos is None:
        return False
    # Una posición razonable en una carrera
    return 1 <= pos <= 10000

def calcular_confianza(datos: Dict) -> float:
    """
    Calcula nivel de confianza en los datos extraídos
    Basado en: validación de campos, coherencia, etc.
    """
    confianza = 0.5  # Base
    
    # Si todos los campos están presentes y válidos
    campos_validos = 0
    if datos.get('tiempo_oficial') and validar_tiempo(datos['tiempo_oficial']):
        campos_validos += 1
        confianza += 0.15
    
    if datos.get('posicion_general') and validar_posicion(datos['posicion_general']):
        campos_validos += 1
        confianza += 0.15
    
    if datos.get('ritmo_medio'):
        campos_validos += 1
        confianza += 0.1
    
    # Menos confianza si solo un campo
    if campos_validos == 1:
        confianza = 0.4
    elif campos_validos == 0:
        confianza = 0.0
    
    return min(1.0, confianza)

# --- 3. BÚSQUEDA MEJORADA CON VALIDACIÓN ---

def buscar_resultado_realista(
    nombre_carrera: str,
    año: int,
    nombre: str,
    url_oficial: Optional[str] = None
) -> ResultadoSchema:
    """
    Versión realista que:
    1. Intenta acceso directo al URL si se proporciona
    2. Detecta portal conocido
    3. Intenta búsqueda específica
    4. Valida datos
    5. Evita alucinaciones
    """
    
    print(f"🔎 Búsqueda: {nombre} en {nombre_carrera} ({año})")
    
    # PASO 1: Si hay URL directo, intentar acceso inmediato
    if url_oficial:
        print(f"  📌 URL directo proporcionado")
        resultado = _buscar_en_url_directo(url_oficial, nombre, nombre_carrera, año)
        if resultado.tiempo_oficial:
            print(f"  ✅ Datos extraídos del URL")
            return resultado
    
    # PASO 2: Detectar portal conocido y buscar específicamente
    portal_detectado = None
    if url_oficial:
        for portal_nombre, config in PORTALES_CONOCIDOS.items():
            if any(dominio in url_oficial.lower() for dominio in config.get("dominios", [])):
                portal_detectado = portal_nombre
                print(f"  ✅ Portal detectado: {portal_nombre}")
                break
    
    if portal_detectado:
        resultado = _buscar_en_portal_conocido(
            portal_detectado,
            nombre_carrera,
            año,
            nombre,
            url_oficial
        )
        if resultado.tiempo_oficial:
            return resultado
    
    # PASO 3: Búsqueda genérica fallback
    print(f"  ℹ️  Intento de búsqueda genérica...")
    return _buscar_generico(nombre_carrera, año, nombre)


def _buscar_en_url_directo(
    url: str,
    nombre: str,
    nombre_carrera: str,
    año: int
) -> ResultadoSchema:
    """
    Busca usando Tavily en el URL directo (mejor que HTML crudo)
    Tavily limpia el contenido automáticamente
    """
    print(f"  → Buscando en URL directo: {url[:60]}...")
    
    try:
        # Extraer dominio del URL para búsqueda específica
        domain = urlparse(url).netloc
        
        # Buscar específicamente en este dominio + nombre
        query = f'site:{domain} "{nombre}" clasificación resultados'
        
        print(f"  → Query: {query[:60]}...")
        busqueda = tavily.search(query=query, search_depth="advanced", max_results=5)
        
        if busqueda.get('results'):
            # Priorizar resultados del URL original
            contexto = ""
            for res in busqueda['results']:
                if url in res['url']:
                    # Resultado del URL exacto - máxima prioridad
                    contexto = res['content']
                    break
            
            if not contexto:
                # Usar primer resultado si no está el URL exacto
                contexto = "\n".join([r['content'][:1500] for r in busqueda['results'][:3]])
            
            print(f"  ✅ Contenido obtenido, extrayendo datos...")
            return _extraer_resultado_estricto(contexto, nombre, nombre_carrera, año)
        else:
            print(f"  ℹ️  No se encontraron resultados en {domain}")
    
    except Exception as e:
        print(f"  ⚠️  Error buscando en URL: {e}")
    
    return ResultadoSchema()


def _buscar_en_portal_conocido(
    portal: str,
    nombre_carrera: str,
    año: int,
    nombre: str,
    url_oficial: str
) -> ResultadoSchema:
    """Búsqueda específica para portales conocidos"""
    
    config = PORTALES_CONOCIDOS[portal]
    partes_nombre = nombre.split()
    apellido = partes_nombre[-1] if partes_nombre else nombre
    
    # Construir diferentes queries a intentar
    queries = []
    if portal == "sportmaniacs":
        # Para Sportmaniacs: intentar nombre completo primero, luego solo apellido
        queries = [
            f"{nombre_carrera} {año} site:sportmaniacs.com {nombre} clasificación",
            f"sportmaniacs {nombre_carrera} {año} {apellido} clasificación",
            f"site:sportmaniacs.com {nombre_carrera} {año}"
        ]
    elif portal == "mylaps":
        queries = [
            f"mylaps {nombre_carrera} {año} {nombre} resultados",
            f"mylaps {nombre_carrera} {year} {apellido}"
        ]
    else:
        queries = [f"{portal} {nombre_carrera} {año} {nombre}"]
    
    # Intentar cada query
    for query in queries:
        print(f"  → Buscando: {query[:60]}...")
        
        try:
            busqueda = tavily.search(query=query, search_depth="advanced", max_results=5)
            
            if busqueda.get('results'):
                contexto = "\n".join([
                    f"--- {res['url']} ---\n{res['content'][:1500]}\n"
                    for res in busqueda['results'][:3]
                ])
                
                # Procesar con IA estricta
                resultado = _extraer_resultado_estricto(contexto, nombre, nombre_carrera, año)
                if resultado.tiempo_oficial:
                    return resultado
                
                # También intentar buscar por apellido si el nombre completo falló
                if nombre != apellido:
                    resultado = _extraer_resultado_estricto(contexto, apellido, nombre_carrera, año)
                    if resultado.tiempo_oficial:
                        return resultado
        
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
            continue
    
    return ResultadoSchema()


def _buscar_generico(nombre_carrera: str, año: int, nombre: str) -> ResultadoSchema:
    """Búsqueda genérica como último recurso"""
    
    queries = [
        f'"{nombre_carrera}" {año} "{nombre}" clasificación',
        f'{nombre_carrera} {año} {nombre} tiempo resultados',
        f'{nombre_carrera} {año} pdf descargar resultados',
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"  → Query {i}/3: {query[:50]}...")
        try:
            busqueda = tavily.search(query=query, search_depth="basic", max_results=5)
            if busqueda.get('results'):
                contexto = "\n".join([
                    f"{res['content'][:800]}\n"
                    for res in busqueda['results']
                ])
                return _extraer_resultado_estricto(contexto, nombre, nombre_carrera, año)
        except:
            continue
    
    return ResultadoSchema()


def _extraer_resultado_estricto(
    contexto: str,
    nombre: str,
    nombre_carrera: str,
    año: int
) -> ResultadoSchema:
    """
    Extrae datos EXTREMADAMENTE CONSERVADOR
    Regex primero, LLM solo como último recurso
    """
    
    print(f"  → Buscando '{nombre}' en {len(contexto)} chars...")
    
    # PASO 1: Regex - es MÁS confiable
    resultado_regex = _buscar_por_regex(contexto, nombre)
    if resultado_regex.tiempo_oficial:
        return resultado_regex
    
    # PASO 2: LLM EXTREMADAMENTE CONSERVADOR
    print(f"  → LLM: búsqueda extremadamente estricta...")
    
    prompt = f"""BÚSQUEDA EXTREMADAMENTE ESTRICTA. Solo devuelve datos si ESTÁS 100% SEGURO.

Buscas: "{nombre}"

TABLA/CONTENIDO:
{contexto[:2000]}

INSTRUCCIONES ABSOLUTAS:
1. SOLO SI ves el nombre CLARAMENTE en el contexto
2. SOLO SI ves un tiempo en formato HH:MM:SS
3. SOLO SI ves una posición numérica
4. TODAS las 3 cosas en el MISMO párrafo/línea

SI TIENES MÍS DE 5% DE DUDA → Devuelve NULL
NO INVENTES. Es mejor vacío que incorrecto."""

    try:
        datos = llm_estructurado.invoke(prompt)
        
        # Validación ESTRICTA post-LLM
        if datos.tiempo_oficial and not validar_tiempo(datos.tiempo_oficial):
            print(f"    ❌ Tiempo rechazado: {datos.tiempo_oficial}")
            return ResultadoSchema()
        
        if datos.posicion_general and not validar_posicion(datos.posicion_general):
            print(f"    ❌ Posición rechazada: {datos.posicion_general}")
            return ResultadoSchema()
        
        # Si tiene datos válidos
        if datos.tiempo_oficial and datos.posicion_general:
            print(f"    ✅ LLM validó: {datos.tiempo_oficial}, Pos: {datos.posicion_general}")
            datos.confianza = 0.65  # Confianza baja en LLM
            return datos
        
        print(f"    ⚠️  LLM devolvió datos incompletos, descartando")
        return ResultadoSchema()
    
    except Exception as e:
        print(f"    ⚠️  Error LLM: {e}")
        return ResultadoSchema()


def _buscar_por_regex(contexto: str, nombre: str) -> ResultadoSchema:
    """Busca usando regex - EVÍta alucinación
    
    Estrategia de 2 pasadas:
    1. Busca nombre completo (máxima confianza)
    2. Si no encuentra, busca por nombre de pila (más flexible para nombres alternativos)
    """
    
    if not contexto or len(contexto) < 50:
        return ResultadoSchema()
    
    partes = nombre.split()
    nombre_pila = partes[0] if partes else ""
    apellido = partes[-1] if partes else ""
    nombre_sin_acentos = _sin_acentos(nombre)
    apellido_sin_acentos = _sin_acentos(apellido)
    nombre_pila_sin_ac = _sin_acentos(nombre_pila)
    
    lineas = contexto.split('\n')
    
    # PASADA 1: Buscar por nombre completo
    print(f"    → Pasada 1: Buscando por nombre completo '{nombre}' o apellido '{apellido}'")
    resultado = _buscar_regex_flexible(lineas, nombre, apellido, nombre_sin_acentos, apellido_sin_acentos, True)
    if resultado.tiempo_oficial:
        return resultado
    
    # PASADA 2: Si no encuentra, buscar por nombre de pila (más flexible)
    # Esto permite encontrar al usuario aunque esté registrado con un nombre diferente
    print(f"    → Pasada 2: Buscando flexible por nombre de pila '{nombre_pila}' + tiempo + posición")
    resultado = _buscar_regex_flexible(lineas, nombre_pila, "", nombre_pila_sin_ac, "", False)
    if resultado.tiempo_oficial:
        return resultado
    
    print(f"    ⚠️  Regex no encontró coincidencias")
    return ResultadoSchema()


def _buscar_regex_flexible(lineas: List[str], patron_nombre: str, patron_apellido: str, 
                          patron_sin_ac: str, apellido_sin_ac: str, requiere_apellido: bool) -> ResultadoSchema:
    """Función auxiliar para búsqueda por regex con diferentes patrones
    
    Args:
        requiere_apellido: Si True, DEBE tener nombre+apellido. Si False, solo nombre de pila
    """
    for linea in lineas:
        linea_upper = linea.upper()
        linea_sin_ac = _sin_acentos(linea_upper)
        
        # ¿Contiene el nombre de búsqueda?
        tiene_nombre = any([
            patron_nombre.upper() in linea_upper,
            patron_sin_ac.upper() in linea_sin_ac
        ])
        
        if not tiene_nombre:
            continue
        
        # Si requiere apellido, verificar que el apellido también esté
        if requiere_apellido and patron_apellido:
            tiene_apellido = any([
                patron_apellido.upper() in linea_upper,
                apellido_sin_ac.upper() in linea_sin_ac
            ])
            if not tiene_apellido:
                continue
        
        # ¿Contiene tiempo HH:MM:SS?
        tiempo_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})', linea)
        if not tiempo_match:
            continue
        
        tiempo = tiempo_match.group(0)
        
        # ¿Contiene número de posición?
        # Buscar números después del tiempo
        resto = linea[tiempo_match.end():]
        posicion_match = re.search(r'\b(\d{1,4})\b', resto)
        
        if not posicion_match:
            # Buscar antes del tiempo también
            antes = linea[:tiempo_match.start()]
            posicion_match = re.search(r'\b(\d{1,4})\b', antes)
        
        if not posicion_match:
            continue
        
        posicion_str = posicion_match.group(1)
        
        # Validar datos extraídos
        if validar_tiempo(tiempo) and validar_posicion(int(posicion_str)):
            confianza = 0.9 if requiere_apellido else 0.75  # Menos confianza si solo nombre de pila
            print(f"    ✅ REGEX encontró: {tiempo}, Pos: {posicion_str} (confianza: {confianza})")
            print(f"       Línea: {linea[:80]}")
            return ResultadoSchema(
                tiempo_oficial=tiempo,
                posicion_general=int(posicion_str),
                confianza=confianza
            )
    
    return ResultadoSchema()
    return ResultadoSchema()


def _sin_acentos(texto: str) -> str:
    """Convierte texto sin acentos"""
    import unicodedata
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(texto))
        if unicodedata.category(c) != 'Mn'
    )


# --- 4. PROCESAMIENTO DE ARCHIVOS (PDF/CSV) ---

def buscar_en_archivo_local(
    archivo_path: str,
    nombre: str,
    año: int
) -> ResultadoSchema:
    """
    Procesa archivo local (PDF o CSV) directamente
    MUCHO más confiable que búsqueda web
    """
    
    print(f"📄 Procesando archivo: {Path(archivo_path).name}")
    
    try:
        if archivo_path.endswith('.pdf'):
            contenido = _extraer_pdf(archivo_path)
        elif archivo_path.endswith('.csv'):
            contenido = _extraer_csv(archivo_path)
        else:
            contenido = open(archivo_path, 'r', encoding='utf-8').read()
        
        # Procesar archivo
        return _extraer_resultado_estricto(contenido, nombre, "", año)
    
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return ResultadoSchema()


def _extraer_pdf(path: str) -> str:
    """Extrae texto de PDF con manejo robusto de encoding"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        texto = ""
        
        # Extraer hasta 30 páginas (generalmente clasificaciones están en primeras páginas)
        for page_num in range(min(30, len(reader.pages))):
            try:
                page = reader.pages[page_num]
                extracted_text = page.extract_text()
                if extracted_text:
                    texto += extracted_text + "\n"
            except Exception as e:
                print(f"    ⚠️  Error extrayendo página {page_num}: {e}")
                continue
        
        if not texto.strip():
            print(f"    ⚠️  PDF no contiene texto extraíble")
            return ""
        
        print(f"    ✅ Extraídos {len(texto)} caracteres del PDF")
        return texto
    
    except ImportError:
        print("    ❌ PyPDF2 no instalado")
        return ""
    except Exception as e:
        print(f"    ❌ Error leyendo PDF: {e}")
        return ""


def _extraer_csv(path: str) -> str:
    """Extrae contenido de CSV con múltiples encodings"""
    try:
        import csv
        
        # Intentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                contenido = []
                with open(path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        if i < 200:  # Primeras 200 filas
                            line = " | ".join(str(v).strip() for v in row.values() if v)
                            contenido.append(line)
                
                if contenido:
                    print(f"    ✅ CSV leído con encoding {encoding}")
                    return "\n".join(contenido)
            
            except UnicodeDecodeError:
                continue
        
        print(f"    ⚠️  No se pudo leer CSV")
        return ""
    
    except Exception as e:
        print(f"    ❌ Error leyendo CSV: {e}")
        return ""


# --- 5. FUNCIONES AUXILIARES ---

def generar_instrucciones_usuario(nombre_carrera: str, url_oficial: Optional[str]) -> str:
    """
    Genera instrucciones para que usuario proporcione datos
    cuando búsqueda automática falla
    """
    
    instrucciones = f"""
❌ No se encontró {nombre_carrera} automáticamente.

💡 OPCIONES:

1️⃣ OPCIÓN FÁCIL: Proporciona archivo
   • Descarga el PDF o CSV de resultados
   • Súbelo aquí
   • Sistema extraerá datos automáticamente

2️⃣ OPCIÓN RÁPIDA: Proporciona URL directa
   • Ve a la web oficial
   • Busca botón "Resultados" o "Ver Clasificación"
   • Copia URL de la página con la tabla de resultados
   • Prop porciona URL aquí

3️⃣ OPCIÓN MANUAL: Ingresa datos
   • Tiempo: HH:MM:SS
   • Posición: número
   • Categoría: número
   • Ritmo: MIN:SS/km
"""
    
    return instrucciones


def detectar_format_csv_automatico(contenido: str) -> Dict[str, int]:
    """
    Detecta automáticamente la estructura de un CSV/tabla
    para extraer posición, nombre, tiempo correctamente
    """
    
    # Patrones comunes
    patrones = [
        {
            "nombre": "Pos | Nombre | Tiempo",
            "regex": r"(\d+)\s*\|\s*([A-Z][a-záéíóú\s]+)\s*\|\s*(\d{1,2}:\d{2}:\d{2})"
        },
        {
            "nombre": "Pos Nombre Tiempo",
            "regex": r"^(\d+)\s+([A-Z][a-záéíóú\s]+)\s+(\d{1,2}:\d{2}:\d{2})"
        },
        {
            "nombre": "CSV Estándar",
            "regex": r"\"(\d+)\",\"([A-Z][a-z\s]+)\",\"(\d{1,2}:\d{2}:\d{2})\""
        }
    ]
    
    for patron in patrones:
        if re.search(patron['regex'], contenido, re.MULTILINE):
            return {"detectado": patron['nombre']}
    
    return {"detectado": "desconocido"}
