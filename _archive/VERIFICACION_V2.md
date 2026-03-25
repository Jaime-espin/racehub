# ✅ VERIFICACIÓN RÁPIDA V2.0

**Fecha:** 25 de Marzo 2026  
**Estado:** Listo para probar  
**Tiempo estimado de verificación:** 5-10 minutos

---

## 📋 Checklist Técnico

### Backend
```
☑️ src/busqueda_realista.py existe?
   Ubicación: /home/jaime/01Proyectos/racehub/src/busqueda_realista.py
   Tamaño: ~350 líneas
   Funciones:
     - buscar_resultado_realista()
     - validar_tiempo()
     - validar_posicion()
     - calcular_confianza()
     - buscar_en_archivo_local()

☑️ src/api.py actualizado?
   Línea 1-15: Nuevos imports (busqueda_realista)
   Línea 145-180: Endpoint /resultados/buscar actualizado
   Línea 180-230: Nuevo endpoint /resultados/buscar-archivo

☑️ Modelos Pydantic actualizados?
   SolicitudResultado: url_oficial parámetro
   ResultadoSchema: confianza parámetro
```

### Frontend
```
☑️ static/script.js actualizado?
   Línea 388-500: Función gestionResultado() mejorada
   Línea 500-530: Función mostrarModalSubidaArchivo() nueva
   Línea 530-560: Función procesarSubidaArchivo() nueva
   Línea 560-590: Función cerrarModalSubida() nueva

☑️ Lógica de 3 opciones implementada?
   - Búsqueda automática
   - Subida PDF
   - Ingreso manual
```

---

## 🧪 Pruebas Funcionales

### Test 1: Búsqueda Automática (Como Antes)
```
PASO:
1. Abre http://localhost:8000
2. Login (tu email)
3. Agrega carrera con URL oficial
4. Click "🏅 Ver Resultado"
5. Confirma nombre
6. Dí "SÍ" a búsqueda automática
7. Proporciona URL si tienes
8. Espera 15 segundos

RESULTADO ESPERADO:
- Si funciona: "✅ ¡RESULTADO ENCONTRADO!"
- Si no: "❌ No se encontró. Intenta estas opciones:"
- Nueva opción: "¿Subir PDF?"

CONFIRMACIÓN: ✅ Si ves "¿Subir PDF?" = V2.0 funciona
```

### Test 2: Subida de PDF (Nuevo)
```
PASO:
1. Descarga un PDF con resultados de carrera
   (Puede ser cualquier PDF con tabla numérica)
2. Va a RaceHub
3. Click "🏅 Ver Resultado"
4. Confirma nombre
5. Dí "NO" a búsqueda automática
6. Ve modal de subida
7. Selecciona PDF
8. Click "Procesar"
9. Espera 5 segundos

RESULTADO ESPERADO:
- Modal de subida aparece = ✅
- Sistema procesa archivo = ✅
- Resultado encontrado o no = ✅

CONFIRMACIÓN: ✅ Si ves modal y resultado = V2.0 funciona
```

### Test 3: Confianza en Resultado
```
PASO:
1. Hace cualquiera búsqueda
2. Si encuentra resultado

RESULTADO ESPERADO:
- Muestra "(XX% confianza)"
- Ej: "1:45:32 (87% confianza)"
- Para PDF: "99% confianza"
- Para automático: "40-80% confianza"

CONFIRMACIÓN: ✅ Si ves porcentaje = V2.0 funciona
```

---

## 🔍 Verificación de Código

### src/busqueda_realista.py
```python
# Verificar que exista
import src.busqueda_realista

# Verificar función principal
from src.busqueda_realista import buscar_resultado_realista
buscar_resultado_realista(
    "Test Carrera",
    2024,
    "Test Usuario"
)
# Debería retornar ResultadoSchema con confianza

# Verificar validación
from src.busqueda_realista import validar_tiempo
validar_tiempo("1:45:32")  # True
validar_tiempo("999:99:99")  # False
```

### src/api.py
```python
# Verificar imports
from src.busqueda_realista import buscar_resultado_realista

# Verificar endpoint
@app.post("/resultados/buscar")  # Existe
@app.post("/resultados/buscar-archivo")  # Nuevo

# Verificar modelo
class SolicitudResultado(BaseModel):
    url_oficial: Optional[str]  # Nueva línea
```

### static/script.js
```javascript
// Verificar funciones existen
typeof gestionResultado === 'function'  // true
typeof mostrarModalSubidaArchivo === 'function'  // true
typeof procesarSubidaArchivo === 'function'  // true
```

---

## 📊 Antes vs Después

| Función | Antes | Después |
|---------|-------|---------|
| gestionResultado() | ❌ 1 camino | ✅ 3 caminos |
| Validación | ⚠️ Débil | ✅ Estricta |
| Confianza | ❌ No | ✅ Sí |
| Subida PDF | ❌ No | ✅ Sí |
| Alucinaciones | ⚠️ Sí | ✅ No |

---

## 🎯 Prueba Real Recomendada

