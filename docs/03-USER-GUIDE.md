#  Guía de Usuario

##  Casos de Uso

### Caso 1: Buscar y Agregar una Carrera

**Objetivo**: Encontrar una carrera y agregarla a tu calendario.

**Pasos**:

1. **Abre la aplicación web**
   ```
   http://127.0.0.1:8000
   ```

2. **Inicia sesión**
   - Ingresa tu email (se crea automáticamente si no existe)

3. **Busca una carrera**
   - Escribe el nombre en el buscador (ej: \"Barcelona Marathon 2026\")
   - Haz clic en \"Buscar\"
   - **Espera** a que la IA busque en internet (~5-10 segundos)

4. **Revisa los datos**
   - Nombre oficial
   - Deporte (Running, Trail, Ciclismo, etc.)
   - Fecha y lugar
   - Distancias disponibles
   - Estado de inscripción

5. **Confirma**
   - Si los datos son correctos, haz clic en \"Guardar\"
   - Si no, haz clic en \"Cancelar\" para editar o rechazar

**Resultado**: La carrera aparece en tu calendario.

---

### Caso 2: Buscar tu Resultado en una Carrera

**Objetivo**: Encontrar tu tiempo y posición en una carrera que ya completaste.

**Pasos**:

1. **Dirígete a la sección \"Mis Resultados\"**

2. **Selecciona una carrera**
   - Escoge una carrera de tu calendario

3. **Ingresa tu nombre** (opcional)
   - Si dejas en blanco, usa el nombre de tu perfil

4. **Haz clic en \"Buscar Resultado\"**
   - La IA buscará en portales conocidos (Sportmaniacs, ChronoEmpresa, etc.)
   - Si no encuentra, te mostrará instrucciones manuales

**Opciones si la búsqueda automática falla**:

#### Opción A: Subir PDF/CSV
1. Si tienes el archivo de resultados descargado:
   - Haz clic en \"Subir Archivo\"
   - Selecciona el PDF o CSV
   - Indica tu nombre
   - La IA extrae tus datos del archivo

#### Opción B: Proporcionar URL Oficial
1. Si conoces la URL de los resultados:
   - Haz clic en \"Usar URL\"
   - Pegue la dirección web
   - Haz clic en \"Buscar\"

**Resultado**: Tu tiempo, posición y ritmo aparecen en el calendario.

---

## Funcionalidades

### Calendario de Carreras

- **Vista mensual**: Arrastra el calendario para cambiar meses
- **Colores por deporte**: Running (rojo), Trail (verde), Ciclismo (azul), etc.
- **Filtros**: Muestra solo el deporte que quieres

### Planificación de Calendario

- **Candidatas**: carreras que te interesan pero aún no has decidido.
- **Seleccionadas**: pruebas que consideras seriamente para tu calendario.
- **Inscritas**: carreras ya confirmadas.
- **Descartadas**: pruebas que decides dejar fuera.

**Cómo usarlo**:
1. Al añadir una carrera, queda como **Candidata**.
2. Muévela a **Seleccionada** cuando quieras compararla con otras.
3. Si te inscribes, márcala como **Inscrita**.
4. Si la descartas, pásala a **Descartada**.

**Colisiones**:
- Solo se muestran en **Seleccionadas** e **Inscritas**.
- Si dos carreras comparten fecha, verás una etiqueta de **Colisión** para decidir.

### Mi Perfil

- **Nombre completo**: Editable
- **Email**: Tu identificador
- **Token de compartir**: Para que otros vean tu calendario público

### Compartir Calendario

1. Copia tu **link de compartir** del perfil
2. Envíalo a amigos
3. Ellos pueden ver tu calendario sin iniciadora sesión

---

## Uso desde Terminal (CLI)

Si prefieres usar la línea de comandos, ejecuta:

```bash
python src/main.py
```

**Flujo interactivo**:
1. Introduce el nombre de la carrera
2. Revisa los datos que extrajo la IA
3. Confirma (s/n)
4. Se guarda en la BD

---

##  Personalización

### Cambiar el Tema

Edita `static/styles.css` para cambiar colores, fuentes, etc.

### Agregar Nuevos Deportes

1. Abre `src/main.py`
2. En la clase `CarreraSchema`, modifica el validador `validar_deporte()`
3. Agrega al array `deportes_validos`

---

##  Iconos y Símbolos

| Símbolo | Significado |
|---------|----------|
|  | Completado exitosamente |
|  | Error o procesamiento fallido |
| [Aviso] | Advertencia o información importante |
|  | Búsqueda en progreso |
|  | Fecha/Calendario |
|  | Resultado encontrado |
|  | Deporte/Actividad |

---

##  Consejos

### Para Mejores Resultados de Búsqueda

1. **Sé específico**: \"Barcelona Marathon 2026\" es mejor que \"Barcelona\"
2. **Usa años**: Incluye el año para evitar confusiones
3. **Caracteres especiales**: Accents/tildes se detectan automáticamente

### Para Encontrar Resultados

1. **Muchas carreras usan portales estándar**:
   - **Sportmaniacs** (España)
   - **ChronoEmpresa** (España)
   - **Cronos** (Europa)

2. **Si tu carrera no está en estos**, sube el PDF:
   - La mayoría de eventos proporcionan classificaciones en PDF
   - El sistema las lee automáticamente

3. **Nombre flexible**:
   - Puedes escribir \"Juan Pérez\" o \"Perez\"
   - \"JUAN PABLO\" o \"Juan Pablo\"
   - El sistema entiende variaciones

---

##  Preguntas Frecuentes

**P: ¿Qué información necesita la IA para buscar una carrera?**
R: Solo el nombre. A partir de ahí, busca automáticamente la fecha, distancias y lugar oficiales.

**P: ¿Se guardan mis datos en la nube?**
R: No, están en tu PostgreSQL local. Puedes desplegar en un servidor si quieres.

**P: ¿Qué pasa si ingreso mal el nombre de una carrera?**
R: La IA intenta lo mejor. Si falla, revisa el nombre oficial y reinenta.

**P: ¿Funciona offline?**
R: No. Necesita internet para:
- Buscar en Tavily
- Procesar con Groq

**P: ¿Puedo editar dates después de guardarlas?**
R: Aún no en la interfaz. Próximamente. Por ahora, puedes editar directamente en PostgreSQL.

---

**Más ayuda en**: [docs/05-TROUBLESHOOTING.md](./05-TROUBLESHOOTING.md)
