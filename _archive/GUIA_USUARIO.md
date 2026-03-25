# 📖 GUÍA DE USUARIO: Búsqueda de Resultados (Versión 2.0)

**Versión:** 2.0 - Realista  
**Fecha:** 25 de Marzo 2026

---

## 👤 ¿Quién Eres Tú?

**Escenario:** Hiciste una carrera, quieres ver tu tiempo y posición

**Problema anterior:** 
```
Hacías click en "Ver Resultado" 
→ Sistema intentaba buscar automáticamente
→ Si fallaba, listo. No había nada más que hacer
```

**Solución nueva:**
```
Tienes 3 opciones cada una con buenos resultados
Tú eliges cuál es más conveniente para tu caso
```

---

## 🎯 Tres Opciones. Elige la Tuya

### OPCIÓN 1: Búsqueda Automática (Rápida - 30 seg)

**Cuándo:** Si ya tienes la URL de la web de resultados a mano

**Pasos:**
```
1. Click en "🏅 Ver Resultado"
2. Confirma tu nombre
3. Dí "SÍ" a búsqueda automática
4. (Opcional) Proporciona URL si tienes
5. Espera ~15 segundos
```

**Resultado:**
- ✅ Si funciona: Ves tu tiempo, posición
- ❌ Si no funciona: Pasa a Opción 2

**Precisión:** 40-80% según carrera

---

### OPCIÓN 2: Subir PDF (Muy Preciso - 99%)

**Cuándo:** Sistema no encontró automáticamente

**Pasos:**
```
1. Ve a la web oficial de la carrera
2. Busca "Resultados" o "Clasificación"
3. Descarga el PDF/archivo de resultados
4. Vuelve aquí, dí "Cancelar" a búsqueda automática
5. Sube el archivo
6. Sistema busca automáticamente tu nombre
```

**Resultado:**
- ✅ Casi siempre funciona
- Precisión: 95-99%
- Tiempo: 5 segundos

**Ejemplo:**
```
Media Maratón Málaga:
1. Ve a www.mediamaratonmalaga.com
2. Click "Resultados" → te lleva a Sportmaniacs
3. Descarga PDF
4. Súbelo aquí
5. ✅ "¡Encontrado! 1:55:32, Pos. 234"
```

---

### OPCIÓN 3: Ingresar Manualmente (Para casos excepcionales)

**Cuándo:** No hay archivo digital

**Pasos:**
```
1. Si búsqueda automática falló
2. Ves instrucciones con opciones
3. Dí "Cancelar" a subida de archivo
4. Copia manualmente desde web:
   - Tu tiempo (ej: 1:45:32)
   - Tu posición (ej: 142)
   - Tu categoría (ej: M40)
   - Tu ritmo (ej: 4:55 min/km)
```

**Precisión:** 100% (tú lo controlas)

---

## 📱 Flujo Visual

```
Haces click en "🏅 Ver Resultado"
        ↓
¿"Buscar automático"? 
    ↓         ↓
   SÍ        NO
    ↓         ↓
Búsqueda   Modal subida
automática  PDF
    ↓
¿Funcionó?
  ↓    ↓
 SÍ   NO
  ↓    ↓
✅    ¿Subir 
      PDF?
       ↓ ↓
      SÍ NO
       ↓ ↓
      📄 ✋ Manual
```

---

## 🆘 Casos Especiales

### Caso 1: "Descargué PDF pero qué archivo?"

```
Passos:
1. Ve a web oficial de carrera
2. Busca botón "Resultados"
3. Busca botón "Descargar" o "Ver Clasificación"
4. Guarda el archivo
5. Sube aquí

Ejemplo Media Maratón Málaga:
www.mediamaratonmalaga.com
  → "Resultados" (botón)
  → Te lleva a Sportmaniacs
  → "Ver Clasificación"
  → Botón "Descargar PDF"
  → Guarda en tu PC
```

### Caso 2: "No hay PDF, solo tabla en web"

```
Si la tabla es HTML (no PDF):
1. Intenta búsqueda automática con esa URL
2. Si falla, copia los datos manualmente

Si no puedes copiar (tabla en imagen):
1. Lee desde pantalla
2. Ingresa manualmente
```

### Caso 3: "Tengo CSV, no PDF"

```
¡Perfecto! Funciona también
1. Descarga CSV
2. Súbelo aquí
3. Sistema busca tu nombre
4. ✅ Datos extraídos
```

---

## ✅ Qué Busca el Sistema

Cuando subes archivo o haces búsqueda automática, el sistema busca:

