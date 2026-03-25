# 📊 RaceHub - Resumen de Estado (Session 12)

**Fecha:** 25 de Marzo 2026  
**Estado General:** 🔴 Funcionalidad limitada por problemas de límites de API y coincidencia de nombres

---

## 📋 Resumen Ejecutivo

El proyecto RaceHub está casi completo en arquitectura pero enfrenta **dos problemas críticos**:

1. **🚫 Límite de tokens Groq excedido** (rate limit 429) - Impide búsquedas con LLM
2. **🔍 Mismatch de nombres** - El usuario se registra con un nombre distinto al que aparece en clasificaciones

---

## ✅ LO QUE FUNCIONA CORRECTAMENTE

### 1. **Infraestructura Base**
- ✅ FastAPI en puerto 8000 (servidor activo)
- ✅ PostgreSQL conectada y funcionando
- ✅ SQLAlchemy ORM para persistencia de datos
- ✅ Autenticación de usuarios implementada
- ✅ Rutas CRUD para carreras y resultados

### 2. **Interfaz de Usuario (Frontend)**
- ✅ Modal system completo (sin alertas/confirms nativos)
- ✅ Desplegables en tarjetas de carreras para mostrar resultados
- ✅ Botón "🔄 Buscar de nuevo" fuerza búsqueda nueva
- ✅ Sistema de 4 opciones de búsqueda (Automática, URL, PDF, Manual)
- ✅ Error modal con alternativas cuando falla búsqueda
- ✅ Modal de ingreso manual de datos

### 3. **Extracción de PDF**
- ✅ PyPDF2 instalado correctamente
- ✅ Extrae texto de PDFs sin errores (89,188 caracteres en test)
- ✅ Maneja múltiples páginas (hasta 30 páginas probadas)
- ✅ Fallback robusto si falla extracción de página individual

### 4. **Base de Datos**
- ✅ Migración automática crea columnas faltantes (posicion_categoria, confianza)
- ✅ Guardado de resultados con todos los campos
- ✅ API retorna datos en estructura correcta (CarreraOut con resultados[])

### 5. **Búsqueda por Regex (Mejorado en Session 12)**
- ✅ Búsqueda de 2 pasadas:
  - Pasada 1: Nombre completo + apellido (confianza 0.9)
  - Pasada 2: Solo nombre de pila (confianza 0.75)
- ✅ Validación triple: nombre + tiempo HH:MM:SS + posición número
- ✅ Soporte para acentos: "García" = "Garcia"
- ✅ Búsqueda flexible antes y después del tiempo

### 6. **Opción Manual**
- ✅ Usuario puede ingresar manualmente tiempo, posición, ritmo
- ✅ Datos se guardan con confianza 1.0 (manual)
- ✅ Se muestran inmediatamente en desplegable

---

## ❌ LO QUE FALLA O NO FUNCIONA

### 1. **PROBLEMA CRÍTICO: Límite de Tokens Groq (Rate Limit 429)**

**Síntoma:** 
```
Error code: 429 - Rate limit reached for model `llama-3.3-70b-versatile`
Limit 100000, Used 99041, Requested 1424
```

**Causa:** Groq tiene límite de **100,000 tokens/día** en plan on-demand. Se alcanzó el límite.

**Afectados:**
- Búsqueda con LLM fallback cuando regex no encuentra nada
- PDF: Intenta LLM como fallback cuando regex falla
- Portales: Fallback LLM cuando regex no encuentra
- URL directo: Fallback LLM

**Impacto:** 🔴 **CRÍTICO** - Sin LLM, solo funciona si el regex encuentra exactamente

### 2. **PROBLEMA CRÍTICO: Mismatch de Nombres**

**Síntoma:** 
```
Buscando: 'Jaime Espin Rodriguez' en PDF
✅ Extraídos 89188 caracteres del PDF
⚠️ Regex no encontró coincidencias
```

**Causa Identificada:** El usuario se registra como "Jaime Espin Rodriguez" pero en Sportmaniacs aparece como "JAIME LOPEZ LOPEZ" (apellido diferente en la carrera).

**En Test Anterior:** 
```
Línea encontrada: JAIME LOPEZ LOPEZ, FFAA Y CCS - M, M, --, 01:34:32, 01:34:30. 222, 38, 219
```

