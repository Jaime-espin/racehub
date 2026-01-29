# RaceHub

RaceHub es una herramienta que automatiza la creación de un calendario deportivo personal. Utiliza Inteligencia Artificial para buscar carreras en internet, extraer su información oficial (fechas, distancias, ubicación) y organizarlas en una base de datos local visualizable vía web.

---

## Paso a Paso

### 1. Base de Datos (PostgreSQL)
Antes de nada, creamos el "recipiente" donde vivirán los datos. Usamos **PostgreSQL**.

* **Esquema:** Tablas relacionales para `carreras` (calendario).
* **Comando de creación:**
    ```bash
    psql -U jaime -d racehub -f db/schema.sql
    ```
    *(Verificamos las tablas con `\dt` en la consola de `psql`)*.

### 2. Entorno y Librerías
Preparamos un entorno virtual de Python para aislar las dependencias del proyecto.

```bash
python -m venv venv
source venv/bin/activate  # O venv\Scripts\activate en Windows
pip install fastapi sqlalchemy psycopg2-binary langchain-groq tavily-python python-dotenv pydantic python-dateutil jinja2 uvicorn
```

**Herramientas clave:**
* **SQLAlchemy:** ORM que permite a Python "hablar" con SQL usando objetos.
* **LangChain + Groq:** El "cerebro" que procesa el lenguaje natural.
* **Tavily:** Buscador optimizado para agentes de IA (sin ruido ni anuncios).
* **Pydantic:** Validador que obliga a la IA a entregar datos estructurados (JSON) y no texto libre.

### 3. El Motor de Ingesta (`src/main.py`)
Script principal que orquesta la búsqueda y guardado de datos.

* **Búsqueda Inteligente:** Usa Tavily para leer el contenido de webs oficiales de carreras.
* **Extracción Estructurada:** Usa un modelo LLM (Llama 3.3) para rellenar un esquema estricto:
    * Nombre, Deporte, Fecha (YYYY-MM-DD), Lugar, Distancias.
* **Human-in-the-loop:** Antes de guardar, el script muestra los datos al usuario y pide confirmación manual para evitar errores o "alucinaciones" de la IA.

### 4. Persistencia de Datos
Utilizamos **SQLAlchemy** para manejar la base de datos de forma segura:

* Se abre una **Sesión**.
* Se crea el objeto `CarreraDB`.
* Se realiza un **Commit** (guardado).
* **Control de duplicados:** El sistema impide guardar la misma carrera (mismo nombre y fecha) dos veces.

### 5. Visualización Web (`src/api.py`)
Para ver los datos, creamos una API con **FastAPI**:

* **Backend:** Expone los datos en formato JSON en `/carreras`.
* **Frontend:** Renderiza una plantilla HTML (`templates/index.html`) en la ruta raíz `/` para mostrar un calendario visual con estilos CSS modernos.
* **Documentación:** Genera automáticamente documentación Swagger en `/docs`.

---

## 🛠️ Cómo ejecutar el proyecto

1. **Configuración inicial:**
   
   Copia el archivo de ejemplo y configura tus claves:
   ```bash
   cp .env.example .env
   ```
   
   Edita `.env` con tus credenciales:
   ```env
   GROQ_API_KEY=tu_clave_aqui
   TAVILY_API_KEY=tu_clave_aqui
   DATABASE_URL=postgresql://usuario:password@localhost:5432/racehub
   ```

2. **Instalar dependencias:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Crear la base de datos:**
   ```bash
   psql -U jaime -d racehub -f db/schema.sql
   ```

4. **Añadir una carrera (CLI):**
   ```bash
   python src/main.py
   # Introduce el nombre de la carrera cuando se te solicite
   ```

5. **Iniciar el servidor web:**
   ```bash
   uvicorn src.api:app --reload
   ```
   Abre tu navegador en: http://127.0.0.1:8000

---

## 📝 Mejoras Recientes

- ✅ Refactorización de código duplicado
- ✅ Validación de variables de entorno
- ✅ Mejora en el manejo de errores
- ✅ Validaciones en el schema de datos
- ✅ .gitignore completo
- ✅ Documentación de configuración (.env.example)

Ver [MEJORAS.md](MEJORAS.md) para más detalles.