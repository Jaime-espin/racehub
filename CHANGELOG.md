#  Changelog - RaceHub

## [Unreleased] - 2026-03-25

###  Cambios Principales

#### Mejoras de Código
-  **Mejorado manejo de excepciones** en `src/main.py`
  - Reemplazado bare `except:` por excepciones específicas
  - Agregada encadenamiento de excepciones (`raise from`)
  - Mejor distinción entre ValidationError y otras excepciones

#### Documentación
-  **Reorganización completa de documentación**
  - Creada carpeta `/docs/` con estructura coherente
  - `01-SETUP.md` - Guía de instalación. paso a paso
  - `02-ARCHITECTURE.md` - Arquitectura del sistema
  - `03-USER-GUIDE.md` - Guía de usuario completa
  - `04-API-REFERENCE.md` - Endpoints REST documentados
  - `05-TROUBLESHOOTING.md` - Solución de problemas detallada
  - `README.md` actualizado como punto de entrada principal

-  **Archivamiento de documentación antigua**
  - Trasladados 14 archivos markdown a `/_archive/`
  - Creado `_archive/README.md` explicando el contenido
  - Consolidada información duplicada

#### Dependencias
-  **Creado `requirements-clean.txt`** (versión simplificada)
  - Solo dependencias directas (no transitivas)
  - Mejor mantenibilidad
  - Comentmarios sobre cada grupo de dependencias

#### Limpieza de Archivos
- Eliminados archivos temporales:
  - `leep 2`, `leep 3`
  - `cookies.txt`
  - `requirements-clean.txt` (redundante)
  
- Archivados en `/_archive/`:
  - `migrate_db.py` (funcionalidad incluida en `src/database.py`)
  - `migration.sql` (ya no necesario)
  - 14 archivos markdown de documentación histórica
  
- Carpeta `/borrador/` mantened para referencia futura

###  Mejoras Técnicas

#### src/main.py
```python
# Antes
except:
    raise ValueError("...")

# Después
except (ValueError, TypeError) as e:
    raise ValueError("...") from e
```

#### Manejo de Rate Limits
- Mejore detección de errores 429 (case-insensitive)
- Mejor mensajes de error al usuario
- Consistent con otros módulos

###  Estructura de Carpetas

```
antes:
├── README.md (5 secciones)
├── 14 * ARCHIVO.md (documentación dispersa)

después:
├── README.md (punto de entrada)
├── docs/
│   ├── 01-SETUP.md
│   ├── 02-ARCHITECTURE.md
│   ├── 03-USER-GUIDE.md
│   ├── 04-API-REFERENCE.md
│   └── 05-TROUBLESHOOTING.md
└── _archive/
    └── (14 archivos antiguos)
```

###  Cambios de Documentación

#### README.md
-  Quick Start (30 segundos)
-  Tabla de documentación con enlaces
-  Tech Stack claro
-  Ejemplos de uso (CLI y API)
-  Sección "Concepto Clave"
-  Información de licencia y soporte

#### 01-SETUP.md (Nuevo)
-  Requisitos previos
-  Setup PostgreSQL desde cero
-  Configuración de `.env`
-  Entorno virtual Python
-  Verificación paso a paso
-  Solución de problemas comunes

#### 02-ARCHITECTURE.md (Nuevo)
-  Diagrama ASCII de arquitectura
-  Estructura de carpetas detallada
-  Flujo de datos (búsqueda y resultados)
-  Modelo de datos (tablas SQL)
-  Componentes externos explicados
-  Roadmap de mejoras

#### 03-USER-GUIDE.md (Nuevo)
-  Casos de uso principales
-  Instrucciones paso a paso
-  Funcionalidades disponibles
-  Uso desde CLI
-  Consejos para mejores resultados
-  FAQ completo

#### 04-API-REFERENCE.md (Nuevo)
-  Todos los endpoints documentados
-  Request/Response ejemplos JSON
-  Parámetros y headers
-  Códigos HTTP
-  Ejemplos con curl y Python
-  Swagger UI y ReDoc

#### 05-TROUBLESHOOTING.md (Nuevo)
-  10 problemas comunes con soluciones
-  Debugging avanzado
-  Logs y cómo leerlos
-  Testing de componentes
-  Recursos para obtener ayuda

###  Beneficios

**Para Usuario**:
- Documentación clara y buscable
- Setup más fácil
- Troubleshooting autoservicio

**Para Desarrollo**:
- Código con mejor manejo de errores
- Mantenimiento simplificado
- Escalabilidad documentada

**Para Proyecto**:
- Repositorio más limpio
- Mejor onboarding para contribuidores
- Preparado para open-source

---

## [Unreleased] - 2026-04-28

###  Simplificación Integral del Proyecto y Frontend
-  **Frontend rediseñado y simplificado**: Reducción drástica de código y complejidad en HTML, CSS y JS sin perder ninguna funcionalidad.
-  **Diálogo de Resultados Unificado**: Se reemplazó el laberinto de 6 modales encadenados por un único diálogo intuitivo con pestañas limpias (Búsqueda Web, Subida de Archivo, Entrada Manual).
-  **Eliminación de estilos inline**: Se extrajeron todos los estilos en línea repetidos a un sistema de diseño CSS limpio, ligero y moderno (`styles.css`).
-  **JS depurado y optimizado**: `script.js` pasó de 1062 líneas complejas con inyecciones dinámicas de HTML y SVGs duplicados a un código modular, limpio y reactivo.
-  **Limpieza de archivos obsoletos**: Se archivaron borradores, código muerto (`busqueda_mejorada.py`), notas de versiones pasadas y hojas de estilo no importadas hacia `_archive/`.
-  **Backend depurado**: Eliminado código inalcanzable en `src/api.py` y unificado el esquema `ResultadoSchema` para evitar duplicaciones.

### Planificación de Calendario (Opción 3)
-  Estados de planificación por carrera: candidata, seleccionada, inscrita, descartada
-  Filtros en UI para navegar por estado
-  Etiqueta de colisión para carreras seleccionadas en la misma fecha
-  Endpoints para cambiar estado e inscribir carreras

###  Backend y Datos
-  Nuevas columnas en `carreras`: `estado_planificacion`, `fecha_inscripcion`
-  Migración automática para columnas faltantes
-  Respuesta de `/carreras` enriquecida con colisiones

###  Documentación
-  Guía de usuario actualizada con flujo de planificación
-  Referencia de API actualizada con endpoints de planificación

---

## [2.0] - 2026-03-15

###  Búsqueda de Resultados

-  Sistema realista de búsqueda de resultados
-  Soporte para portales conocidos (Sportmaniacs, ChronoEmpresa)
-  Búsqueda flexible por regex
-  Subida de archivos (PDF/CSV)
-  Puntuación de confianza en resultados

###  Cambios API

-  POST `/resultados/buscar` - Nueva
-  POST `/resultados/buscar-archivo` - Nueva  
-  Mejor manejo de errores 429

---

## [1.0] - 2026-02-01

###  Características Iniciales

-  Búsqueda de carreras con IA (Tavily + Groq)
-  Calendario visual (HTML/CSS/JS)
-  Base de datos PostgreSQL
-  API REST con FastAPI
-  Autenticación por email
-  Compartición de calendario

---

##  Referencias

- GitHub: `git log --oneline` para más detalles
- Issues: Reportar bugs en la sección de Issues  
- Diskusiones: Ideas en Discussions