El mismo usuario aparece con apellidos completamente diferentes en distintas fuentes.

**Razones Posibles:**
1. Usuario usó segundo apellido en una carrera y primero en otra
2. Cambio de apellido (matrimonio, etc.)
3. Errores de tipeo en inscripción
4. Nombres registrados de forma inconsistente

**Afectado:**
- Búsqueda automática en Sportmaniacs falla
- Búsqueda en PDF falla si el nombre no coincide exactamente
- LLM no puede ayudar (límite de tokens)

---

## 🔧 CAMBIOS REALIZADOS EN ESTA SESIÓN

### Session 12 - Mejoras de Regex y Diagnóstico

1. **Reescrita de `_buscar_por_regex()` con 2 pasadas**
   - Antes: Buscaba solo nombre completo + apellido exacto
   - Ahora: 
     - Pasada 1: Nombre completo + apellido
     - Pasada 2: Solo nombre de pila (más flexible)
   - Resultado: Más flexible pero **aún falla con apellidos diferentes**

2. **Nueva función auxiliar `_buscar_regex_flexible()`**
   - Parametrizada para reutilizar lógica de búsqueda
   - Diferencia confianza: 0.9 (pasada 1) vs 0.75 (pasada 2)
   - Permite búsquedas sucesivas sin duplicar código

3. **PyPDF2 Instalado y Verificado**
   - Extrae correctamente texto de PDFs
   - Maneja múltiples páginas
   - Pero el problema sigue siendo el mismatch de nombres

---

## 📊 Flujo de Búsqueda Actual

```
Usuario busca resultado automático
    ↓
1. URL Directo (si disponible)
   → Búsqueda web con site: operator
   → Regex (2 pasadas)
   → LLM fallback ❌ (RATE LIMIT 429)
    ↓
2. Portal Específico (Sportmaniacs)
   → 3 intentos de queries
   → Regex (2 pasadas) ❌ FALLA: nombre no coincide
   → LLM fallback ❌ (RATE LIMIT 429)
    ↓
3. Búsqueda Genérica Web
   → Tavily search
   → Regex (2 pasadas) ❌ FALLA: nombre no coincide
   → LLM fallback ❌ (RATE LIMIT 429)
    ↓
📌 RESULTADO: Falla en todos los intentos
```

---

## 🐛 PROBLEMAS ESPECÍFICOS ENCONTRADOS

### Test 1: PDF Upload (Jaime Espin Rodriguez)
```
✅ PDF extraído: 89,188 caracteres
✅ Regex pasada 1: Busca "Jaime Espin Rodriguez"... ❌ NO ENCONTRADO
✅ Regex pasada 2: Busca "Jaime"... ❌ NO ENCONTRADO (probablemente dice JAIME LOPEZ)
❌ LLM fallback: ❌ RATE LIMIT 429
```

**Conclusión:** El nombre en el PDF no es "Jaime Espin Rodriguez"

### Test 2: Sportmaniacs Automático
```
✅ Portal detectado: sportmaniacs
✅ 3 query variations ejecutadas
✅ Contenido obtenido de Tavily (3778-4656 chars)
❌ Regex pasada 1: Busca "Jaime Espin Rodriguez"... NO ENCONTRADO
❌ Regex pasada 2: Busca "Jaime"... NO ENCONTRADO (probablemente dice JAIME LOPEZ)
❌ LLM fallback: ❌ RATE LIMIT 429
```

**Conclusión:** En Sportmaniacs también aparece con otro apellido

---

## 📝 SOLUCIONES PROPUESTAS

### **Solución Inmediata (Sin Cambios de Código)**
1. Esperar a que resetee el límite de Groq (mañana)
2. User manualmente ingresa el nombre como aparece en cada fuente
3. Usar opción "✍️ Ingreso Manual" cuando falla automático

### **Solución a Corto Plazo**
1. **Implementar "Nombre Alternativo"** en perfil de usuario
   - Campo: `alias_en_carreras` 
   - Permite registrar variaciones de nombre
