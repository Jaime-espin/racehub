# 🚀 GUÍA RÁPIDA DE REFERENCIA

## ¿Qué cambió?

### 1. Nuevo archivo: `src/busqueda_mejorada.py` ✨
- **Función principal:** `buscar_resultado_usuario_v2()`
- **Mejora:** Busca en URLs alternativas + múltiples queries
- **Uso:** Reemplaza la función antigua en el endpoint de búsqueda

### 2. Modificaciones en `src/api.py`
```python
# Línea 12 - Agregar import:
from src.busqueda_mejorada import buscar_resultado_usuario_v2

# Línea 43 - Actualizar modelo:
class SolicitudResultado(BaseModel):
    # ... (campos existentes)
    url_oficial: Optional[str] = None  # ← NUEVO

# Línea 158 - Cambiar función:
# ANTES: buscar_resultado_usuario(...)
# AHORA: buscar_resultado_usuario_v2(..., url_oficial=solicitud.url_oficial)
```

### 3. Mejoras en `static/script.js`
- Función `gestionResultado()` ahora pregunta por URL
- Mejor feedback: "Buscando en múltiples fuentes..."
- Ofrece pegar URL si no existe URL oficial

---

## 🎯 Cómo Probar

### Opción A: Interfaz Web
1. Abre http://localhost:8000
2. Agrega una carrera con URL oficial
3. Click en "🏅 Ver Resultado"
4. Elige usar URL oficial o proporciona otra
5. Sistema busca automáticamente en URLs alternativas

### Opción B: API directa
```bash
curl -X POST http://localhost:8000/resultados/buscar \
  -H "Content-Type: application/json" \
  -b "user_email=tu@email.com" \
  -d '{
    "nombre_carrera": "Maratón de...",
    "anio": 2024,
    "nombre_corredor": "Tu Nombre",
    "url_oficial": "https://ejemplo.com/resultados"
  }'
```

---

## 🔍 ¿Cómo Funciona Internamente?

```
1. Usuario hace búsqueda
   ↓
2. Backend recibe solicitud con:
   - nombre_carrera
   - anio
   - nombre_corredor
   - url_oficial (NUEVO)
   ↓
3. buscar_resultado_usuario_v2() ejecuta:
   
   PASO A - Si hay URL oficial:
   - Intenta ejemplo.com/resultados/
   - Intenta ejemplo.com/clasificación/
   - Intenta ejemplo.com/standings/
   - etc (5-6 URLs comunes)
   
   PASO B - Búsquedas en Tavily (en cascada):
   - Query 1: "{carrera} {año} clasificación {nombre}"
   - Query 2: "{carrera} {año} resultados {nombre} tiempo"
   - Query 3: "{carrera} '{año}' {nombre} posición"
   - Query 4: "{carrera.split()[0]} {año} results {nombre}"
   - Query 5: fallback general
   
   PASO C - Extracción con IA:
   - Groq analiza contexto encontrado
   - Extrae: tiempo, posición, categoría, ritmo
   - Si no seguro → devuelve NULL
   
4. Resultado se muestra al usuario
   ↓
5. Se guarda en base de datos
```

---

## ✅ Verificación Rápida

### ¿Está implementado correctamente?

```python
# En python:
from src.busqueda_mejorada import buscar_resultado_usuario_v2

# Debería existir esta función
print(buscar_resultado_usuario_v2.__doc__)
```

```python
# En src/api.py debería existir:
from src.busqueda_mejorada import buscar_resultado_usuario_v2

class SolicitudResultado(BaseModel):
    url_oficial: Optional[str] = None  # ← Esta línea
```

---

## 📊 Changelog

```diff
src/api.py:
+ from src.busqueda_mejorada import buscar_resultado_usuario_v2
+ url_oficial: Optional[str] = None
+ url_oficial=solicitud.url_oficial

src/busqueda_mejorada.py:
+ NUEVO ARCHIVO (260 líneas)
+ buscar_resultado_usuario_v2()
+ generar_urls_alternativas()
+ buscar_resultado_en_archivo()

static/script.js:
+ Pregunta por URL en gestionResultado()
+ Mejor feedback visual
+ Soporta url_oficial en request

DOCS:
+ DIAGNOSTICO_BUSQUEDA.md
+ PLAN_IMPLEMENTACION.md
+ RESUMEN_SOLUCION.md
+ REFERENCIA_RAPIDA.md (este)
```

---

## 🆘 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'busqueda_mejorada'"
→ Asegúrate que `src/busqueda_mejorada.py` existe y Python puede encontrarlo

### ❌ "No se encuentran resultados"
→ Es normal cuando:
  - La carrera es muy nueva
  - Los resultados están en PDF protegido
  - El nombre del corredor varía mucho
→ Solución: Proporciona URL oficial en la búsqueda

### ❌ "Error 429 de Groq"
→ Límite de API excedido
→ Espera unos minutos e intenta de nuevo

### ✅ "¡Resultado encontrado!"
→ La mejora funcionó correctamente

---

## 🎓 Notas Importantes

1. **Las URLs alternativas se generan automáticamente**
   - No necesitas configurar nada
   - Sistema intenta dominio.com/resultados/, /clasificación/, etc.

2. **URL oficial es opcional**
   - Si la proporcionas → mejor precisión
   - Si no → funciona normal (búsqueda web)

3. **El LLM es riguroso**
   - Devuelve NULL si no está seguro
   - Es mejor eso que datos falsos

4. **Funciona con variantes de nombre**
   - "Jaime Espín" = "Espin Jaime" = "Rodríguez, Jaime"
   - El sistema es flexible

5. **Próximamente**
   - Soporte para subir PDF directamente
   - Caché para no repetir búsquedas

---

## 📧 Próximos Pasos

1. **Prueba con carreras reales**
   - Casos que fallaban antes
   - Casos nuevos

2. **Reporta resultados**
   - ¿Qué porcentaje de éxito ahora?
   - ¿Qué carreras siguen fallando?

3. **Optimiza**
   - Agrega URLs alternativas específicas por deporte
   - Ajusta prompts según experiencia

---

**Status Actual:** ✅ Implementado y listo para probar

**Último update:** 25 de Marzo 2026
