# RaceHub - Calendario Deportivo Personal

RaceHub es una plataforma disenada para automatizar la planificacion, gestion y seguimiento de un calendario deportivo personal (running, trail, ciclismo, gravel y triatlon).

---

## Integracion de Inteligencia Artificial en el Frontend

El frontend de RaceHub se comunica de forma directa con los motores de Inteligencia Artificial (Groq mediante modelos Llama y Tavily Search) para automatizar tareas complejas desde la interfaz de usuario:

1. **Alta asistida por IA en tiempo real**:
   - El usuario introduce unicamente el nombre o referencia de la carrera en el buscador web (por ejemplo, "Maraton de Valencia 2025" o "Behobia San Sebastian").
   - El frontend orquesta la peticion hacia el servicio de IA, que investiga las fuentes oficiales en internet y devuelve los datos maestros estructurados: nombre oficial, deporte, fecha de la proxima edicion, distancias homologadas, localizacion, enlace web oficial y estado de la inscripcion.
   - La interfaz muestra una tarjeta de previsualizacion interactiva para que el corredor valide los datos extraidos por la IA antes de confirmarlos en base de datos.

2. **Rastreo y extraccion de marcas y clasificaciones con IA**:
   - En pruebas finalizadas, el frontend ofrece un dialogo unificado con soporte para tres vias de obtencion de marca:
     - **Busqueda automatica en la red**: la IA rastrea plataformas de cronometraje y clasificaciones oficiales buscando el nombre y apellidos del corredor.
     - **Procesamiento de documentos**: el usuario puede arrastrar o seleccionar un archivo PDF, CSV o Excel oficial de clasificaciones; el frontend remite el documento al motor de analisis para localizar tiempos oficiales, ritmo medio y posicion absoluta y por categoria.
     - **Entrada manual**: formulario directo de soporte en caso de que no existan listados digitales.

3. **Planificacion y deteccion de colisiones en el cliente**:
   - Filtros rapidos por ciclo de decision: *Candidatas*, *Seleccionadas*, *Inscritas* y *Descartadas*.
   - El frontend evalua en tiempo real las fechas de las pruebas seleccionadas e inscritas para alertar visualmente sobre colisiones de calendario cuando dos competiciones coinciden el mismo dia.

---

## Inicio Rapido

### Requisitos previos
- Python 3.10 o superior
- PostgreSQL activo
- Clave de API de Groq (gratuita en console.groq.com)
- Clave de API de Tavily (gratuita en tavily.com)

### Pasos de instalacion

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu_usuario/racehub.git && cd racehub

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus claves de Groq, Tavily y la URL de PostgreSQL

# 3. Entorno virtual e instalacion de dependencias
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Inicializar base de datos
psql -U usuario -d racehub -f db/schema.sql

# 5. Iniciar la aplicacion
python -m uvicorn src.api:app --reload
```

Abre en tu navegador: **http://127.0.0.1:8000**

---

## Documentacion

| Documento | Descripcion |
|---|---|
| [01-SETUP.md](./docs/01-SETUP.md) | Guia de instalacion y configuracion del entorno |
| [02-ARCHITECTURE.md](./docs/02-ARCHITECTURE.md) | Arquitectura del sistema, capas y flujo de datos |
| [03-USER-GUIDE.md](./docs/03-USER-GUIDE.md) | Manual de uso de la aplicacion y planificacion |
| [04-API-REFERENCE.md](./docs/04-API-REFERENCE.md) | Especificacion completa de endpoints REST |
| [05-TROUBLESHOOTING.md](./docs/05-TROUBLESHOOTING.md) | Resolucion de incidencias y preguntas frecuentes |

---

## Caracteristicas Principales

- **Frontend reactivo con IA**: busqueda automatizada de carreras y extraccion de marcas en clasificaciones.
- **Doble visualizacion**: alternancia entre vista de Tabla interactiva (con filas de resultados desplegables) y Calendario mensual organizado.
- **Sistema de planificacion**: ciclo de vida de la carrera (candidata, seleccionada, inscrita, descartada) con alertas de colision de fechas.
- **Autenticacion ligera**: gestion de sesion por email mediante cookies seguras.
- **Calendario publico**: generacion de enlace unico (`/share/{token}`) para compartir el calendario en modo solo lectura.
- **Persistencia robusta**: PostgreSQL con modelos ORM de SQLAlchemy y migraciones automaticas de esquema.

---

## Stack Tecnologico

| Capa | Tecnologia |
|---|---|
| Frontend | HTML5, CSS3 (variables nativas), Vanilla JavaScript integrado con endpoints de IA |
| Backend | FastAPI (Python) con Pydantic para validacion estricta |
| Base de Datos | PostgreSQL + SQLAlchemy ORM |
| Inteligencia Artificial | Groq (Llama 3.3 70B Versatile) + Tavily Search API |
| Procesamiento de Documentos | PyPDF2 y parsers CSV |

---

## Estructura del Proyecto

```
racehub/
├── src/
│   ├── main.py              # Logica principal de extraccion con IA y guardado
│   ├── api.py               # Endpoints REST de FastAPI y autenticacion
│   ├── database.py          # Modelos ORM, conexion SQLAlchemy y migraciones
│   └── busqueda_realista.py # Busqueda especializada de resultados y lectura de archivos
├── templates/
│   ├── index.html           # Interfaz principal de usuario
│   └── public.html          # Vista publica compartida
├── static/
│   ├── styles.css           # Sistema de diseno y estilos unificados
│   └── script.js            # Logica del frontend y comunicacion con la API
├── db/
│   └── schema.sql           # Esquema relacional de PostgreSQL
├── docs/                    # Documentacion tecnica detallada
├── requirements.txt         # Dependencias de Python del proyecto
├── .env.example             # Plantilla de variables de configuracion
└── Procfile                 # Archivo de despliegue para plataformas cloud
```

---

## Variables de Entorno

```env
# Claves de acceso a servicios de Inteligencia Artificial
GROQ_API_KEY=tu_clave_de_groq
TAVILY_API_KEY=tu_clave_de_tavily

# Conexion a base de datos
DATABASE_URL=postgresql://usuario:contrasena@localhost:5432/racehub
```

---

## Contribuir

1. Crea una bifurcacion (fork) del proyecto.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios y documentalos con commits claros.
4. Envia tu rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request describiendo las modificaciones realizadas.

---

## Licencia y Creditos

Desarrollado por Jaime Espin Rodriguez. Proyecto enfocado en simplificar y automatizar la organizacion deportiva mediante Inteligencia Artificial.