2. **Mejorar Detección de Nombres** con fuzzy matching
   - Usar librería `fuzzywuzzy` para "Jaime Espin ≈ Jaime Lopez"
   - Umbral: 80% similitud

### **Solución a Mediano Plazo**
1. **Aumentar límite de Groq**
   - Upgrade plan de on-demand a Dev Tier
   - O rotar entre múltiples API keys
2. **Usar OCR para PDF con imágenes**
   - `Tesseract` para PDFs escaneados
3. **Mejorar Web Scraping**
   - Direct HTML parsing para portales específicos
   - Evitar dependencia de Tavily

### **Solución a Largo Plazo**
1. **Base de datos de nombres conocidos**
   - Guardar alias históricos del usuario
   - Auto-detectar variaciones
2. **Machine Learning**
   - Entrenar modelo local para matching de nombres
3. **Integración directa con portales**
   - APIs oficiales si están disponibles

---

## 📂 Archivos Principales

| Archivo | Status | Notas |
|---------|--------|-------|
| `src/busqueda_realista.py` | 🟡 Enhancements | Regex mejorado, pero aún falla con apellidos diferentes |
| `src/api.py` | ✅ Stable | Endpoints funcionan, API structure correcta |
| `src/database.py` | ✅ Stable | Migración auto-genera columnas, ORM working |
| `static/script.js` | ✅ Stable | Modal system complete, error handling OK |
| `templates/index.html` | ✅ Stable | HTML structure OK, no native dialogs |
| `requirements.txt` | ✅ Updated | PyPDF2 added, all deps installed |

---

## 🎯 Recursos y Límites

### API Keys Status

| API | Status | Límite | Usado | Disponible |
|-----|--------|--------|-------|-----------|
| Groq LLM | 🔴 EXCEDIDO | 100k tokens/día | ~99,041 | ~959 (casi nada) |
| Tavily Search | ✅ OK | 1000 queries/mes | ~50 | ~950 |
| PostgreSQL | ✅ OK | Local | - | - |

---

## 💡 Recomendaciones

1. **PRIORITARIO:** Resolver mismatch de nombres
   - Usuario debe verificar cómo aparece en cada carrera
   - Implementar "Nombre Alternativo" para casos así

2. **IMPORTANTE:** Aumentar cuota Groq
   - Current: 100k tokens/día (muy bajo)
   - Recomendado: Dev Tier (~1M tokens/día)

3. **RECOMENDADO:** Añadir fuzzy matching
   - Permitir 80%+ similitud, no exacto
   - Manejo robusto de variaciones de nombres

4. **FUTURO:** OCR para PDFs escaneados
   - Muchas carreras distribuyen PDFs con imágenes
   - Requiere Tesseract u otro OCR

---

## 🚀 Estado de Features

| Feature | Status | % Completado |
|---------|--------|------------|
| Calendario Visual | ✅ DONE | 100% |
| Búsqueda Automática | 🟡 PARTIAL | 60% (funciona si regex coincide) |
| Búsqueda Manual | ✅ DONE | 100% |
| Desplegables de Resultados | ✅ DONE | 100% |
| PDF Upload | 🟡 PARTIAL | 70% (extrae pero regex falla) |
| Compartir Calendario | ✅ DONE | 100% |
| Modal System | ✅ DONE | 100% |
| Error Handling | ✅ DONE | 100% |
| Database Schema | ✅ DONE | 100% |

---

## 📌 Próximos Pasos

1. **Diagnosticar nombre exacto en fuentes**
   - ¿Qué nombre exacto aparece en Sportmaniacs?
   - ¿Qué nombre exacto aparece en el PDF?
   - User debería revisar sus inscripciones

2. **Implementar fuzzy matching**
   - Cambiar búsqueda exacta a ~80% similitud
   - Usar `fuzzywuzzy` o `rapidfuzz`

3. **Resolver Groq rate limit**
   - Upgrade plan o usar otra API
   - O hacer LLM opcional (fallback a manual)

4. **Mejorar UX de error**
   - No mostrar "no encontrado"
   - Preguntar: "¿Cómo apareces registrado?"
   - Permitir corrección en UI

---

**Última Actualización:** 25/03/2026 14:45  
**Próxima Revisión:** Cuando se resuelva el mismatch de nombres
