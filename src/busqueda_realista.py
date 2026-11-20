# Busqueda y extraccion de clasificaciones deportivas
# Rastreo automatizado en plataformas oficiales de cronometraje (Cruzando La Meta, Global Tempo, Dorsalchip, etc.),
# motores de busqueda web y procesamiento de archivos locales (PDF/CSV).

import os
import re
import json
import urllib.request
import unicodedata
from urllib.parse import urlparse
from datetime import datetime
from typing import Optional, List, Dict
from tavily import TavilyClient
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pathlib import Path
from src.main import ResultadoSchema

load_dotenv()

# --- CLIENTES DE BUSQUEDA E IA ---
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def _crear_motores_llm():
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
    api_key = os.getenv("GROQ_API_KEY")

    raw_llm = ChatGroq(
        model_name=modelos_unicos[0],
        temperature=0,
        api_key=api_key,
        max_retries=2
    )

    structured_llm = raw_llm.with_structured_output(ResultadoSchema)

    if len(modelos_unicos) > 1:
        fallbacks = [
            ChatGroq(model_name=m, temperature=0, api_key=api_key, max_retries=2).with_structured_output(ResultadoSchema)
            for m in modelos_unicos[1:]
        ]
        structured_llm = structured_llm.with_fallbacks(fallbacks)

    return raw_llm, structured_llm

raw_llm, llm_estructurado = _crear_motores_llm()


def invocar_llm_seguro(prompt: str) -> ResultadoSchema:
    """
    Invoca el LLM estructurado. Si Groq emite directamente JSON en markdown
    y lanza error 400 (failed_generation), extrae el JSON recuperado con precision.
    """
    try:
        return llm_estructurado.invoke(prompt)
    except Exception as e:
        err = str(e)
        match = re.search(r'\{[^{}]*\}', err, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return ResultadoSchema(**data)
            except Exception:
                pass
        try:
            resp = raw_llm.invoke(
                prompt + "\n\nResponde estrictamente con un JSON: {\"tiempo_oficial\": ..., \"posicion_general\": ..., \"posicion_categoria\": ..., \"ritmo_medio\": ..., \"confianza\": 0.9}"
            ).content
            match = re.search(r'\{[^{}]*\}', resp, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return ResultadoSchema(**data)
        except Exception:
            pass
        return ResultadoSchema()


# --- VALIDACION Y NORMALIZACION DE TIEMPOS ---

def sin_acentos(texto: str) -> str:
    if not texto:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(texto))
        if unicodedata.category(c) != 'Mn'
    ).lower()


def validar_tiempo(tiempo_str: Optional[str]) -> bool:
    """Valida formato de tiempo: HH:MM:SS, MM:SS o MM:SS.d"""
    if not tiempo_str:
        return False
    s = tiempo_str.strip()
    if re.match(r'^\d{1,2}:\d{2}:\d{2}(?:\.\d+)?$', s):
        partes = s.split(':')
        return 0 <= int(partes[0]) < 24
    if re.match(r'^\d{1,2}:\d{2}(?:\.\d+)?$', s):
        partes = s.split(':')
        return 0 <= int(partes[0]) < 60
    return False


def tiempo_a_segundos(tiempo_str: str) -> int:
    if not tiempo_str:
        return 0
    s = re.sub(r'[^\d:]', '', tiempo_str.strip())
    partes = [int(p) for p in s.split(':') if p]
    if len(partes) == 2:
        return partes[0] * 60 + partes[1]
    if len(partes) == 3:
        return partes[0] * 3600 + partes[1] * 60 + partes[2]
    return 0


def es_tiempo_plausible(tiempo_str: str, nombre_carrera: str) -> bool:
    """
    Verifica que la marca sea fisiologicamente posible para la distancia de la prueba.
    Evita confundir parciales por km, ritmos o errores tipograficos con marcas finales.
    """
    if not tiempo_str:
        return False
    segundos = tiempo_a_segundos(tiempo_str)
    if segundos <= 0:
        return False

    s_carrera = sin_acentos(nombre_carrera)

    # Ninguna prueba popular adulta se finaliza en menos de 12 minutos
    if segundos < 12 * 60:
        return False

    # Media Maraton (21.097 km): entre 55 min y 4 horas
    if any(k in s_carrera for k in ['media maraton', 'medio maraton', '21k', 'half']):
        return 3300 <= segundos <= 14400

    # Maraton (42.195 km): entre 2h y 7 horas
    if ('maraton' in s_carrera and 'media' not in s_carrera and 'medio' not in s_carrera) or '42k' in s_carrera:
        return 7200 <= segundos <= 25200

    # Ultra trail / Ultra distancia (> 42k)
    if 'ultra' in s_carrera:
        return segundos >= 3 * 3600 + 30 * 60

    # 10K / Pruebas populares de 10km (entre 26 min y 2h30)
    if '10k' in s_carrera or 'volantones' in s_carrera:
        return 1560 <= segundos <= 9000

    # Rango general admisible para pruebas entre 5k y 35k
    return 900 <= segundos <= 21600


