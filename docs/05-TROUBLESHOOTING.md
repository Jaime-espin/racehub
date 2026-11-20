#  Troubleshooting y Solución de Problemas

##  Problemas Comunes

### 1. \"ERROR: TAVILY_API_KEY no está configurada\"

**Problema**: La aplicación no inicia porque falta la clave de API de Tavily.

**Soluciones**:

1. **Verifica que existe `.env`**:
   ```bash
   ls -la .env
   ```
   Si no existe:
   ```bash
   cp .env.example .env
   ```

2. **Edita `.env` y agrega tu clave**:
   ```bash
   nano .env  # o tu editor preferido
   ```
   ```env
   TAVILY_API_KEY=tu_clave_aqui
   GROQ_API_KEY=tu_otra_clave
   DATABASE_URL=postgresql://...
   ```

3. **Obtén una clave gratuita**:
   - Tavily: https://tavily.com
   - Groq: https://console.groq.com

4. **Reinicia la aplicación**:
   ```bash
   python src/main.py
   # o
   python -m uvicorn src.api:app --reload
   ```

---

### 2. \"psycopg2.OperationalError: connection to database failed\"

**Problema**: No puede conectarse a PostgreSQL.

**Soluciones**:

1. **Verifica que PostgreSQL está ejecutándose**:
   ```bash
   # Linux/Mac
   sudo systemctl status postgresql
   
   # Windows (Services)
   # O simplemente prueba:
   psql -U postgres -c \"SELECT 1\"
   ```

2. **Verifica `DATABASE_URL` en `.env`**:
   ```env
   DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/racehub
   
   # Ejemplo correcto:
   DATABASE_URL=postgresql://usuario:contrasena@localhost:5432/racehub
   ```

3. **Verifica que la BD existe**:
   ```bash
   psql -U usuario -d racehub -c \"\\dt\"
   ```
   
   Si da error, créala:
   ```bash
   psql -U postgres -c \"CREATE DATABASE racehub\"
   psql -U usuario -d racehub -f db/schema.sql
   ```

4. **Verifica credenciales**:
   ```bash
   # Intenta conectarte manualmente
   psql -U jaime -d racehub -h localhost
   ```

---

### 3. \"ModuleNotFoundError: No module named 'X'\"

**Problema**: Falta una librería Python.

**Soluciones**:

1. **¿Estás dentro del entorno virtual?**:
   ```bash
   # Deberías ver (venv) al inicio del prompt
   # Si no:
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate    # Windows
   ```

2. **Reinstala las dependencias**:
   ```bash
   pip install -r requirements-clean.txt
   ```

3. **Verifica que Python tiene acceso a la BD venv**:
   ```bash
   which python  # Debe mostrar ruta dentro de venv/
   ```

---

### 4. \"ConnectionRefusedError: [Errno 111] Connection refused\"

**Problema**: Groq o Tavily rechaza la conexión.

**Soluciones**:

1. **Verifica tu conexión a internet**:
   ```bash
   ping google.com
   ```

2. **Verifica que tus claves API son válidas**:
   - Groq: https://console.groq.com → Copia tu clave exacta
   - Tavily: https://tavily.com/dashboard → Copia tu clave exacta

3. **Verifica que las claves están en `.env` SIN espacios**:
   ```env
   #  MALO
   GROQ_API_KEY = tu_clave_aqui
   TAVILY_API_KEY= tu_clave
   
   #  CORRECTO
   GROQ_API_KEY=tu_clave_aqui
   TAVILY_API_KEY=tu_clave
   ```

4. **Prueba la conexión manualmente**:
   ```python
   from tavily import TavilyClient
   tavily = TavilyClient(api_key=\"your_key\")
   print(tavily.search(\"test\"))  # Si funciona, clave es válida
   ```

---

### 5. \"Rate Limit 429 - Groq está saturado\"

**Problema**: El servicio de IA está sobrecargado.

**Soluciones**:

1. **Espera unos minutos** y reinente.

2. **Reduce la frecuencia de búsquedas**:
   - No hagas más de 5-10 búsquedas por minuto
   - Groq tiene límites de uso gratuito

3. **Actualiza a plan de pago** (si usas mucho):
   - https://console.groq.com/settings/billing

4. **Implementa reintentos automáticos** (código avanzado):
   ```python
   import time
   for intento in range(3):
       try:
           resultado = buscar_y_extraer_datos(\"carrera\")
           break
       except ValueError as e:
           if \"429\" in str(e) and intento < 2:
               print(\"Esperando 30s antes de reintentar...\")
               time.sleep(30)
           else:
               raise
   ```

---

### 6. \"HTML Status Code 500 - Error al procesar con el LLM\"

