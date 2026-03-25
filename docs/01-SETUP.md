# 🚀 Setup e Instalación de RaceHub

## Requisitos Previos

- **Python 3.9+**
- **PostgreSQL 12+** instalado y ejecutándose
- **Git** (opcional, para clonar el repositorio)

## Paso 1: Configuración de Base de Datos

### Crear una base de datos PostgreSQL

```bash
# Conectarse a PostgreSQL
psql -U postgres

# Dentro de psql, crear la base de datos
CREATE DATABASE racehub;
CREATE USER jaime WITH PASSWORD '6999';
ALTER ROLE jaime SET client_encoding TO 'utf8';
ALTER ROLE jaime SET default_transaction_isolation TO 'read committed';
ALTER ROLE jaime SET default_transaction_deferrable TO on;
ALTER ROLE jaime SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE racehub TO jaime;
\q
```

### Cargar el esquema

```bash
psql -U jaime -d racehub -f db/schema.sql
```

Verifica las tablas creadas:
```bash
psql -U jaime -d racehub -c "\dt"
```

## Paso 2: Configurar Variables de Entorno

### Crear archivo `.env`

```bash
cp .env.example .env
```

### Editar `.env` con tus claves

```env
# API Keys (obtén éstas gratis en sus sitios web)
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Database
DATABASE_URL=postgresql://jaime:6999@localhost:5432/racehub
```

> **Obtener API Keys:**
> - **Groq**: https://console.groq.com (gratuito)
> - **Tavily**: https://tavily.com (gratuito para investigación)

## Paso 3: Entorno Virtual Python

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Linux/Mac)
source venv/bin/activate

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements-clean.txt
```

## Paso 4: Ejecutar la Aplicación

### Opción A: CLI (línea de comandos)

```bash
python src/main.py
```

Introduce el nombre de una carrera cuando se te pida.

### Opción B: Interfaz Web

```bash
python -m uvicorn src.api:app --reload
```

Abre tu navegador en: **http://127.0.0.1:8000**

La API Swagger estará disponible en: **http://127.0.0.1:8000/docs**

## Verificación

✅ Base de datos conectada
```bash
psql -U jaime -d racehub -c "SELECT COUNT(*) FROM carreras;"
```

✅ Dependencias instaladas
```bash
pip list | grep -E "fastapi|sqlalchemy|langchain|groq|tavily"
```

✅ Aplicación funcionando
```bash
curl http://127.0.0.1:8000/
```

## Solución de Problemas

### Error: "TAVILY_API_KEY no está configurada"
→ Asegúrate de que el archivo `.env` existe y tiene la variable correcta.

### Error: "connection to database failed"
→ Verifica que PostgreSQL esté ejecutándose: `psql -U postgres -c "SELECT 1"`

### Error: "Module not found"
→ Estás dentro del entorno virtual activado? Ejecuta `source venv/bin/activate`

Para más ayuda, ver [TROUBLESHOOTING.md](./05-TROUBLESHOOTING.md)