def normalizar_tiempo(tiempo_str: Optional[str]) -> Optional[str]:
    """Limpia y normaliza tiempos en formatos variados a HH:MM:SS"""
    if not tiempo_str:
        return None
    s = re.sub(r'[^\d:\.]', '', tiempo_str.strip())
    partes = s.split(':')
    if len(partes) == 2:
        return f"00:{partes[0].zfill(2)}:{partes[1].zfill(2)}"
    if len(partes) == 3:
        try:
            # Si horas es >= 6 en prueba corta, es el puesto de categoria pegado a MM:SS (ej: 8:51:43)
            if int(partes[0]) >= 6 and int(partes[1]) < 60 and int(partes[2].split('.')[0]) < 60:
                return f"00:{partes[1].zfill(2)}:{partes[2].zfill(2)}"
            return f"{partes[0].zfill(2)}:{partes[1].zfill(2)}:{partes[2].split('.')[0].zfill(2)}"
        except Exception:
            pass
    return s


def validar_posicion(pos: Optional[int]) -> bool:
    if pos is None:
        return False
    return 1 <= pos <= 100000


# --- IDENTIFICACION Y VALIDACION DE CARRERAS ---

def extraer_tokens_carrera(nombre_carrera: str) -> List[str]:
    """Extrae palabras clave representativas de la prueba omitiendo terminos genericos."""
    s = sin_acentos(nombre_carrera)
    s = re.sub(r'\b(xi|xii|xiii|xiv|xv|xvi|xvii|xviii|xix|xx|x|ix|viii|vii|vi|v|iv|iii|ii|i|\d+ª|\d+º|\d+)\b', ' ', s)
    s = re.sub(r'\b(edicion|prueba|carrera|cxm|trail|popular|deporte|deportiva|s\.c\.a\.|c\.d\.|villa de|ciudad de|202\d|media maraton|maraton)\b', ' ', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    tokens = [t.strip() for t in s.split() if len(t.strip()) >= 3]
    return tokens


def carrera_coincide_con_doc(nombre_carrera: str, doc_title: str, doc_url: str, doc_text: str = '') -> bool:
    """
    Verifica que el documento pertenezca exactamente a la carrera consultada.
    Previene de forma estricta la contaminacion cruzada entre pruebas distintas.
    """
    s_carrera = sin_acentos(nombre_carrera)
    fuente = sin_acentos(f"{doc_title} {doc_url} {doc_text[:600]}")

    if 'snow' in s_carrera:
        return 'snow' in fuente
    if 'volantones' in s_carrera:
        return 'volantones' in fuente or 'base aerea' in fuente
    if 'padul' in s_carrera or 'mamut' in s_carrera:
        return 'padul' in fuente or 'mamut' in fuente
    if 'calahorra' in s_carrera:
        return 'calahorra' in fuente
    if 'motril' in s_carrera:
        return 'motril' in fuente
    if 'sierro' in s_carrera:
        return 'sierro' in fuente
    if 'grupo' in s_carrera:
        return 'grupo' in fuente
    if 'portugos' in s_carrera:
        return 'portugos' in fuente
    if 'lanjaron' in s_carrera:
        return 'lanjaron' in fuente
    if 'ultra' in s_carrera and 'sierra nevada' in s_carrera:
        return 'ultra' in fuente and ('sierra' in fuente or 'usn' in fuente)
    if 'baza' in s_carrera:
        return 'baza' in fuente
    if 'benemerita' in s_carrera:
        return 'benemerita' in fuente
    if 'molvizar' in s_carrera:
        return 'molvizar' in fuente
    if 'durcal' in s_carrera:
        return 'durcal' in fuente
    if 'peza' in s_carrera or '51x13' in s_carrera:
        return 'peza' in fuente or '51x13' in fuente

    tokens = extraer_tokens_carrera(nombre_carrera)
    if not tokens:
        tokens = [t for t in s_carrera.split() if len(t) >= 4]

    return any(t in fuente for t in tokens)


def limpiar_texto_clasificaciones(texto: str) -> str:
    """Separa columnas comprimidas en tablas HTML deportivas (ej: 14JAIME -> 14 JAIME, 8º51:43 -> 8º 51:43)"""
    t = re.sub(r'(\d+)([A-ZÁÉÍÓÚÑ]{3,})', r'\1 \2', texto)
    t = re.sub(r'(\d+[ºª])(\d{1,2}:\d{2})', r'\1 \2', t)
    t = re.sub(r'(\d{1,2}:\d{2}(?::\d{2})?)(\d{1,2}[\':]\d{2})', r'\1 \2', t)
    return t


# --- PARSERS DIRECTOS DE PORTALES OFICIALES DE CRONOMETRAJE ---

def extraer_cruzandolameta_url(url: str, nombre_atleta: str, nombre_carrera: str) -> Optional[ResultadoSchema]:
    """
    Descarga y parsea de forma directa e inmediata una pagina oficial de Cruzando La Meta.
    Garantiza extraccion determinista al 100% en informes de participantes y listados.
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"    [Aviso] Error descargando informe ({url}): {e}")
        return None

    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)

    # Validar que pertenezca a la carrera consultada
    m_header = re.search(r'Pruebas Finalizadas / ([^/]+) / Clasificaciones / Informe de ([^0-9]+)', text)
    header_carrera = m_header.group(1).strip() if m_header else ""
    if not carrera_coincide_con_doc(nombre_carrera, header_carrera, url, text[:500]):
        return None

    tiempo_match = re.search(r'TIEMPO OFICIAL:\s*([0-9:]+)', text)
    if not tiempo_match:
        return None

    tiempo_raw = tiempo_match.group(1)
    tiempo_norm = normalizar_tiempo(tiempo_raw)
    if not tiempo_norm or not es_tiempo_plausible(tiempo_norm, nombre_carrera):
        return None

    puesto_match = re.search(r'PUESTO DE LA GENERAL:\s*(\d+)', text)
    cat_match = re.search(r'PUESTO DE SU CATEGORIA:\s*(\d+)', text)
    ritmo_match = re.search(r'RITMO OFICIAL:\s*([0-9:\'\"/ a-zA-Z]+?)(?=\s*TIEMPO|\s*RITMO|\s*ESTADÍSTICAS|$)', text)

    puesto = int(puesto_match.group(1)) if puesto_match else None
    cat = int(cat_match.group(1)) if cat_match else None
    ritmo = ritmo_match.group(1).strip() if ritmo_match else None

    return ResultadoSchema(
        tiempo_oficial=tiempo_norm,
        posicion_general=puesto,
        posicion_categoria=cat,
        ritmo_medio=ritmo,
        confianza=1.0
    )


# --- EXTRACCION Y RASTREO MULTIPLATAFORMA ---

def buscar_resultado_realista(
    nombre_carrera: str,
    año: int,
    nombre: str,
    url_oficial: Optional[str] = None
) -> ResultadoSchema:
    """
    Rastrea el resultado oficial del corredor de forma exhaustiva:
    1. Si hay URL directa oficial o en el portal de cronometraje, la examina primero.
    2. Consulta perfiles e informes del corredor en plataformas de cronometraje.
    3. Descarta de raiz cualquier documento que no pertenezca a la prueba indicada.
    4. Procesa y normaliza marcas con validacion de plausibilidad.
    """
    print(f"[Busqueda de resultado] Corredor: '{nombre}' en Carrera: '{nombre_carrera}' ({año})")

    nombre_sin = sin_acentos(nombre).strip()
    partes_nombre = nombre_sin.split()
    nombre_pila = partes_nombre[0] if partes_nombre else nombre_sin
    primer_apellido = partes_nombre[1] if len(partes_nombre) > 1 else ''
    nombre_corto = f"{nombre_pila} {primer_apellido}" if primer_apellido else nombre_pila
    tokens_carrera = extraer_tokens_carrera(nombre_carrera)
    kw_carrera = tokens_carrera[0] if tokens_carrera else sin_acentos(nombre_carrera)

    # 1. Analisis directo de URL oficial si fue suministrada
    if url_oficial:
        if 'cruzandolameta.es' in url_oficial:
            res_directo = extraer_cruzandolameta_url(url_oficial, nombre, nombre_carrera)
            if res_directo and res_directo.tiempo_oficial:
                print(f"  [OK] Resultado verificado desde URL oficial: {res_directo.tiempo_oficial}, Pos #{res_directo.posicion_general}")
                return res_directo

    # 2. Rastreo en Cruzando La Meta mediante el perfil de competiciones del corredor
    docs = []
    urls_vistas = set()

    try:
        res_clm = tavily.search(query=f'site:cruzandolameta.es "{nombre_corto}"', max_results=20)
        for r in res_clm.get('results', []):
            u = r.get('url', '')
            t = r.get('title', '')
            c = r.get('content', '')
            if u and u not in urls_vistas:
                urls_vistas.add(u)
                if carrera_coincide_con_doc(nombre_carrera, t, u, c):
                    if '/informe/' in u:
                        res_informe = extraer_cruzandolameta_url(u, nombre, nombre_carrera)
                        if res_informe and res_informe.tiempo_oficial:
                            print(f"  [OK] Informe oficial localizado en Cruzando La Meta: {res_informe.tiempo_oficial}, Pos #{res_informe.posicion_general}")
                            return res_informe
                    if c:
                        docs.append(limpiar_texto_clasificaciones(f"URL: {u}\nTITULO: {t}\n{c}"))
        if docs:
            ctx_clm = "\n---\n".join(docs)
            r_directo = _buscar_por_regex(ctx_clm, nombre_pila, primer_apellido, nombre_carrera)
            if r_directo and r_directo.tiempo_oficial and r_directo.posicion_general:
                print(f"  [OK] Clasificacion oficial verificada en Cruzando La Meta: {r_directo.tiempo_oficial}, Pos #{r_directo.posicion_general}")
                return r_directo
    except Exception as e:
        print(f"  [Aviso] Error consultando portal de cronometraje: {e}")

    # 3. Rastreo amplio en otros portales y agregadores web
    queries = [
        f'site:global-tempo.com "{nombre_corto}" {kw_carrera}',
        f'site:dorsalchip.es "{nombre_corto}" {kw_carrera}',
        f'site:sportmaniacs.com "{nombre_corto}" {kw_carrera}',
        f'clasificacion "{nombre_carrera}" "{nombre_corto}"',
        f'resultados "{nombre_carrera}" "{nombre_sin}" {año}',
        f'clasificacion "{nombre_carrera}" "{nombre_pila}" "{primer_apellido}"',
    ]

    for q in queries:
        try:
            res = tavily.search(query=q, search_depth="advanced", max_results=3)
            for r in res.get('results', []):
                u = r.get('url', '')
                t = r.get('title', '')
                c = r.get('content', '')
                if u and u not in urls_vistas:
                    urls_vistas.add(u)
                    # FILTRO ESTRICTO: Descartar de raiz documentos que pertenezcan a otras pruebas
                    if carrera_coincide_con_doc(nombre_carrera, t, u, c):
                        # Si es un informe de Cruzando La Meta, parsearlo directamente
                        if 'cruzandolameta.es' in u and '/informe/' in u:
                            res_inf = extraer_cruzandolameta_url(u, nombre, nombre_carrera)
                            if res_inf and res_inf.tiempo_oficial:
                                print(f"  [OK] Informe localizado via busqueda avanzada: {res_inf.tiempo_oficial}")
                                return res_inf
                        docs.append(limpiar_texto_clasificaciones(f"URL: {u}\nTITULO: {t}\n{c}"))
            if len(docs) >= 3:
                break
        except Exception as e:
            print(f"  [Aviso] Error en consulta '{q}': {e}")
            continue

    if not docs:
        print("  [Aviso] No se localizaron documentos oficiales confirmados para esta carrera")
        return ResultadoSchema()

    contexto = "\n---\n".join(docs)[:25000]
    return _extraer_resultado_estricto(contexto, nombre, nombre_carrera, año)


def _extraer_resultado_estricto(
    contexto: str,
    nombre: str,
    nombre_carrera: str,
    año: int
) -> ResultadoSchema:
    nombre_sin = sin_acentos(nombre).strip()
    partes = nombre_sin.split()
    nombre_pila = partes[0] if partes else nombre_sin
    primer_apellido = partes[1] if len(partes) > 1 else ''
    nombre_corto = f"{nombre_pila} {primer_apellido}" if primer_apellido else nombre_pila

    # 1. Regex estricto sobre lineas que contengan el nombre del atleta
    r_reg = _buscar_por_regex(contexto, nombre_pila, primer_apellido, nombre_carrera)
    if r_reg and r_reg.tiempo_oficial and r_reg.posicion_general:
        print(f"  [OK] Coincidencia por patron de clasificacion: Tiempo {r_reg.tiempo_oficial}, Pos #{r_reg.posicion_general}")
        return r_reg

    # 2. Extraccion asistida por IA con directivas de no-alucinacion
    print(f"  -> Extrayendo datos con IA para '{nombre}' en {len(contexto)} caracteres...")

    prompt = f"""
Eres un analista experto en extraccion de tiempos y clasificaciones deportivas.
Tu objetivo es encontrar la marca oficial del corredor: "{nombre}" (o "{nombre_corto}") en la carrera: "{nombre_carrera}" ({año}).

DOCUMENTOS OFICIALES DE LA PRUEBA:
{contexto}

INSTRUCCIONES ESTRICTAS:
1. El corredor puede figurar como "{nombre}", "{nombre_corto}" o con apellidos primero ("{primer_apellido.upper()}").
2. REGLA FUNDAMENTAL DE VERACIDAD:
   - Extrae UNICAMENTE el tiempo y puesto particular de "{nombre}".
   - NUNCA extraigas el tiempo del ganador de la carrera ni de otros corredores.
   - Si el texto solo menciona que el corredor participo, o gano una categoria, pero NO incluye su tiempo individual oficial de llegada, DEBES devolver null en tiempo_oficial.
   - Si el corredor no aparece en la tabla de clasificaciones, devuelve null en todos los campos.
3. Formatos:
   - tiempo_oficial: HH:MM:SS o MM:SS (null si no existe)
   - posicion_general: numero entero (null si no existe)
   - posicion_categoria: numero entero (null si no existe)
   - ritmo_medio: ritmo por km ej: '4:15 min/km' (null si no existe)
   - confianza: 0.9 si lo localizas con total certeza, 0.5 si es dudoso.
"""

    datos = invocar_llm_seguro(prompt)

    # Validacion y normalizacion de la marca extraida
    if datos.tiempo_oficial:
        tiempo_limpio = normalizar_tiempo(datos.tiempo_oficial)
        if tiempo_limpio and validar_tiempo(tiempo_limpio) and es_tiempo_plausible(tiempo_limpio, nombre_carrera):
            datos.tiempo_oficial = tiempo_limpio
            if not datos.confianza:
                datos.confianza = 0.85
            print(f"  [OK] IA extrajo resultado verificado: Tiempo {datos.tiempo_oficial}, Pos #{datos.posicion_general}")
            return datos
        else:
            print(f"  [Aviso] Tiempo '{datos.tiempo_oficial}' descartado por no ser plausible para esta prueba")

    if r_reg and r_reg.tiempo_oficial and es_tiempo_plausible(r_reg.tiempo_oficial, nombre_carrera):
        return r_reg

    print("  [Aviso] No se localizo marca confirmada en las clasificaciones consultadas")
    return ResultadoSchema()


def _buscar_por_regex(contexto: str, nombre_pila: str, primer_apellido: str, nombre_carrera: str) -> Optional[ResultadoSchema]:
    if not contexto or not primer_apellido:
        return None

    primer_ap_up = primer_apellido.upper()
    nombre_pila_up = nombre_pila.upper()

    for linea in contexto.split('\n'):
        linea_sin = sin_acentos(linea).upper()

        if primer_ap_up not in linea_sin:
            continue
        if nombre_pila_up and nombre_pila_up not in linea_sin:
            continue

        tiempo_match = re.search(r'\b(\d{1,2}:\d{2}:\d{2})\b', linea)
        if not tiempo_match:
            tiempo_match = re.search(r'\b(\d{1,2}:\d{2}(?:\.\d+)?)\b', linea)
        if not tiempo_match:
            continue

        tiempo = normalizar_tiempo(tiempo_match.group(1))
        if not tiempo or not validar_tiempo(tiempo) or not es_tiempo_plausible(tiempo, nombre_carrera):
            continue

        # Posicion general: numero inmediatamente anterior al nombre del atleta
        posicion = None
        idx_pila = linea_sin.find(nombre_pila_up)
        idx_ap = linea_sin.find(primer_ap_up)
        indices_validos = [i for i in [idx_pila, idx_ap] if i != -1]
        if indices_validos:
            idx_nombre = min(indices_validos)
            antes_nombre = linea[:idx_nombre]
            antes_clean = re.sub(r'\b\d{1,3}\s*[kKmM]\b', '', antes_nombre)
            nums = re.findall(r'\b(\d{1,4})\b', antes_clean)
            if nums:
                try:
                    posicion = int(nums[-1])
                except Exception:
                    pass
        if not posicion:
            antes = linea[:tiempo_match.start()]
            pos_match = re.search(r'\b(\d{1,4})\b', antes)
            if pos_match:
                try:
                    posicion = int(pos_match.group(1))
                except Exception:
                    pass

        # Posicion categoria (ej: 8º o 8ª)
        cat_pos = None
        cat_match = re.search(r'\b(\d+)[ºª]\b', linea)
        if cat_match:
            try:
                cat_pos = int(cat_match.group(1))
            except Exception:
                pass

        # Ritmo medio
        ritmo = None
        despues = linea[tiempo_match.end():]
        rit_match = re.search(r'(\d{1,2}[\':]\d{2}(?:\"?/(?:km|Km)|\s*min/km)?)', despues)
        if not rit_match:
            antes_tiempo = linea[:tiempo_match.start()]
            rit_match = re.search(r'(\d{1,2}[\':]\d{2}(?:\"?/(?:km|Km)|\s*min/km)?)', antes_tiempo)
        if rit_match:
            ritmo = rit_match.group(1).replace("'", ":").replace('"', '').strip()
            if "/km" in ritmo.lower():
                ritmo = re.sub(r'/(?:km|Km)', ' min/km', ritmo)
            elif "min/km" not in ritmo.lower():
                ritmo += " min/km"

        return ResultadoSchema(
            tiempo_oficial=tiempo,
            posicion_general=posicion,
            posicion_categoria=cat_pos,
            ritmo_medio=ritmo,
            confianza=0.9 if posicion else 0.75
        )

    return None


# --- PROCESAMIENTO DE ARCHIVOS LOCALES (PDF/CSV) ---

def buscar_en_archivo_local(
    archivo_path: str,
    nombre: str,
    año: int
) -> ResultadoSchema:
    print(f"Procesando archivo: {Path(archivo_path).name}")

    try:
        if archivo_path.endswith('.pdf'):
            contenido = _extraer_pdf(archivo_path)
        elif archivo_path.endswith('.csv'):
            contenido = _extraer_csv(archivo_path)
        else:
            with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()

        contenido_limpio = limpiar_texto_clasificaciones(contenido)
        return _extraer_resultado_estricto(contenido_limpio, nombre, "", año)

    except Exception as e:
        print(f"[Error] Procesando archivo: {e}")
        return ResultadoSchema()


def _extraer_pdf(path: str) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        texto = ""

        for page_num in range(min(50, len(reader.pages))):
            try:
                page = reader.pages[page_num]
                extracted_text = page.extract_text()
                if extracted_text:
                    texto += extracted_text + "\n"
            except Exception as e:
                print(f"    [Aviso] Error extrayendo pagina {page_num}: {e}")
                continue

        if not texto.strip():
            print("    [Aviso] PDF no contiene texto extraible")
            return ""

        print(f"    [OK] Extraidos {len(texto)} caracteres del PDF")
        return texto

    except ImportError:
        print("    [Error] PyPDF2 no instalado")
        return ""
    except Exception as e:
        print(f"    [Error] Leyendo PDF: {e}")
        return ""


def _extraer_csv(path: str) -> str:
    try:
        import csv
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']

        for encoding in encodings:
            try:
                contenido = []
                with open(path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        if i < 500:
                            line = " | ".join(str(v).strip() for v in row.values() if v)
                            contenido.append(line)

                if contenido:
                    print(f"    [OK] CSV leido con encoding {encoding}")
                    return "\n".join(contenido)

            except UnicodeDecodeError:
                continue

        print("    [Aviso] No se pudo leer CSV")
        return ""

    except Exception as e:
        print(f"    [Error] Leyendo CSV: {e}")
        return ""


# --- INSTRUCCIONES DE SOPORTE ---

def generar_instrucciones_usuario(nombre_carrera: str, url_oficial: Optional[str]) -> str:
    return f"""No se encontro marca oficial para {nombre_carrera} en los listados publicos indexados.

Opciones para registrar tu resultado:
1. Pegar el enlace directo a la clasificacion en la pestana 'Buscar en Web' (por ejemplo el enlace directo de Cruzando La Meta o Global Tempo).
2. Subir el archivo PDF o CSV oficial de resultados en la pestana 'Subir Archivo'.
3. Ingresar tu tiempo y posicion en la pestana 'Entrada Manual'.
"""