**Problema**: Groq devolvió un error diferente a 429.

**Soluciones**:

1. **Revisa los logs en la terminal**:
   ```
    Error al procesar con el LLM: [mensaje específico del error]
   ```

2. **Posibles causas**:
   - Pydantic schema no validable (datos mal formados)
   - Prompt muy largo
   - Groq down (raro pero pasa)

3. **Intenta de nuevo** con datos diferentes.

4. **Abre un issue** si persiste: https://github.com/tu_usuario/racehub/issues

---

### 7. \"No found - Tavily no encontró resultados\"

**Problema**: La búsqueda en internet no devolvió resultados.

**Soluciones**:

1. **Verifica el nombre de la carrera**:
   - ¿Escribiste bien el nombre?
   - Intenta con el nombre oficial exacto

2. **Intenta con más detalles**:
   - \"Barcelona Marathon 2026\" → más específico
   - \"Marathon Barcelona\" → menos específico

3. **Verifica que la carrera existe**:
   - Búscala en Google
   - Verifica la fecha del año

4. **Para resultados**: Sube un PDF o CSV en lugar de buscar automáticamente

---

### 8. \"CSS/JavaScript no carga en el navegador\"

**Problema**: La página web funciona pero se ve sin estilos.

**Soluciones**:

1. **Limpia la caché del navegador**:
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete

2. **Verifica que los archivos existen**:
   ```bash
   ls -la static/
   ls -la templates/
   ```

3. **Revisa la consola del navegador** (F12):
   - ¿Hay errores de 404?
   - ¿Hay errores de CORS?

4. **Reinicia el servidor**:
   ```bash
   # Ctrl+C para detener
   python -m uvicorn src.api:app --reload
   ```

---

### 9. \"Error al extraer PDF/CSV\"

**Problema**: El archivo subido no se procesó correctamente.

**Soluciones**:

1. **Verifica el formato**:
   - PDF: Debe tener texto extraíble (no imagen escaneada)
   - CSV: Debe tener columnas con nombres

2. **Tamaño máximo**:
   - Archivos > 50MB pueden fallar
   - Intenta con un archivo más pequero

3. **Encoding (CSV)**:
   - El sistema intenta UTF-8, Latin-1, ISO-8859-1, CP1252
   - Si sigue fallando, convierte el CSV a UTF-8:
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 archivo.csv > archivo-utf8.csv
   ```

4. **Intenta búsqueda web**:
   - Si el archivo no funciona, busca en internet en lugar de subir

---

### 10. \"Usuario no encontrado\" en login

**Problema**: Aunque el email está configurado, no aparece.

**Soluciones**:

1. **Limpia las cookies del navegador**:
   - F12 → Application → Cookies → Elimina `user_email`

2. **Intenta incógnito/privado** en el navegador:
   - Chrome: Ctrl+Shift+N
   - Firefox: Ctrl+Shift+P

3. **Verifica BD**:
   ```bash
   psql -U jaime -d racehub -c \"SELECT * FROM users;\"
   ```

4. **Recrear usuario manualmente**:
   ```bash
   psql -U jaime -d racehub
   INSERT INTO users (nombre_completo, email) VALUES ('Jaime', 'jaime@example.com');
   ```

---

##  Debugging Avanzado

### Activar logs detallados

**En Python** (src/main.py o src/api.py):
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Luego en el código:
logger.debug(f\"Variable: {variable}\")
logger.info(f\"Paso completado\")
logger.warning(f\"Precaución\")
logger.error(f\"Error: {e}\")
```

### Revisar logs de PostgreSQL

```bash
# Linux/Mac
tail -f /var/log/postgresql/postgresql.log

# O dentro de psql:
psql -U jaime -d racehub -c \"SELECT now()\"
```

### Testear componentes aislados

**¿Funciona Tavily?**
```python
from tavily import TavilyClient
t = TavilyClient(api_key=\"tu_clave\")
print(t.search(\"test\"))
```

**¿Funciona Groq?**
```python
from langchain_groq import ChatGroq
llm = ChatGroq(model_name=\"llama-3.3-70b-versatile\", api_key=\"tu_clave\")
print(llm.invoke(\"Hola\"))
```

**¿Funciona PostgreSQL?**
```python
from src.database import engine
print(engine.execute(\"SELECT 1\").fetchall())
```

---

##  Obtener Ayuda

1. **Lee los logs**: Están en la terminal donde ejecutaste la app
2. **Revisa la documentación**: [docs/](./docs/)
3. **Busca en Google**: \"fastapi [tu error]\" + \"sqlalchemy\" + etc.
4. **Abre un issue**: https://github.com/tu_usuario/racehub/issues

---

**Última actualización**: 25 de Marzo 2026