```
1. Tu nombre exacto
   ✅ "Jaime Espín"
   ✅ "Espín, Jaime"
   ✅ "ESPÍN JAIME"
   ❌ "Jaime" (muy corto)

2. Tu tiempo
   ✅ "1:45:32" (formato HH:MM:SS)
   ✅ "1:45:32"
   ❌ "145:32" (formato inválido)

3. Tu posición
   ✅ "142" (número)
   ✅ "Pos. 142"
   ❌ "abc" (no número)

4. Tu categoría (opcional)
   ✅ "M40" (categoría)
   ✅ "5" (posición en categoría)
```

---

## 🎯 Consejos Prácticos

### ✅ HACES BIEN:
```
• Descarga PDF el mismo día de carrera
• Busca tu nombre completo, no solo el nombre
• Proporciona URL si tienes
• Sube PDF si búsqueda automática falla
```

### ❌ NO HAGAS:
```
• Esperar a que búsqueda automática funcione siempre
• Usar solo "Jaime" sin apellido
• Cambiar letras del nombre
• Dar números inventados
```

---

## 📊 Expectativas Realistas

### Búsqueda Automática:
```
Funciona bien: 40-80% de las carreras
Funciona mal: 20-60% de las carreras
Depende: Del portal (Sportmaniacs, MyLaps, etc)
Tiempo: 10-15 segundos
```

### Subida de PDF:
```
Funciona bien: 95-99% si tienes el PDF
Fácil: Descarga y sube (2 clicks)
Rápido: 5 segundos
Precisión: Casi perfecta
```

### Manual:
```
Funciona siempre: 100%
Precisión: 100%
Tiempo: 2-3 minutos
```

---

## 🚀 Paso a Paso: Media Maratón Málaga

**Escenario:** Corriste la Media Maratón de Málaga 2024

### Intento 1: Búsqueda Automática
```
1. Click "🏅 Ver Resultado"
2. Confirmas "Jaime Espín"
3. Click "Sí, buscar automático"
4. (Tienes URL oficial, la proporcionas)
5. Esperas 15 segundos
6. ❌ "No se encontró"
7. Pasa al Intento 2
```

### Intento 2: Subir PDF
```
1. Abres www.mediamaratonmalaga.com
2. Buscas "Resultados" → va a Sportmaniacs
3. Le das a "Ver Clasificación"
4. Descargas el PDF
5. Vuelves a RaceHub
6. Click "🏅 Ver Resultado"
7. Confirmas "Jaime Espín"
8. Click "No, subir PDF"
9. Seleccionas el PDF descargado
10. Click "Procesar"
11. ✅ 5 segundos después:
    "¡Encontrado! 1:55:32, Pos. 234"
```

---

## 💬 Preguntas Frecuentes

### P: ¿Por qué no funciona la búsqueda automática?

R: Porque muchas carreras usan portales dinámicos que requieren clicks. Nuestro sistema no puede hacer clicks automáticos. Es una limitación tecnológica.

---

### P: ¿Qué diferencia hay con la versión anterior?

Antes:
```
Click → Búsqueda automática → Si funciona ✅, si no ❌
```

Ahora:
```
Click → Opción de búsqueda automática
     → Si no funciona, opción 2: Subir PDF
     → Si tampoco, opción 3: Ingresar manual
     → Una de las 3 siempre funciona
```

---

### P: ¿Cuánto pesa el PDF máximo?

R: No hay límite especificado, pero típicamente los PDFs son < 10MB

---

### P: ¿Puedo subir CSV en lugar de PDF?

R: Sí, funciona igual. También Excel.

---

### P: ¿Y si no recuerdo mi tiempo exacto?

R: Sube PDF si tienes, o entra en la web y cópialo de ahí.

---

### P: ¿Los datos se guardan?

R: Sí, se guardan pero solo si proporcionas datos válidos. El sistema rechaza datos inventados.

---

## 🔐 Tu Privacidad

- ✅ Los archivos PDF se procesan localmente
- ✅ No se envían a servidores externos
- ✅ Se borran después de procesar
- ✅ Solo se guardan tus datos de resultado

---

## 📞 Soporte

Si algo no funciona:
1. Intenta las 3 opciones
2. Si ninguna funciona, contáctanos
3. Proporciona detalles de la carrera

---

## 🎉 Resumen

**Nueva versión: 3 opciones, 1 siempre funciona**

- Opción 1: Búsqueda automática (40-80% casos)
- Opción 2: Subir PDF (95-99% casos)
- Opción 3: Ingresar manual (100% casos)

**Resultado:** Ya no hay frustración. Siempre hay un camino.

---

**¡Bienvenido a RaceHub 2.0! Ahora con opciones reales.**
