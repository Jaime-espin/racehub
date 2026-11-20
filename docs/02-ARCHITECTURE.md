# Arquitectura de RaceHub

## Diagrama General

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB BROWSER / USER                       │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST
┌────────────────▼────────────────────────────────────────────┐
│                   FastAPI Web Server                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Frontend (HTML/CSS/JavaScript con IA) - /          │  │
│  │  API REST Endpoints                                 │  │
│  │    - POST /carreras/buscar      (buscar carrera)    │  │
│  │    - POST /carreras/confirmar   (guardar carrera)   │  │
│  │    - POST /resultados/buscar    (buscar resultado)  │  │
│  │    - GET  /carreras             (listar carreras)   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌──────────┐
│ Tavily  │  │  Groq   │  │PostgreSQL│
│ Search  │  │  LLM    │  │ Database │
└─────────┘  └─────────┘  └──────────┘
```

## Estructura de Carpetas

```
racehub/
├── src/                          # Codigo fuente Python
│   ├── main.py                  # Nucleo: busqueda y guardado
│   ├── api.py                   # API REST con FastAPI
│   ├── database.py              # Modelos ORM y conexiones
│   └── busqueda_realista.py    # Busqueda avanzada de resultados (portales, URL, archivos)
│
├── templates/                   # Archivos HTML
│   ├── index.html              # Interfaz principal (autenticada)
│   └── public.html             # Version compartida (publica)
│
├── static/                      # Archivos estaticos (CSS y JS)
│   ├── script.js               # Logica del frontend
│   └── styles.css              # Estilos CSS
│
├── db/                         # Base de datos
│   └── schema.sql              # Esquema de tablas
│
├── docs/                       # Documentacion tecnica
│   ├── 01-SETUP.md            # Instalacion
│   ├── 02-ARCHITECTURE.md     # Arquitectura
│   ├── 03-USER-GUIDE.md       # Guia de usuario
│   ├── 04-API-REFERENCE.md    # Referencia API
│   └── 05-TROUBLESHOOTING.md  # Troubleshooting
│
├── README.md                   # Punto de entrada de la documentacion
├── requirements.txt            # Dependencias del proyecto
├── .env.example               # Variables de entorno template
├── .env                       # Variables de entorno (no versionado)
└── Procfile                   # Configuracion para despliegue
```

## Flujo de Datos

### 1. Busqueda de Carreras (src/main.py)

```
Usuario pide: "Barcelona Marathon 2026"
    ↓
[Tavily Search]
    - Query: "Barcelona Marathon 2026 fechas distancias"
    - Motor de busqueda
    ↓
[Groq LLM + Pydantic]
    - Extrae: nombre, deporte, fecha, lugar, distancias
    - Valida contra schema CarreraSchema
    ↓
[Confirmacion de Usuario]
    - Muestra datos al usuario en la interfaz web
    - Confirmacion previa a la persistencia
    ↓
[PostgreSQL]
    - Guarda en tabla 'carreras'
    - Control de duplicados
```

### 2. Busqueda de Resultados (src/busqueda_realista.py)

```
Usuario busca marca en carrera finalizada
    ↓
[Estrategia 1: Portales Conocidos]
    - Detecta si es Sportmaniacs, ChronoEmpresa, etc.
    - Usa regex especifico para cada portal
    ↓
[Estrategia 2: Busqueda Web]
    - Tavily busca:
      1. "{carrera} {ano} clasificacion {nombre}"
      2. "{carrera} {ano} resultados pdf"
    ↓
[Estrategia 3: Subida de Archivos]
    - Usuario sube PDF o CSV con resultados
    - Extrae texto y busca nombre
    ↓
[Groq LLM]
    - Extrae: tiempo, posicion, ritmo
    - Valida contra schema ResultadoSchema
    ↓
[PostgreSQL]
    - Guarda en tabla 'resultados'
    - Vinculado a usuario y carrera
```

## Modelo de Datos

### Tabla: `users`
```sql
id                INTEGER (PRIMARY KEY)
nombre_completo   VARCHAR
email             VARCHAR (UNIQUE)
share_token       VARCHAR (opcional)
```

### Tabla: `carreras`
```sql
id                INTEGER (PRIMARY KEY)
user_id           INTEGER (FOREIGN KEY → users.id)
nombre            VARCHAR
deporte           VARCHAR (running, trail, ciclismo, etc.)
fecha             DATE
localizacion      VARCHAR
distancia_resumen VARCHAR
url_oficial       VARCHAR
estado_inscripcion VARCHAR (abierta, cerrada, pendiente)
estado_planificacion VARCHAR (candidata, seleccionada, inscrita, descartada)
fecha_inscripcion DATE
```

### Tabla: `resultados`
```sql
id                INTEGER (PRIMARY KEY)
carrera_id        INTEGER (FOREIGN KEY → carreras.id)
tiempo_oficial    VARCHAR (ej: "1:30:45")
posicion_general  INTEGER
posicion_categoria INTEGER
ritmo_medio       VARCHAR (ej: "4:30 min/km")
confianza         INTEGER (0-100, nivel de confianza)
comentarios       VARCHAR
```

## Modelos de IA

### Pydantic Schemas

**CarreraSchema** (src/main.py)
```python
class CarreraSchema(BaseModel):
    nombre_oficial: str
    deporte: str
    fecha: str  # YYYY-MM-DD
    lugar: str
    distancias: List[str]
    url_oficial: Optional[str]
    estado_inscripcion: str  # abierta|cerrada|pendiente
```

**ResultadoSchema** (src/main.py)
```python
class ResultadoSchema(BaseModel):
    tiempo_oficial: Optional[str]
    posicion_general: Optional[int]
    posicion_categoria: Optional[int]
    ritmo_medio: Optional[str]
    confianza: Optional[float]  # 0.0-1.0
```

## Componentes Externos

| Componente | Uso | Sitio Web |
|---|---|---|
| **Tavily** | Motor de busqueda hiper-optimizado | https://tavily.com |
| **Groq** | LLM (Language Model) Llama 3.3 | https://groq.com |
| **PostgreSQL** | Base de datos relacional | https://postgresql.org |
| **FastAPI** | Framework web Python | https://fastapi.tiangolo.com |
| **SQLAlchemy** | ORM (Object-Relational Mapping) | https://sqlalchemy.org |

## Seguridad

- **Variables de entorno**: Claves API en `.env` (no versionado).
- **Validacion Pydantic**: Rechaza datos mal formados antes de la persistencia.
- **Autenticacion**: Basada en cookies HTTP seguras (`user_email`).

## Escalabilidad

- **Base de datos**: PostgreSQL con indices en claves foraneas y emails.
- **API**: FastAPI con uvicorn (arquitectura ASGI asincrona).
