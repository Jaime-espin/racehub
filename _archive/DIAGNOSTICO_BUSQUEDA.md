# 📋 Diagnóstico: Sistema de Búsqueda de Clasificaciones

## 🔍 Cómo funciona actualmente:

### Flujo actual (en `src/main.py` línea 223):
```
1. BÚSQUEDA INICIAL
   - Query: "{carrera} {año} clasificación {nombre}"
   - Motor: Tavily (search_depth="advanced", max_results=10)
   - Objetivo: Encontrar listados web directamente indexados

2. BÚSQUEDA DE FALLBACK
   - Si la búsqueda #1 falla, intenta: "{carrera} {año} resultados pdf completo"
   - Mismo motor: Tavily (intenta encontrar PDFs)
   - max_results=5

3. EXTRACCIÓN CON IA
   - Motor: LLM Groq (llama-3.3-70b)
   - Tarea: Extraer tiempo, posición y ritmo del contexto de búsqueda
   - Problema: Solo analiza el contenido que Tavily pudo indexar
```

## ❌ Problemas identificados:

### 1. **Limitación de Tavily:**
   - ❌ No puede descargar PDFs directamente
   - ❌ No puede ejecutar JavaScript (webs dinámicas)
   - ❌ No puede acceder a portales privados
   - ✅ Solo indexa contenido HTML público disponible

### 2. **Portales donde están los resultados:**
   - `/resultados/` en el dominio oficial (no siempre linkado desde el buscador)
   - PDFs en servidores de descargas
   - Páginas dinámicas (requieren JavaScript)
   - Portales de timing (Mylaps, ChipTiming, etc.) con búsqueda interna

### 3. **Formato de datos variados:**
   - CSV en PDFs
   - Tablas HTML dinámicas
   - XML de timing
   - Formatos propietarios

## ✅ Soluciones propuestas:

### Opción 1: Búsqueda multi-fuente (Recomendado)
Modificar `buscar_resultado_usuario()` para:
```python
# 1. Buscar en URLs específicas conocidas
# 2. Intentar URLs alternativas automáticamente
# 3. Buscar archivos en espacios de descargas públicas
# 4. Parsear formatos comunes (CSV, PDF, XML)
```

### Opción 2: Integración con buscadores específicos
- `runner.es` (Running)
- `cronometrage.net` (Trail)
- Portales nacionales por deporte

### Opción 3: Rasgueo inteligente
- Detectar el dominio de la carrera
- Buscar automáticamente rutas comunes:
  - `/resultados/`
  - `/clasificación/`
  - `/standings/`
  - `/scores/`

### Opción 4: Combinar con buscador local
Si el usuario proporciona un PDF o URL, procesarlo localmente con:
- PyPDF2 (leer PDFs)
- Beautiful Soup (parsear HTML)
- Selenium (cargar páginas dinámicas)

## 📊 Comparativa de soluciones:

| Solución | Esfuerzo | Cobertura | Velocidad | Confiabilidad |
|----------|----------|-----------|-----------|---------------|
| Multi-fuente | Medio | 70% | Rápida | Media |
| Buscadores específicos | Alto | 85% | Media | Alta |
| Rasgueo inteligente | Medio | 60% | Lenta | Media |
| Procesamiento local | Bajo | 95% | Muy rápida | Alta |
| **Híbrido** | **Alto** | **95%** | **Rápida** | **Muy Alta** |

## 🎯 Recomendación:

**Implementar enfoque HÍBRIDO:**
1. Mantener Tavily para búsqueda rápida
2. Agregar rasgueo inteligente de URLs comunes
3. Permitir al usuario subir PDF o URL directo
4. Procesamiento local de esos archivos
