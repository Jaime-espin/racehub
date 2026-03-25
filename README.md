# 🏃 RaceHub - Tu Calendario Deportivo Personal

RaceHub es una herramienta que **automatiza la creación de un calendario deportivo personal**. Utiliza Inteligencia Artificial para:

- 🔍 **Buscar carreras** en internet automáticamente
- 📊 **Extraer información oficial** (fechas, distancias, ubicación)
- 💾 **Organizar en base de datos** local visualizable vía web
- 🎯 **Buscar tus resultados** en portales de eventos

---

## 🚀 Quick Start (30 segundos)

```bash
# 1. Clonar y entrar
git clone https://github.com/tu_usuario/racehub.git && cd racehub

# 2. Configurar
cp .env.example .env
# Edita .env con tus claves (Groq + Tavily - ambas gratis)

# 3. Instalar
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Base de datos
psql -U jaime -d racehub -f db/schema.sql

# 5. Ejecutar
python -m uvicorn src.api:app --reload
```

Abre: **http://127.0.0.1:8000**

---

## 📚 Documentación

| Documento | Descripción |
|-----------|----------|
| [01-SETUP.md](./docs/01-SETUP.md) | 🔧 Instalación paso a paso |
| [02-ARCHITECTURE.md](./docs/02-ARCHITECTURE.md) | 🏗️ Cómo funciona internamente |
| [03-USER-GUIDE.md](./docs/03-USER-GUIDE.md) | 👤 Cómo usar la aplicación |
| [04-API-REFERENCE.md](./docs/04-API-REFERENCE.md) | 📡 Endpoints REST detallados |
| [05-TROUBLESHOOTING.md](./docs/05-TROUBLESHOOTING.md) | 🔧 Resolver problemas |

---

## 🎯 Características

### ✅ Implementadas

- 📅 **Calendario visual** de carreras
- 🤖 **IA para buscar carreras** (Tavily + Groq Llama 3.3)
- 🔐 **Autenticación por email** (cookies)
- 📤 **Búsqueda de resultados** en portales conocidos
- 📎 **Subida de archivos** (PDF/CSV con resultados)
- 🌐 **Calendario compartible** (link público)
- 🗄️ **Base de datos** PostgreSQL local

### 🔜 Roadmap

- [ ] Edición de carreras desde UI
- [ ] Notificaciones de aperturas de inscripción
- [ ] Integración con Google Calendar
- [ ] Estadísticas personales (tiempos, VO₂max, etc.)
- [ ] Desafíos/retos entre amigos
- [ ] Caché Redis para búsquedas rápidas
- [ ] Autenticación OAuth2 + JWT

---

## 🛠️ Tech Stack

| Capa | Tecnología |
|------|-----------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | FastAPI (Python) |
| **BD** | PostgreSQL + SQLAlchemy ORM |
| **IA** | Groq (LLM Llama 3.3) + Tavily (búsqueda) |
| **Deploy** | Procfile para Heroku (opcional) |

---

## 📦 Estructura

```
racehub/
├── src/               # Código Python
│   ├── main.py       # Núcleo: búsqueda + guardado
│   ├── api.py        # API REST con FastAPI
│   ├── database.py    # Modelos ORM
│   └── busqueda_*.py  # Búsqueda avanzada
├── templates/        # HTML (Jinja2)
├── static/           # CSS + JavaScript
├── db/               # Esquema SQL
├── docs/             # Documentación
└── requirements-clean.txt  # Dependencias (simplificado)
```

---

## 🔐 Variables de Entorno Requeridas

```env
# API Keys (gratis en sus sitios web)
GROQ_API_KEY=xxx          # https://console.groq.com
TAVILY_API_KEY=xxx        # https://tavily.com

# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/racehub
```

---

## 💡 Ejemplos de Uso

### CLI - Buscar una carrera

```bash
python src/main.py
# Escribe: "Barcelona Marathon 2026"
# La IA busca la información oficial
# Confirmas si está correcta
# ¡Se guarda en tu calendario!
```

### Web API - Buscar resultado

```bash
curl -X POST http://127.0.0.1:8000/resultados/buscar \
  -H \"Content-Type: application/json\" \
  -d '{
    \"nombre_carrera\": \"Barcelona Marathon 2026\",
    \"anio\": 2026,
    \"nombre_corredor\": \"Jaime Espín\"
  }' \
  -b cookies.txt
```

---

## 🎓 Conceptos Clave

### Búsqueda Inteligente
- **Tavily API**: Motor de búsqueda optimizado para IA (evita ruido)
- **Groq LLM**: Extrae datos estructurados (no texto libre)
- **Pydantic**: Valida que la IA responda en formato JSON correcto

### Resultados
- **Estrategia múltiple**: Portales conocidos → Web → Subida manual
- **Regex flexible**: Detecta nombres con variaciones (acentos, orden, etc.)
- **Puntuación de confianza**: 0.9 (alta) = regex, 0.65 (baja) = LLM

### Base de Datos
- **SQLAlchemy ORM**: Python habla con PostgreSQL como objetos
- **Control de duplicados**: Impide guarrar la misma carrera 2 veces
- **Relaciones**: Usuarios → Carreras → Resultados

---

## 🤝 Contribuir

Este es un proyecto personal pero las contribuciones son bienvenidas:

1. **Fork** el repo
2. **Crea rama**: `git checkout -b feature/mi-feature`
3. **Commit**: `git commit -am \"Agrego feature\"`
4. **Push**: `git push origin feature/mi-feature`
5. **PR**: Abre un Pull Request

---

## ✨ Credits

**Creado por**: Jaime Espín Rodríguez
**Última actualización**: 25 de Marzo 2026  
**Versión**: 2.0 (con búsqueda de resultados)

---

## 🐛 Encontraste un Bug?

1. 🔍 **Revisa [TROUBLESHOOTING.md](./docs/05-TROUBLESHOOTING.md)**
2. 📝 **Abre un issue** con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs/errores
3. 💬 **O contacta** directamente

---

## 📞 Soporte

- 📖 **Documentación**: [./docs/](./docs/)
- 🐛 **Issues**: https://github.com/tu_usuario/racehub/issues
- 📧 **Email**: tu_email@example.com

---

**Hecho con ❤️ para runners, ciclistas y triatletas** 🏃‍♂️🚴‍♀️🏊‍♂️
