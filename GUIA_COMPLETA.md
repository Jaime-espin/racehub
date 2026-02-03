# 📚 GUÍA COMPLETA DE RACEHUB - Para Entender Todo el Proyecto

## 📑 Índice

1. [Visión General del Proyecto](#1-visión-general-del-proyecto)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Base de Datos (PostgreSQL)](#3-base-de-datos-postgresql)
4. [Python - Backend Explicado](#4-python---backend-explicado)
5. [JavaScript - Frontend Explicado](#5-javascript---frontend-explicado)
6. [Flujo Completo de Datos](#6-flujo-completo-de-datos)
7. [Conceptos Clave de Programación](#7-conceptos-clave-de-programación)
8. [Comandos para Ejecutar el Proyecto](#8-comandos-para-ejecutar-el-proyecto)

---

## 1. Visión General del Proyecto

### ¿Qué hace RaceHub?

RaceHub es una aplicación web que te ayuda a crear un calendario personal de carreras deportivas usando Inteligencia Artificial. En lugar de buscar manualmente en internet, tú escribes el nombre de una carrera y la IA:

1. Busca información en internet (fechas, distancias, ubicación)
2. Te muestra lo que encontró para que lo confirmes
3. Lo guarda en una base de datos
4. Te lo muestra en una página web bonita (tabla o calendario)

### Tecnologías Utilizadas

```
┌─────────────────────────────────────┐
│         NAVEGADOR WEB               │
│  (HTML + CSS + JavaScript)          │
└──────────────┬──────────────────────┘
               │ HTTP Requests
               │
┌──────────────▼──────────────────────┐
│         FASTAPI                     │
│  (Python - Servidor Web)            │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼─────┐  ┌─────▼────────┐
│ PostgreSQL │  │  APIs IA     │
│ (Base de   │  │ - Tavily     │
│  Datos)    │  │ - Groq       │
└────────────┘  └──────────────┘
```

---

## 2. Arquitectura del Sistema

### Estructura de Archivos

```
racehub/
├── db/
│   └── schema.sql          # Estructura de la base de datos
├── src/
│   ├── main.py            # Lógica de búsqueda con IA
│   ├── database.py        # Conexión a PostgreSQL
│   └── api.py             # Servidor web (FastAPI)
├── static/
│   └── styles.css         # Estilos visuales
├── templates/
│   └── index.html         # Página web
├── .env                   # Claves secretas (NO subir a Git)
├── .gitignore             # Archivos que Git debe ignorar
├── requirements.txt       # Lista de librerías Python
└── README.md              # Documentación del proyecto
```

### Roles de Cada Archivo

| Archivo | Propósito |
|---------|-----------|
| `main.py` | Motor de IA que busca y extrae datos |
| `database.py` | Conecta Python con PostgreSQL |
| `api.py` | Servidor que recibe peticiones del navegador |
| `index.html` | Interfaz visual que ve el usuario |
| `styles.css` | Colores, tamaños, animaciones |

---

## 3. Base de Datos (PostgreSQL)

### ¿Qué es PostgreSQL?

Es como una hoja de Excel gigante que vive en tu ordenador, pero mucho más potente:
- Guarda información de forma estructurada (en tablas)
- Es rápida para buscar datos
- Garantiza que no se pierda información

### Esquema Relacional de Tablas

RaceHub utiliza tres tablas conectadas para gestionar usuarios, carreras y resultados:

#### 1. Tabla: `users` (Usuarios)
Guarda la información de cada cuenta.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL, -- "Jaime Espín"
    email VARCHAR(255) UNIQUE NOT NULL,    -- "jaime@example.com"
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP //
);
```

#### 2. Tabla: `carreras` (Eventos)
Ahora incluye una referencia al usuario (`user_id`).

```sql
CREATE TABLE carreras (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- ¡NUEVO!
    nombre VARCHAR(255) NOT NULL,
    deporte VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    localizacion VARCHAR(255),
    distancia_resumen VARCHAR(255),
    url_oficial TEXT,
    estado_inscripcion VARCHAR(50) DEFAULT 'pendiente',
    CONSTRAINT carrera_usuario_unica UNIQUE (user_id, nombre, fecha)
);
```

**Novedad:**
- `user_id`: Vincula cada carrera con su dueño.
- `ON DELETE CASCADE`: Si borras al usuario, se borran sus carreras automáticamente.

#### 3. Tabla: `resultados` (Clasificaciones)
Guarda tus marcas personales de carreras finalizadas.

```sql
CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    carrera_id INTEGER REFERENCES carreras(id), -- Conexión con la tabla de arriba
    tiempo_oficial VARCHAR(50),                 -- "01:30:45"
    posicion_general INTEGER,                   -- 154
    ritmo_medio VARCHAR(50),                    -- "4:15 min/km"
    comentarios TEXT                            -- Para guardar categoría o notas
);
```

### Comandos SQL Básicos

```sql
-- Ver todas las carreras de un usuario específico (ID 1)
SELECT * FROM carreras WHERE user_id = 1;

-- Ver resultados conseguidos
SELECT * FROM resultados;

-- Unir tablas para ver carrera + tiempo
SELECT c.nombre, c.fecha, r.tiempo_oficial 
FROM carreras c 
JOIN resultados r ON c.id = r.carrera_id;
```

---

## 4. Python - Backend Explicado

### 4.1 Archivo: `database.py`

**Propósito:** Conectar Python con PostgreSQL usando SQLAlchemy (ORM).

#### ¿Qué es un ORM?

**ORM** = Object-Relational Mapping = "Traductor entre Python y SQL"

En lugar de escribir SQL manualmente:
```sql
INSERT INTO carreras (nombre, fecha) VALUES ('Behobia', '2025-11-09');
```

Escribes Python:
```python
nueva_carrera = CarreraDB(nombre="Behobia", fecha="2025-11-09")
db.add(nueva_carrera)
db.commit()
```

#### Código Explicado Línea por Línea

```python
import os
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()  # Lee el archivo .env y carga las variables
```

**Explicación:**
- `import os`: Permite acceder a variables del sistema operativo
- `load_dotenv()`: Lee el archivo `.env` donde están tus claves secretas
- `from sqlalchemy import ...`: Importa las herramientas de SQLAlchemy

```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jaime:6999@localhost:5432/racehub")
```

**¿Qué hace?**
- `os.getenv("DATABASE_URL")`: Busca una variable llamada `DATABASE_URL` en `.env`
- Si no existe, usa el valor por defecto (segundo parámetro)
- Formato: `postgresql://usuario:contraseña@servidor:puerto/nombre_bd`

```python
engine = create_engine(DATABASE_URL)
```

**¿Qué es el engine?**
El "motor" es el encargado de establecer la conexión real con PostgreSQL.

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**¿Qué es una Session?**
Una "sesión" es como una conversación temporal con la base de datos:
1. Abres la sesión
2. Haces operaciones (añadir, modificar, eliminar)
3. Confirmas con `commit()` (o cancelas con `rollback()`)
4. Cierras la sesión

**Parámetros:**
- `autocommit=False`: Los cambios NO se guardan automáticamente (tienes control)
- `autoflush=False`: No envía cambios automáticamente antes de consultas
- `bind=engine`: Vincula la sesión al motor de PostgreSQL

```python
Base = declarative_base()
```

**¿Qué es Base?**
La clase "madre" de la que heredarán todos tus modelos (tablas).

```python
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    
    # 1 Usuario -> N Carreras
    carreras = relationship("CarreraDB", back_populates="usuario")

class CarreraDB(Base):
    __tablename__ = "carreras"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Clave Foránea
    nombre = Column(String, nullable=False)
    # ... otros campos ...
    
    # Relaciones
    usuario = relationship("UserDB", back_populates="carreras")
    resultados = relationship("ResultadoDB", back_populates="carrera")

class ResultadoDB(Base):
    __tablename__ = "resultados"

    id = Column(Integer, primary_key=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"))
    tiempo_oficial = Column(String)
    posicion_general = Column(Integer)
    # ...
    
    carrera = relationship("CarreraDB", back_populates="resultados")
```

**Explicación:**
- `UserDB`, `CarreraDB`, `ResultadoDB`: Son las 3 clases que representan tus tablas.
- `ForeignKey`: Dice "esta columna apunta al ID de otra tabla".
- `relationship`: Magia de SQLAlchemy que permite navegar entre objetos (ej: `usuario.carreras` te da la lista de todas sus carreras).

```python
Base.metadata.create_all(bind=engine)
```

**¿Qué hace?**
Crea la tabla en PostgreSQL si no existe. Es como ejecutar `CREATE TABLE` automáticamente.

---

### 4.2 Archivo: `main.py`

**Propósito:** Usar IA para buscar información de carreras en internet y guardarla.

#### Importaciones y Variables de Entorno

```python
import os
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List, Optional
from dateutil import parser
from sqlalchemy.orm import Session
from database import SessionLocal, CarreraDB

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("❌ ERROR: TAVILY_API_KEY no está configurada")
if not GROQ_API_KEY:
    raise ValueError("❌ ERROR: GROQ_API_KEY no está configurada")
```

**¿Qué hace?**
1. Importa todas las librerías necesarias
2. Carga las claves API del archivo `.env`
3. Verifica que existan, si no, lanza un error y detiene el programa

**Librerías clave:**
- `tavily`: Motor de búsqueda optimizado para IA (como Google pero para bots)
- `langchain_groq`: Conecta con modelos de lenguaje (Llama 3.3)
- `pydantic`: Valida que los datos tengan la estructura correcta
- `dateutil`: Maneja fechas de forma inteligente

#### Schemas de Validación con Pydantic

Tenemos dos esquemas principales ahora:

1. **`CarreraSchema`**: Para datos generales del evento (Nombre, Fecha, Lugar).
2. **`ResultadoSchema`**: Para datos de rendimiento personal.

```python
class ResultadoSchema(BaseModel):
    tiempo_oficial: Optional[str] = Field(None, description="Tiempo (ej: '1:30:45')")
    posicion_general: Optional[int] = Field(None)
    posicion_categoria: Optional[int] = Field(None)
    ritmo_medio: Optional[str] = Field(None)
```

**Nota Importante:** Usamos `Optional` porque en muchos listados puede faltar algún dato y no queremos que la IA falle.

#### Inteligencia Artificial: Dos Cerebros Especializados

```python
# Cerebro 1: Experto en buscar Eventos
llm_estructurado_carreras = llm.with_structured_output(CarreraSchema)

# Cerebro 2: Experto en buscar Resultados en Clasificaciones
llm_estructurado_resultado = llm.with_structured_output(ResultadoSchema)
```

Hemos dividido la lógica en dos para mejorar la precisión.

#### Nueva Función: `buscar_resultado_usuario()`

Esta es la joya de la nueva actualización. Busca tu nombre en listados históricos.

```python
def buscar_resultado_usuario(nombre_carrera, año, nombre_corredor):
    # ESTRATEGIA:
    # 1. Buscamos nombres exactos y variantes (con/sin tildes)
    # 2. Si falla, busca listados PDF generales
    
    query = f'"{nombre_carrera}" {año} clasificación "{nombre_corredor}"'
    
    # ... Búsqueda con Tavily ...
    
    prompt = """
    Eres un experto rastreador de resultados.
    INSTRUCCIONES:
    1. Busca coincidencias de: {nombre_corredor}
    2. Extrae Tiempo, Posición y Ritmo.
    3. Si no está seguro, devuelve NULL (no inventes).
    """
    
    return llm_estructurado_resultado.invoke(prompt)
```

#### Funciones de Guardado (`database.py`)

Ahora `guardar_en_db` y `guardar_resultado_db` requieren un `user_id`.

```python
def guardar_en_db(datos, user_id):
    # Guarda carrera asociada a un usuario específico
    ...

def guardar_resultado_db(datos, carrera, año, user_id):
    # 1. Busca la carrera en la lista de ESE usuario
    # 2. Si existe, guarda el resultado asociado
    # 3. Si ya existía, evita duplicados
    ...
```

#### Función: `buscar_y_extraer_datos()`

```python
def buscar_y_extraer_datos(nombre_a_buscar: str, max_results: int = 6):
    if not nombre_a_buscar or not nombre_a_buscar.strip():
        raise ValueError("❌ ERROR: El nombre no puede estar vacío")
    
    año_actual = datetime.now().year  # 2026
    query_optimizada = f"fecha y distancias oficiales carrera {nombre_a_buscar} {año_actual}"
    print(f"Buscando: {nombre_a_buscar}...")
    
    try:
        # PASO 1: Buscar en internet con Tavily
        busqueda = tavily.search(query=query_optimizada, search_depth="advanced", max_results=max_results)
        
        if not busqueda.get('results'):
            raise ValueError(f"❌ No se encontraron resultados")
            
        # PASO 2: Juntar el contenido de todas las páginas
        contexto = "\n---\n".join([res['content'] for res in busqueda['results']])
        
        if not contexto.strip():
            raise ValueError("❌ Contexto vacío")
        
    except Exception as e:
        print(f"❌ Error en Tavily: {e}")
        raise
    
    # PASO 3: Crear el prompt para la IA
    prompt = f"""
    Eres un analista de datos deportivos. Extrae info de: {nombre_a_buscar}.
    
    Contexto encontrado en internet:
    {contexto}
    
    INSTRUCCIONES:
    1. FECHA: Solo fechas >= {año_actual}
    2. DISTANCIA: No inventes. Busca en 'Recorrido' o 'Reglamento'
    3. VERIFICACIÓN: Prioriza fuentes oficiales (.com/.es del evento)
    4. DEPORTE: Running, Trail, Ciclismo, Gravel, Triatlón, etc.
    """
    
    try:
        # PASO 4: Enviar prompt a la IA y obtener respuesta estructurada
        datos_extraidos = llm_estructurado.invoke(prompt)
        return datos_extraidos
    except Exception as e:
        print(f"❌ Error en LLM: {e}")
        raise
```

**¿Qué hace paso por paso?**

1. **Validación inicial**: Verifica que el nombre no esté vacío
2. **Construcción de query**: Crea una búsqueda optimizada para Tavily
3. **Búsqueda**: Tavily busca en internet (hasta 6 páginas)
4. **Extracción de contenido**: Junta todo el texto encontrado
5. **Prompt engineering**: Crea instrucciones detalladas para la IA
6. **Invocación del LLM**: La IA lee todo y devuelve un objeto `CarreraSchema`

**Ejemplo de búsqueda:**
```
Input: "Behobia"
Query: "fecha y distancias oficiales carrera Behobia 2026"
Tavily busca → 6 páginas web
Contexto: "... La carrera se celebrará el 9 de noviembre ... 20 kilómetros ..."
IA analiza → Devuelve CarreraSchema estructurado
```

#### Funciones de Ejecución

```python
def ejecutar_proyecto(nombre_a_buscar):
    """Versión CLI con confirmación manual"""
    datos_extraidos = buscar_y_extraer_datos(nombre_a_buscar)
    
    # Mostrar datos para validación humana
    print("\n" + "="*30)
    print("📋 DATOS ENCONTRADOS")
    print("="*30)
    print(f"🏆 Nombre: {datos_extraidos.nombre_oficial}")
    print(f"🚴 Deporte: {datos_extraidos.deporte}")
    print(f"📅 Fecha: {datos_extraidos.fecha}")
    # ... más campos ...
    
    confirmacion = input("\n¿Datos correctos? (s/n): ").lower()
    
    if confirmacion == 's':
        guardar_en_db(datos_extraidos)
    else:
        print("❌ Cancelado")

def procesar_carrera_desde_web(nombre_a_buscar: str):
    """Versión API sin confirmación manual"""
    print(f"🌍 WEB: {nombre_a_buscar}...")
    
    try:
        datos_extraidos = buscar_y_extraer_datos(nombre_a_buscar, max_results=5)
        guardar_en_db(datos_extraidos)
        return datos_extraidos
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    carrera = input("Carrera a añadir: ")
    ejecutar_proyecto(carrera)
```

**Diferencias:**
- `ejecutar_proyecto()`: Para uso desde terminal (pide confirmación)
- `procesar_carrera_desde_web()`: Para uso desde la API web (automático)

---

### 4.3 Archivo: `api.py`

**Propósito:** Servidor web que conecta el navegador con Python.

#### ¿Qué es FastAPI?

FastAPI es un framework (conjunto de herramientas) para crear APIs web modernas:
- **API** = Application Programming Interface = "Puente de comunicación"
- Recibe peticiones HTTP del navegador
- Ejecuta código Python
- Devuelve respuestas (normalmente en JSON)

#### Inicialización

```python
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, CarreraDB
from pydantic import BaseModel
from datetime import date
from main import buscar_y_extraer_datos, guardar_en_db, CarreraSchema
from pathlib import Path

app = FastAPI(title="RaceHub API")

BASE_DIR = Path(__file__).resolve().parent.parent
```

**Explicación:**
- `app = FastAPI()`: Crea la aplicación web
- `Path(__file__)`: Ruta del archivo actual (`api.py`)
- `.parent.parent`: Sube dos niveles (de `src/` a `racehub/`)

```python
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
```

**¿Qué hace `mount`?**
- Sirve archivos estáticos (CSS, JS, imágenes)
- Cuando el navegador pide `/static/styles.css`, FastAPI busca en `racehub/static/styles.css`

#### Modelos Pydantic para la API

```python
class CarreraOut(BaseModel):
    id: int
    nombre: str
    deporte: str
    fecha: date
    localizacion: str | None
    distancia_resumen: str | None
    url_oficial: str | None
    estado_inscripcion: str | None

    class Config:
        from_attributes = True
```

**¿Para qué sirve?**
Define cómo se enviarán las carreras al navegador (en formato JSON).

**`str | None`**: Puede ser texto o `None` (Python 3.10+)

**`from_attributes = True`**: Permite convertir objetos SQLAlchemy a JSON automáticamente.

#### Función de Dependencia

```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # "yield" es como "return" pero mantiene la función activa
    finally:
        db.close()
```

**¿Qué es `Depends`?**
FastAPI ejecuta `get_db()` automáticamente y pasa la sesión de BD al endpoint.

```python
@app.get("/carreras")
def listar_carreras(db: Session = Depends(get_db)):
    # FastAPI llama a get_db() y pasa el resultado a "db"
    carreras = db.query(CarreraDB).all()
    return carreras
```

#### Autenticación y Endpoints (Rutas)

**0. Simulación de Usuario (¡NUEVO!)**

El proyecto ahora es multi-usuario (en teoría). Para simplificar el desarrollo, simulamos el login:

```python
def get_current_user():
    # TEMPORAL: Siempre devuelve el Usuario con ID 1
    # En el futuro, esto leería un token o cookie segura
    return 1
```

**1. Página principal**

```python
@app.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

Renderiza la interfaz principal (sin cambios).

**2. Listar carreras (FILTRADAS por usuario)**

Ahora cada usuario ve solo SUS carreras.

```python
@app.get("/carreras/guardadas")
async def listar_carreras(user_id: int = Depends(get_current_user)):
    db = SessionLocal()
    # Filtramos por user_id
    carreras = db.query(CarreraDB).filter(CarreraDB.user_id == user_id).all()
    # ... código para formatear JSON ...
```

**3. Buscar Resultados (El cerebro de la App)**

Este endpoint conecta la base de datos con la IA para encontrar tu clasificación.

```python
@app.get("/resultados/buscar/{carrera_id}")
async def buscar_resultado(carrera_id: int, user_id: int = Depends(get_current_user)):
    db = SessionLocal()
    
    # a. Obtenemos datos de la carrera y del usuario
    carrera = db.query(CarreraDB).filter(CarreraDB.id == carrera_id).first()
    usuario = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    # b. Llamamos a la IA con el nombre REAL del usuario
    try:
        resultado_ia = buscar_resultado_usuario(
            carrera.nombre, 
            carrera.year, 
            usuario.nombre
        )
        # ... lógica de guardado si hay éxito ...
        return {"status": "success", "data": resultado_ia}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

**4. Gestión de Perfil**

Permite al usuario cambiar el nombre que usa la IA para buscarlo.

```python
@app.post("/perfil")
async def actualizar_perfil(data: dict, user_id: int = Depends(get_current_user)):
    # Actualiza el nombre en la tabla users
    # ...
```
- `solicitud: SolicitudCarrera`: FastAPI automáticamente valida el JSON recibido
- `HTTPException`: Devuelve un error HTTP al navegador

**4. Confirmar y guardar**

```python
@app.post("/carreras/confirmar")
def confirmar_carrera(datos: ConfirmacionCarrera):
    try:
        carrera_schema = CarreraSchema(
            nombre_oficial=datos.nombre_oficial,
            # ... resto de campos
        )
        guardar_en_db(carrera_schema)
        return {"mensaje": "Guardada", "nombre": datos.nombre_oficial}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**5. Eliminar carrera**

```python
@app.delete("/carreras/{carrera_id}")
def eliminar_carrera(carrera_id: int, db: Session = Depends(get_db)):
    carrera = db.query(CarreraDB).filter(CarreraDB.id == carrera_id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="No encontrada")
    
    nombre = carrera.nombre
    db.delete(carrera)
    db.commit()
    return {"mensaje": f"'{nombre}' eliminada"}
```

- `{carrera_id}`: Parámetro de ruta (ej: `/carreras/5` → `carrera_id=5`)
- `.filter()`: Equivalente a `WHERE id = 5`
- `.first()`: Devuelve el primer resultado o `None`

---

## 5. JavaScript - Frontend Explicado

### 5.1 ¿Qué es JavaScript?

JavaScript es el lenguaje de programación que se ejecuta **en el navegador** (no en el servidor).

**Funciones principales:**
- Interactividad (botones, formularios)
- Comunicación con el servidor (sin recargar la página)
- Manipulación del HTML (añadir/quitar elementos)

### 5.2 Conceptos Básicos de JavaScript

#### Variables

```javascript
let nombre = "Behobia";           // Variable que puede cambiar
const PI = 3.14159;               // Constante (no cambia)
var antigua = "No usar";          // Forma antigua (evitar)
```

#### Funciones

```javascript
// Función tradicional
function sumar(a, b) {
    return a + b;
}

// Función flecha (moderna)
const sumar = (a, b) => {
    return a + b;
};

// Función flecha corta
const sumar = (a, b) => a + b;
```

#### Async/Await (Promesas)

```javascript
// ❌ INCORRECTO - La respuesta aún no ha llegado
const response = fetch('/carreras');
const data = response.json();  // Error!

// ✅ CORRECTO - Espera la respuesta
async function cargarDatos() {
    const response = await fetch('/carreras');  // Espera la respuesta HTTP
    const data = await response.json();         // Espera convertir a JSON
    console.log(data);
}
```

**`async`**: Marca una función como asíncrona (puede usar `await`)
**`await`**: Pausa la ejecución hasta que la promesa se resuelva

#### Manipulación del DOM

**DOM** = Document Object Model = "Estructura del HTML en memoria"

```javascript
// Obtener un elemento
const boton = document.getElementById('btnBuscar');

// Cambiar texto
boton.textContent = "Nuevo texto";

// Cambiar estilos
boton.style.backgroundColor = "red";

// Añadir HTML
document.getElementById('lista').innerHTML = '<p>Hola</p>';
```

### 5.3 Código de `index.html` Explicado

#### Variables Globales y Caché

```javascript
let datosEncontrados = null;      // Última búsqueda de IA
let vistaActual = 'tabla';        // Vista activa
let carrerasCache = {};           // ¡CLAVE! Almacena carreras + resultados ya buscados
```

**La importancia de `carrerasCache`:**
Ahora no es solo una lista. Es un objeto donde guardamos los resultados de las carreras pasadas para no tener que volver a consultar a la IA (que es lenta y costosa) cada vez que el usuario hace clic.

#### Lógica de Detección de Fecha (`cargarCarreras`)

Cuando cargamos las carreras, el sistema "piensa":

```javascript
const diferenciaDias = (fechaCarrera - hoy) / (1000 * 60 * 60 * 24);

if (diferenciaDias < -1) {
    // Es una carrera PASADA
    // Mostramos botón de MEDALLA 🏅
} else {
    // Es FUTURA
    // Mostramos botón de ELIMINAR 🗑️
}
```

#### El Cerebro del Frontend: `gestionResultado(id)`

Esta función es la que da la sensación de "magia" instantánea.

1. **Revisa la memoria local:** ¿Ya tengo el resultado en `carrerasCache[id].resultado`?
2. **Si SÍ:** Muestra el modal INSTANTÁNEAMENTE.
3. **Si NO:**
   - Muestra "Cargando..."
   - Llama a la API `/resultados/buscar/{id}`
   - Cuando la API responde, GUARDA el dato en `carrerasCache` para la próxima vez.
   - Muestra el modal.

```javascript
async function gestionResultado(id) {
    const carrera = carrerasCache[id];
    
    // CACHÉ: Si ya lo tenemos, no molestamos al servidor
    if (carrera.resultado) {
        mostrarModalResultado(carrera.resultado);
        return;
    }
    
    // API: Si no, buscamos
    mostrarCargando();
    const res = await fetch(`/resultados/buscar/${id}`);
    const data = await res.json();
    
    if (data.status === 'success') {
        carrera.resultado = data.data; // ¡Guardamos en caché!
        mostrarModalResultado(data.data);
    }
}
```

#### Perfil de Usuario

Para que la búsqueda funcione, necesitamos saber **a quién buscar**. 

- Creamos un modal que pide tu "Nombre de Corredor".
- Se guarda en el servidor (`POST /perfil`) y en una variable global.
- Se usa automáticamente en cada búsqueda de resultados.
    const carreras = await response.json();
    
    // Guarda en caché
    carrerasCache = carreras;
    
    // Renderiza
    renderizarCarreras(carreras);
}
```

**¿Qué devuelve `fetch`?**
```javascript
// Si la API devuelve:
[
  {"id": 1, "nombre": "Behobia", "fecha": "2025-11-09"},
  {"id": 2, "nombre": "Maratón", "fecha": "2026-04-20"}
]

// Entonces carreras será:
[
  {id: 1, nombre: "Behobia", fecha: "2025-11-09"},
  {id: 2, nombre: "Maratón", fecha: "2026-04-20"}
]
```

#### Función: `renderizarCarreras()`

```javascript
function renderizarCarreras(carreras) {
    const listaDiv = document.getElementById('lista-carreras');
    
    // Si no hay carreras, mostrar mensaje
    if (!carreras || carreras.length === 0) {
        listaDiv.innerHTML = '<p>📭 No hay carreras</p>';
        return;  // Sale de la función
    }
    
    // Ordenar por fecha (más antigua primero)
    carreras.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
    
    // Decidir qué vista usar
    if (vistaActual === 'tabla') {
        renderizarTabla(carreras, listaDiv);
    } else {
        renderizarCalendario(carreras, listaDiv);
    }
}
```

**`.sort()` explicado:**
```javascript
// Función de comparación
(a, b) => new Date(a.fecha) - new Date(b.fecha)

// Si a.fecha es antes que b.fecha → número negativo → a va primero
// Si a.fecha es después que b.fecha → número positivo → b va primero
```

#### Función: `renderizarTabla()`

```javascript
function renderizarTabla(carreras, listaDiv) {
    let html = `<table>
        <tr>
            <th>Fecha</th>
            <th>Carrera</th>
            <th>Deporte</th>
            <th>Lugar</th>
            <th>Estado</th>
            <th>Acción</th>
        </tr>`;

    // forEach = "para cada" carrera
    carreras.forEach(c => {
        // Template literal: ${variable} se reemplaza con su valor
        html += `<tr>
            <td>${c.fecha}</td>
            <td>
                <strong>${c.nombre}</strong><br>
                <small>${c.distancia_resumen || ''}</small>
            </td>
            <td>${c.deporte}</td>
            <td>${c.localizacion}</td>
            <td><span class="badge ${c.estado_inscripcion}">${c.estado_inscripcion}</span></td>
            <td>
                <button onclick="eliminarCarrera(${c.id}, '${c.nombre}')">🗑️</button>
            </td>
        </tr>`;
    });
    
    html += '</table>';
    listaDiv.innerHTML = html;  // Reemplaza todo el contenido del div
}
```

**Operador OR (`||`):**
```javascript
c.distancia_resumen || ''
// Si c.distancia_resumen es null/undefined/vacío → usa ''
// Si c.distancia_resumen tiene valor → usa ese valor
```

#### Función: `renderizarCalendario()`

```javascript
function renderizarCalendario(carreras, listaDiv) {
    // Objeto para agrupar carreras por mes
    const carrerasPorMes = {};
    
    carreras.forEach(c => {
        const fecha = new Date(c.fecha);
        
        // Crear clave: "2025-11"
        const mesKey = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
        
        // Si no existe ese mes, crear array vacío
        if (!carrerasPorMes[mesKey]) {
            carrerasPorMes[mesKey] = [];
        }
        
        // Añadir carrera al mes
        carrerasPorMes[mesKey].push(c);
    });

    let html = '<div class="calendario-container">';
    
    // Object.keys() devuelve un array con las claves ["2025-11", "2026-04", ...]
    Object.keys(carrerasPorMes).sort().forEach(mesKey => {
        const [ano, mes] = mesKey.split('-');  // "2025-11" → ["2025", "11"]
        
        // Crear fecha y formatear nombre del mes
        const nombreMes = new Date(ano, mes - 1).toLocaleDateString('es-ES', { 
            month: 'long',    // "noviembre"
            year: 'numeric'   // "2025"
        });
        
        html += `<div class="mes-grupo">
            <h3 class="mes-titulo">${nombreMes.charAt(0).toUpperCase() + nombreMes.slice(1)}</h3>
            <div class="carreras-mes">`;
        
        carrerasPorMes[mesKey].forEach(c => {
            const fecha = new Date(c.fecha);
            const dia = fecha.getDate();  // 9
            const diaSemana = fecha.toLocaleDateString('es-ES', { weekday: 'short' });  // "dom"
            
            html += `<div class="carrera-card">
                <div class="carrera-fecha">
                    <div class="dia">${dia}</div>
                    <div class="dia-semana">${diaSemana}</div>
                </div>
                <div class="carrera-info">
                    <h4>${c.nombre}</h4>
                    <p>📍 ${c.localizacion}</p>
                    <p>🏃 ${c.deporte} - ${c.distancia_resumen || ''}</p>
                    <span class="badge ${c.estado_inscripcion}">${c.estado_inscripcion}</span>
                </div>
                <div class="carrera-acciones">
                    <button onclick="eliminarCarrera(${c.id}, '${c.nombre}')">🗑️</button>
                </div>
            </div>`;
        });
        
        html += '</div></div>';
    });
    
    html += '</div>';
    listaDiv.innerHTML = html;
}
```

**`.padStart(2, '0')`:**
```javascript
String(5).padStart(2, '0')   // "05"
String(11).padStart(2, '0')  // "11"
```

**Destructuring:**
```javascript
const [ano, mes] = mesKey.split('-');
// Es equivalente a:
const partes = mesKey.split('-');
const ano = partes[0];
const mes = partes[1];
```

#### Función: `buscarCarrera()`

```javascript
async function buscarCarrera() {
    const input = document.getElementById('nombreInput');
    const btn = document.getElementById('btnBuscar');
    const loading = document.getElementById('loading');
    const confirmacionDiv = document.getElementById('confirmacion');
    const nombre = input.value;

    if (!nombre) return alert("Escribe un nombre primero");

    confirmacionDiv.style.display = 'none';
    btn.disabled = true;
    loading.style.display = 'block';

    try {
        // Petición POST con datos JSON
        const response = await fetch('/carreras/buscar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre: nombre })  // Convierte objeto a JSON
        });

        if (response.ok) {
            datosEncontrados = await response.json();
            
            // Construir HTML de confirmación
            confirmacionDiv.innerHTML = `
                <div style="background: #e8f5e9; padding: 20px; ...">
                    <h3>📋 Datos encontrados:</h3>
                    <p><strong>🏆 Nombre:</strong> ${datosEncontrados.nombre_oficial}</p>
                    <!-- más campos -->
                    <div>
                        <button onclick="confirmarGuardado()">✅ Confirmar</button>
                        <button onclick="cancelarBusqueda()">❌ Cancelar</button>
                    </div>
                </div>
            `;
            confirmacionDiv.style.display = 'block';
            input.value = '';
        } else {
            const error = await response.json();
            alert("❌ Error: " + error.detail);
        }
    } catch (err) {
        alert("❌ Error de conexión: " + err);
    } finally {
        // Siempre se ejecuta (haya error o no)
        btn.disabled = false;
        loading.style.display = 'none';
    }
}
```

**`JSON.stringify()`:**
```javascript
const obj = { nombre: "Behobia" };
JSON.stringify(obj)  // '{"nombre":"Behobia"}'
```

**`response.ok`:**
- `true` si el código HTTP es 200-299
- `false` si es 400+ (error)

#### Función: `confirmarGuardado()`

```javascript
async function confirmarGuardado() {
    if (!datosEncontrados) return;

    try {
        const response = await fetch('/carreras/confirmar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datosEncontrados)
        });

        if (response.ok) {
            document.getElementById('confirmacion').style.display = 'none';
            cargarCarreras();  // Recarga la tabla
            alert("✅ Guardada!");
            datosEncontrados = null;  // Limpia los datos
        } else {
            const error = await response.json();
            alert("❌ Error: " + error.detail);
        }
    } catch (err) {
        alert("❌ Error de conexión");
    }
}
```

#### Función: `eliminarCarrera()`

```javascript
async function eliminarCarrera(id, nombre) {
    // Pedir confirmación
    if (!confirm(`¿Eliminar "${nombre}"?`)) {
        return;  // Si el usuario cancela, sale de la función
    }

    try {
        const response = await fetch(`/carreras/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            cargarCarreras();  // Recarga la tabla
            alert(`✅ "${nombre}" eliminada`);
        } else {
            const error = await response.json();
            alert("❌ Error: " + error.detail);
        }
    } catch (err) {
        alert("❌ Error de conexión");
    }
}
```

**Template literals en URL:**
```javascript
`/carreras/${id}`
// Si id = 5 → "/carreras/5"
```

#### Carga Inicial

```javascript
// Cargar al inicio (cuando se carga la página)
cargarCarreras();
```

Este código se ejecuta automáticamente al cargar el HTML.

---

## 6. Flujo Completo de Datos

### Caso 1: Añadir una Carrera

```
1. Usuario escribe "Behobia" y hace clic en "Añadir"
   ↓
2. JavaScript llama a buscarCarrera()
   ↓
3. fetch('/carreras/buscar', POST, {nombre: "Behobia"})
   ↓
4. FastAPI recibe la petición
   ↓
5. api.py llama a buscar_y_extraer_datos("Behobia")
   ↓
6. main.py busca en Tavily → obtiene contexto
   ↓
7. main.py envía contexto al LLM (Llama 3.3)
   ↓
8. LLM devuelve CarreraSchema estructurado
   ↓
9. FastAPI devuelve JSON al navegador
   ↓
10. JavaScript muestra los datos en pantalla
   ↓
11. Usuario hace clic en "Confirmar"
   ↓
12. JavaScript llama a confirmarGuardado()
   ↓
13. fetch('/carreras/confirmar', POST, datos)
   ↓
14. FastAPI recibe y llama a guardar_en_db()
   ↓
15. SQLAlchemy ejecuta INSERT en PostgreSQL
   ↓
16. PostgreSQL guarda la carrera
   ↓
17. FastAPI devuelve {mensaje: "Guardada"}
   ↓
18. JavaScript recarga la tabla con cargarCarreras()
```

### Caso 2: Ver Carreras

```
1. Usuario abre http://localhost:8000
   ↓
2. JavaScript ejecuta cargarCarreras()
   ↓
3. fetch('/carreras', GET)
   ↓
4. FastAPI llama a listar_carreras()
   ↓
5. SQLAlchemy ejecuta SELECT * FROM carreras
   ↓
6. PostgreSQL devuelve las filas
   ↓
7. FastAPI convierte a JSON
   ↓
8. JavaScript recibe el array
   ↓
9. renderizarCarreras() construye el HTML
   ↓
10. innerHTML actualiza la página
```

### Caso 3: Eliminar Carrera

```
1. Usuario hace clic en 🗑️
   ↓
2. JavaScript pide confirmación
   ↓
3. Si confirma → fetch('/carreras/5', DELETE)
   ↓
4. FastAPI llama a eliminar_carrera(5)
   ↓
5. SQLAlchemy busca la carrera con id=5
   ↓
6. db.delete() marca para eliminar
   ↓
7. db.commit() ejecuta DELETE en PostgreSQL
   ↓
8. PostgreSQL elimina la fila
   ↓
9. FastAPI devuelve {mensaje: "Eliminada"}
   ↓
10. JavaScript recarga la tabla
```

---

## 7. Conceptos Clave de Programación

### 7.1 Variables de Entorno (`.env`)

**¿Por qué usar `.env`?**
- Guarda información sensible (claves API, contraseñas)
- No se sube a Git (está en `.gitignore`)
- Fácil de cambiar sin tocar el código

**Ejemplo de `.env`:**
```
TAVILY_API_KEY=tvly-abc123def456
GROQ_API_KEY=gsk_xyz789
DATABASE_URL=postgresql://jaime:6999@localhost:5432/racehub
```

**En Python:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Lee el archivo .env
api_key = os.getenv("TAVILY_API_KEY")  # Obtiene el valor
```

### 7.2 ORM (Object-Relational Mapping)

**Problema:** SQL y Python hablan "idiomas" diferentes.

**Solución:** ORM traduce entre objetos Python y tablas SQL.

```python
# SIN ORM (SQL puro)
cursor.execute("INSERT INTO carreras (nombre, fecha) VALUES ('Behobia', '2025-11-09')")

# CON ORM (SQLAlchemy)
nueva_carrera = CarreraDB(nombre="Behobia", fecha="2025-11-09")
db.add(nueva_carrera)
db.commit()
```

**Ventajas:**
- Más seguro (previene SQL injection)
- Más legible
- Cambiar de base de datos es más fácil

### 7.3 API REST

**REST** = Representational State Transfer

**Principios:**
- Cada recurso tiene una URL (`/carreras`, `/carreras/5`)
- Se usan verbos HTTP estándar:
  - `GET`: Obtener datos
  - `POST`: Crear nuevos datos
  - `PUT/PATCH`: Actualizar datos
  - `DELETE`: Eliminar datos

**Ejemplo:**
```
GET    /carreras       → Lista todas las carreras
POST   /carreras       → Crea una nueva carrera
GET    /carreras/5     → Obtiene la carrera con id=5
DELETE /carreras/5     → Elimina la carrera con id=5
```

### 7.4 JSON (JavaScript Object Notation)

Formato estándar para intercambiar datos entre el navegador y el servidor.

```json
{
  "id": 1,
  "nombre": "Behobia",
  "fecha": "2025-11-09",
  "distancias": ["20km"],
  "estado": null
}
```

**Tipos de datos:**
- `"texto"`: Strings
- `123`: Números
- `true/false`: Booleanos
- `null`: Valor nulo
- `[]`: Arrays
- `{}`: Objetos

### 7.5 Promesas y Async/Await

**Problema:** Operaciones que tardan (peticiones HTTP, consultas a BD).

**Solución antigua (callbacks - difícil de leer):**
```javascript
fetch('/carreras', function(response) {
    response.json(function(data) {
        console.log(data);
    });
});
```

**Solución moderna (async/await - fácil de leer):**
```javascript
async function cargar() {
    const response = await fetch('/carreras');
    const data = await response.json();
    console.log(data);
}
```

### 7.6 Try-Catch (Manejo de Errores)

```python
try:
    # Código que PUEDE fallar
    resultado = 10 / 0
except ZeroDivisionError as e:
    # Si falla con este error específico
    print("No se puede dividir por cero")
except Exception as e:
    # Cualquier otro error
    print(f"Error: {e}")
finally:
    # Siempre se ejecuta
    print("Limpieza")
```

### 7.7 Validación con Pydantic

```python
from pydantic import BaseModel, Field, validator

class Usuario(BaseModel):
    nombre: str = Field(min_length=3, max_length=50)
    edad: int = Field(ge=0, le=120)  # ge = Greater or Equal
    email: str
    
    @validator('email')
    def validar_email(cls, v):
        if '@' not in v:
            raise ValueError("Email inválido")
        return v

# ✅ Válido
usuario = Usuario(nombre="Juan", edad=30, email="juan@example.com")

# ❌ Error - nombre muy corto
usuario = Usuario(nombre="J", edad=30, email="juan@example.com")
```

---

## 8. Comandos para Ejecutar el Proyecto

### 8.1 Primera Vez (Configuración Inicial)

```bash
# 1. Clonar o crear el proyecto
cd /home/jaime/01Proyectos/racehub

# 2. Crear entorno virtual
python3 -m venv venv

# 3. Activar entorno virtual
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar y añadir tus claves API

# 6. Crear (o REINICIAR) base de datos
# ¡OJO! El nuevo script schema.sql borra las tablas antiguas para añadir
# el sistema de usuarios. Si tenías datos, se perderán.
psql -U jaime -d racehub -f db/schema.sql
```

### 8.2 Uso Diario

```bash
# 1. Activar entorno virtual
cd /home/jaime/01Proyectos/racehub
source venv/bin/activate

# 2. Iniciar servidor web
python -m uvicorn src.api:app --reload

# 3. Abrir navegador en:
# http://127.0.0.1:8000
# o también: http://localhost:8000
```

**Explicación de comandos:**
- `python -m uvicorn`: Ejecuta uvicorn como módulo de Python (asegura imports correctos)
- `src.api:app`: Ubicación del objeto FastAPI (archivo `src/api.py`, variable `app`)
- `--reload`: Reinicia automáticamente el servidor cuando cambias código (solo en desarrollo)

### 8.3 Añadir Carrera desde Terminal (CLI)

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar script
python src/main.py
# Te pedirá el nombre de la carrera
# Mostrará los datos encontrados
# Pedirá confirmación (s/n)
```

### 8.4 Comandos de PostgreSQL

```bash
# Conectar a la base de datos
psql -U jaime -d racehub

# Dentro de psql:
\dt                    # Ver tablas
SELECT * FROM carreras; # Ver todas las carreras
\q                     # Salir
```

### 8.5 Comandos de Git

```bash
# Ver cambios
git status

# Añadir cambios
git add .

# Commit
git commit -m "Descripción del cambio"

# Subir a GitHub
git push origin main
```

---

## 9. Nuevas Funcionalidades: Sistema de Compartir

Recientemente se ha añadido la capacidad de compartir tu calendario públicamente.

### 9.1 ¿Cómo funciona?

1.  Cada usuario tiene un **token único** (código secreto) asociado a su cuenta.
2.  Al pulsar "Compartir", se genera una URL pública como: `/share/AbC123XyZ`.
3.  Cualquier persona con ese enlace puede ver (pero no editar) tu calendario.

### 9.2 Cambios Técnicos Realizados

**Base de Datos:**
- Se ha modificado la tabla `users` para añadir la columna `share_token`.
- Se usa `shortuuid` para generar identificadores cortos y seguros.

**API (api.py):**
- `GET /share/token`: Genera o recupera el token del usuario actual.
- `GET /share/{token}`: Carga el HTML público para el visitante.
- `GET /api/share/{token}/carreras`: Devuelve los datos JSON de las carreras asociadas a ese token (sin necesidad de login).

**Frontend:**
- **index.html**: Añadido botón "Compartir" y ventana modal para copiar el enlace.
- **public.html**: Nueva lógica JS para detectar el token en la URL y cambiar el título ("Calendario de Jaime").
- **Seguridad**: Las vistas compartidas son de **solo lectura**. Los visitantes no ven botones de eliminar ni formularios de búsqueda.

---

## 📝 Resumen Final

### Flujo de Ejecución Simplificado

1. **Usuario abre la web** → FastAPI sirve `index.html`
2. **Usuario busca carrera** → JavaScript llama a `/carreras/buscar`
3. **API busca con IA** → Tavily + Groq extraen datos
4. **Muestra resultados** → Usuario confirma
5. **Guarda en BD** → SQLAlchemy ejecuta INSERT
6. **Actualiza vista** → JavaScript recarga la tabla

### Archivos Clave y Sus Funciones

| Archivo | Responsabilidad |
|---------|----------------|
| `database.py` | Conectar Python ↔ PostgreSQL |
| `main.py` | Buscar con IA y extraer datos |
| `api.py` | Servidor web (FastAPI) |
| `index.html` | Interfaz visual + JavaScript |
| `styles.css` | Diseño y colores |
| `.env` | Claves secretas |

### Tecnologías en Una Frase

- **PostgreSQL**: Base de datos donde se guardan las carreras
- **SQLAlchemy**: Traductor entre Python y SQL
- **FastAPI**: Servidor web que recibe peticiones
- **Tavily**: Buscador inteligente para IA
- **Groq/Llama 3.3**: Cerebro de IA que extrae datos
- **Pydantic**: Validador que asegura datos correctos
- **JavaScript**: Código que se ejecuta en el navegador
- **HTML/CSS**: Estructura y diseño visual

### Próximos Pasos Sugeridos

1. **Añade más validaciones**: Por ejemplo, verificar que la fecha no sea del pasado
2. **Exporta a PDF/Excel**: Añade un botón para descargar el calendario
3. **Notificaciones**: Avisa cuando se acerque una carrera
4. **Mejora la búsqueda**: Añade filtros por deporte, mes, etc.
5. **Tests**: Crea tests automatizados para las funciones principales

---

## 🎓 Glosario de Términos

- **API**: Interfaz que permite comunicación entre programas
- **Async**: Código que no bloquea (permite hacer otras cosas mientras espera)
- **Backend**: Parte del servidor (Python, base de datos)
- **CLI**: Command Line Interface (terminal)
- **Commit**: Confirmar cambios en la base de datos
- **Endpoint**: URL específica de una API (`/carreras`)
- **Frontend**: Parte del navegador (HTML, CSS, JavaScript)
- **JSON**: Formato de datos en texto
- **LLM**: Large Language Model (modelo de IA)
- **ORM**: Traductor entre objetos Python y SQL
- **Prompt**: Instrucciones que le das a la IA
- **REST**: Estilo de diseño de APIs
- **Schema**: Estructura/molde de datos
- **Session**: Conversación temporal con la base de datos

---