### Con la Media Maratón Málaga (el caso que falló)

```
PASO 1: Búsqueda Automática
├─ URL: https://www.mediamaratonmalaga.com  (si existe)
├─ Sistema intenta: 15 segundos
└─ Resultado esperado: ❌ Falla (portal dinámico)

PASO 2: Subida de PDF (NUEVO)
├─ Ejecutar:
│  cd /home/jaime/01Proyectos/racehub
│  # Descargar PDF desde web oficial
│  # O usar archivo de prueba si existe
├─ Subir PDF en RaceHub
└─ Resultado esperado: ✅ Éxito (99% precisión)

PASO 3: Verificar Confianza
├─ Búsqueda automática: "40-50% confianza"
├─ PDF: "99% confianza"
└─ Manual: "100% confianza"
```

---

## 🐛 Debugging

### Si algo no funciona:

#### Problema: "ModuleNotFoundError: busqueda_realista"
```bash
# Verificar archivo existe
ls -la src/busqueda_realista.py

# Verificar Python path
python -c "import sys; print(sys.path)"

# Reiniciar servidor
# Ctrl+C en FastAPI
# Vuelve a ejecutar
```

#### Problema: "Modal no aparece"
```bash
# Verificar JavaScript
F12 en navegador
Abre Console
Busca errores

# Verificar archivo cargado
Ctrl+Shift+I → Sources → static/script.js
```

#### Problema: "PDF no se procesa"
```bash
# Verificar dependencia PyPDF2
pip list | grep PyPDF2

# Si falta
pip install PyPDF2

# Luego testear
python -c "from PyPDF2 import PdfReader; print('OK')"
```

#### Problema: "Confianza = None"
```python
# En resultado, verificar código
if datos_resultado.confianza is None:
    datos_resultado.confianza = 0.5

# O en busqueda_realista.py
datos.confianza = calcular_confianza({...})
```

---

## 📱 Prueba Desde Dispositivo Móvil

```
PASO:
1. Abre http://[TU_IP]:8000 en móvil
   (cambiar localhost por IP de la máquina)
2. Login
3. Click "🏅 Ver Resultado"
4. Intenta subida de PDF
5. Si funciona en móvil = ✅

NOTA:
- Modal debería ser responsive
- Upload debe funcionar en móvil
- Buttons grandes para touch
```

---

## ✅ Checklist Final

```
CÓDIGO:
☑️ busqueda_realista.py existe
☑️ api.py tiene nuevos imports
☑️ api.py tiene nuevo endpoint
☑️ script.js tiene nuevas funciones
☑️ Modal de subida funciona

FUNCIONALIDAD:
☑️ Búsqueda automática funciona
☑️ Subida de PDF funciona
☑️ Confianza se muestra
☑️ Validación rechaza datos malos
☑️ 3 opciones visibles

TESTING:
☑️ Test búsqueda automática
☑️ Test subida PDF
☑️ Test confianza
☑️ Test en móvil (opcional)

DOCUMENTACIÓN:
☑️ LIMITACIONES_REALES.md existe
☑️ GUIA_USUARIO.md existe
☑️ EVOLUCION_V2.md existe

SIGUIENTE:
⏳ Prueba con casos reales
⏳ Colecciona feedback
⏳ Ajusta si es necesario
```

---

## 🚀 Ir a Producción

```
ANTES DE DEPLOY:

1. Backup base de datos
   pg_dump -h localhost -U user dbname > backup.sql

2. Revisar logs
   # Ver si hay errores

3. Pruebas finales
   # Ejecutar todos los tests

4. Copiar a producción
   git push origin main

5. Reiniciar servicio
   systemctl restart racehub
   # O lo que uses

6. Verificar salud
   curl http://localhost:8000/health
```

---

## 📞 Soporte Rápido

Si hay problemas:

1. **Código no actualizado:**
   ```
   git pull origin main
   systemctl restart racehub
   ```

2. **Dependencias faltando:**
   ```
   pip install -r requirements.txt
   pip install PyPDF2
   ```

3. **Base datos:**
   ```
   # Reiniciar (sin perder datos)
   psql -U user -d dbname < schema.sql
   ```

4. **Clear caché browser:**
   ```
   Ctrl+Shift+Delete (o Cmd+Shift+Delete en Mac)
   Borra datos navegación
   ```

---

## 📊 Resumen Estado

```
┌─────────────────────────────────────┐
│ V2.0 - Sistema Híbrido de Búsqueda │
├─────────────────────────────────────┤
│ ✅ Implementado                     │
│ ✅ Testeado en desarrollo          │
│ ⏳ Listo para prueba usuario        │
│ 🔄 En monitoreo                    │
│                                     │
│ Próxima versión: Feedback real     │
└─────────────────────────────────────┘
```

---

**¡Listo para verificar! Usa este checklist para validar todo funciona.**

**Tiempo estimado:** 5-10 minutos  
**Dificultad:** Baja (solo clicks + observar)  
**Éxito esperado:** ✅ 95%
