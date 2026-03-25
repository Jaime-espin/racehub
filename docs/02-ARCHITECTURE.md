# 🏗️ Arquitectura de RaceHub

## 📐 Diagrama General

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB BROWSER / USER                       │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST
┌────────────────▼────────────────────────────────────────────┐
│                   FastAPI Web Server                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Frontend (HTML/CSS/JavaScript)  - /                │  │
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

## 🗂️ Estructura de Carpetas

```
racehub/
├── src/                          # Código fuente Python
│   ├── __pycache__/             # Cache de Python (ignorar)
│   ├── main.py                  # Núcleo: búsqueda y guardado
│   ├── api.py                   # API REST con FastAPI
│   ├── database.py              # Modelos ORM y conexiones
│   ├── busqueda_realista.py    # Búsqueda avanzada de resultados
│   └── busqueda_mejorada.py    # Búsqueda alternativa de resultados
│
├── templates/                   # Archivos HTML
│   ├── index.html              # Interfaz principal (autenticada)
│   └── public.html             # Versión compartida (pública)
│
├── static/                      # Archivos estáticos (CSS/JS/imágenes)
│   ├── script.js               # Lógica del frontend
│   └── styles.css              # Estilos CSS
│
├── db/                         # Base de datos
│   └── schema.sql              # Esquema de tablas
│
├── docs/                       # Documentación (este archivo)
│   ├── 01-SETUP.md            # Instalación
│   ├── 02-ARCHITECTURE.md     # Este archivo
│   ├── 03-USER-GUIDE.md       # Guía de usuario
│   ├── 04-API-REFERENCE.md    # Referencia API
│   └── 05-TROUBLESHOOTING.md  # Troubleshooting
│
├── README.md                   # Punto de entrada de la documentación
├── requirements-clean.txt      # Dependencias (simplificado)
├── requirements.txt            # Dependencias (completo con transitivas)
├── .env.example               # Variables de entorno template
├── .env                       # Variables de entorno (no versionado)
└── Procfile                   # Configuración para Heroku (opcional)
```

## 🔄 Flujo de Datos

### 1. **Búsqueda de Carreras** (src/main.py)

```
Usuario pide: "Barcelona Marathon 2026"
    ↓
[Tavily Search]
    - Query: "Barcelona Marathon 2026 fechas distancias"
    - Motor de búsqueda inteligente
    ↓
[Groq LLM + Pydantic]
    - Extrae: nombre, deporte, fecha, lugar, distancias
    - Valida contra schema CarreraSchema
    ↓
[Human-in-the-loop]
    - Muestra datos al usuario
    - Pide confirmación manual (CLI)
    ↓
[PostgreSQL]
    - Guarda en tabla 'carreras'
    - Control de duplicados
```

### 2. **Búsqueda de Resultados** (src/busqueda_realista.py)

```
Usuario busca: "Mi tiempo en Barcelona Marathon 2026"
    ↓
[Estrategia 1: Portales Conocidos]
    - Detecta si es Sportmaniacs, ChronoEmpresa, etc.
    - Usa regex específico para cada portal
    ↓
[Estrategia 2: Búsqueda Web]
    - Tavily busca:
      1. "{carrera} {año} clasificación {nombre}"
      2. "{carrera} {año} resultados pdf"
    ↓
[Estrategia 3: Upload de Archivos]
    - Usuario sube PDF o CSV con resultados
    - Extrae texto y busca nombre
    ↓
[Groq LLM]
    - Extrae: tiempo, posición, ritmo
    - Valida contra schema ResultadoSchema
    ↓
[PostgreSQL]
    - Guarda en tabla 'resultados'
    - Vinculado a usuario y carrera
```

## 🗄️ Modelo de Datos

### Tabla: `users`
```sql
id                INTEGER (PRIMARY KEY)
nombre_completo   VARCHAR
email             VARCHAR (UNIQUE)
share_token       VARCHAR (opctional)
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

## 🤖 Modelos de IA

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

## 🔌 Componentes Externos

| Componente | Uso | Sitio Web |
|-----------|-----|----------|
| **Tavily** | Motor de búsqueda hiper-optimizado | https://tavily.com |
| **Groq** | LLM (Language Model) Llama 3.3 | https://groq.com |
| **PostgreSQL** | Base de datos relacional | https://postgresql.org |
| **FastAPI** | Framework web Python | https://fastapi.tiangolo.com |
| **SQLAlchemy** | ORM (Object-Relational Mapping) | https://sqlalchemy.org |

## 🔐 Seguridad

- **Variables de entorno**: Claves API en `.env` (no versionado)
- **Validación Pydantic**: Rechaza datos mal formados antes de la BD
- **CORS** (opcional): Configurable en FastAPI
- **Autenticación**: Simple basada en cookies (`user_email`)

## 📈 Escalabilidad

- **Base de datos**: PostgreSQL soporta millones de registros
- **API**: FastAPI con uvicorn es muy rápido (ASGI)
- **Caché**: Soporta Redis (no implementado aún)
- **Búsqueda**: Tavily tiene plan de escalado

## 🚀 Mejoras Futuras

- [ ] Cache Redis para búsquedas frecuentes
- [ ] WebSockets para búsquedas en tiempo real
- [ ] Autenticación OAuth2 + JWT
- [ ] Sistema de notificaciones (carreras próximas)
- [ ] Integración con Google Calendar
- [ ] Dashboard administrativo
