#  Referencia de API

##  URL Base

```
http://127.0.0.1:8000
```

##  Autenticación

Todas las rutas (excepto las públicas) requieren una cookie `user_email`.

**Cómo autenticarse**:
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H \"Content-Type: application/json\" \
  -d '{\"email\": \"jaime@example.com\"}' \
  -c cookies.txt  # Guarda las cookies
```

---

##  Endpoints

###  Autenticación

#### POST `/auth/login`
Inicia sesión o crea una cuenta.

  "estado_planificacion": "candidata",
  "fecha_inscripcion": null,
  "en_colision": false,
  "colisiones_con": [],
**Request Body**:
```json
{
  \"email\": \"jaime@example.com\"
```

**Response** (200 OK):
```json
{
  \"user\": \"jaime@example.com\"
}
```

**Headers**:
- `Set-Cookie: user_email=...` (automático)

---

#### POST `/auth/logout`
Cierra sesión.

**Response** (200 OK):
```json
{
  \"mensaje\": \"Logout exitoso\"
}
```

---

#### GET `/auth/me`

**Cookies Requeridas**:
- `user_email`
**Response** (200 OK):
{
  \"email\": \"jaime@example.com\",
  \"nombre\": \"Jaime Espín\"
}
```

---

###  Perfil

#### GET `/perfil`
Obtiene el perfil completo del usuario.
    \"estado_planificacion\": \"candidata\",
    \"fecha_inscripcion\": null,
    \"en_colision\": false,
    \"colisiones_con\": [],
**Cookies Requeridas**:
- `user_email`

```json
{
  \"nombre\": \"Jaime Espín\",
  \"email\": \"jaime@example.com\"
}

---

#### POST `/perfil`
Actualiza el perfil del usuario.

**Request Body**:
```json
{
  \"nombre_completo\": \"Jaime Espín García\"
}
```

**Response** (200 OK):
```json
{
  \"mensaje\": \"Perfil actualizado\",
  \"nombre\": \"Jaime Espín García\"
}
```

---

###  Carreras

#### POST `/carreras/buscar`
Busca una carrera en internet usando IA.

**Request Body**:
```json
{
  \"nombre\": \"Barcelona Marathon 2026\"
}
```

**Response** (200 OK):
```json
{
  \"nombre_oficial\": \"Barcelona Marathon 2026\",
  \"deporte\": \"running\",
  \"fecha\": \"2026-03-15\",
  \"lugar\": \"Barcelona, España\",
  \"distancias\": [\"42.195 km\"],
  \"url_oficial\": \"https://...\",
  \"estado_inscripcion\": \"abierta\"
}
```

**Errores**:
- `500 Internal Server Error`: No se encontraron resultados o error en IA

---

#### POST `/carreras/confirmar`
Guarda una carrera en la BD del usuario.

**Cookies Requeridas**:
- `user_email`

**Request Body**:
```json
{
  \"nombre_oficial\": \"Barcelona Marathon 2026\",
  \"deporte\": \"running\",
  \"fecha\": \"2026-03-15\",
  \"lugar\": \"Barcelona, España\",
  \"distancias\": [\"42.195 km\"],
  \"url_oficial\": \"https://...\",
  \"estado_inscripcion\": \"abierta\"
}
```

**Response** (200 OK):
```json
{
  \"mensaje\": \"Carrera guardada correctamente\",
  \"nombre\": \"Barcelona Marathon 2026\"
}
```

---

#### GET `/carreras`
Obtiene todas las carreras del usuario.

**Cookies Requeridas**:
- `user_email`

**Response** (200 OK):
```json
[
  {
    \"id\": 1,
    \"nombre\": \"Barcelona Marathon 2026\",
    \"deporte\": \"running\",
    \"fecha\": \"2026-03-15\",
    \"localizacion\": \"Barcelona, España\",
    \"distancia_resumen\": \"42.195 km\",
    \"url_oficial\": \"https://...\",
    \"estado_inscripcion\": \"abierta\",
    \"estado_planificacion\": \"candidata\",
    \"fecha_inscripcion\": null,
    \"en_colision\": false,
    \"colisiones_con\": [],
    \"resultados\": []
  }
]
```

---

#### POST `/carreras/{id}/estado`
Actualiza el estado de planificación de una carrera.

**Cookies Requeridas**:
- `user_email`

**Request Body**:
```json
{
  \"estado\": \"seleccionada\"
}
```

**Response** (200 OK):
```json
{
  \"mensaje\": \"Estado actualizado\",
  \"estado\": \"seleccionada\"
}
```

---

#### POST `/carreras/{id}/inscripcion`
Marca una carrera como inscrita.

**Cookies Requeridas**:
- `user_email`

**Request Body** (opcional):
```json
{
  \"fecha_inscripcion\": \"2026-04-28\"
}
```

**Response** (200 OK):
```json
{
  \"mensaje\": \"Inscripcion registrada\",
  \"fecha_inscripcion\": \"2026-04-28\"
}
```

---

###  Resultados

#### POST `/resultados/buscar`
Busca el resultado de un usuario en una carrera.

**Cookies Requeridas**:
- `user_email`

**Request Body**:
```json
{
  \"nombre_carrera\": \"Barcelona Marathon 2026\",
  \"anio\": 2026,
  \"nombre_corredor\": \"Jaime Espín\",
  \"url_oficial\": null
}
```

**Response** (200 OK) - Encontrado:
```json
{
  \"encontrado\": true,
  \"mensaje\": \"Búsqueda completada\",
  \"corredor\": \"Jaime Espín\",
  \"tiempo\": \"1:30:45\",
  \"posicion\": 234,
  \"posicion_categoria\": 45,
  \"ritmo\": \"2:08 min/km\",
  \"confianza\": 0.95
}
```

**Response** (200 OK) - No encontrado:
```json
{
  \"encontrado\": false,
  \"mensaje\": \"No se encontraron datos exactos. Intenta estas opciones:\",
  \"instrucciones\": \"1. Busca en Sportmaniacs...\\n2. Descarga el PDF...\",
  \"corredor\": \"Jaime Espín\",
  \"confianza\": 0.0
}
```

---

#### POST `/resultados/buscar-archivo`
Sube un PDF/CSV con resultados para extraer datos.

**Cookies Requeridas**:
- `user_email`

**Parámetros (multipart/form-data)**:
- `file`: Archivo PDF o CSV
- `nombre_carrera`: Nombre de la carrera
- `nombre_corredor`: Nombre a buscar (opcional)
- `anio`: Año de la carrera (opcional, default 2024)

**Ejemplo con curl**:
```bash
curl -X POST http://127.0.0.1:8000/resultados/buscar-archivo \
  -F \"file=@resultados.pdf\" \
  -F \"nombre_carrera=Barcelona Marathon\" \
  -F \"nombre_corredor=Jaime Espín\" \
  -F \"anio=2026\" \
  -b cookies.txt
```

**Response** (200 OK):
```json
{
  \"encontrado\": true,
  \"mensaje\": \"¡Encontrado en resultados.pdf!\",
  \"corredor\": \"Jaime Espín\",
  \"tiempo\": \"1:30:45\",
  \"posicion\": 234,
  \"posicion_categoria\": 45,
  \"ritmo\": \"2:08 min/km\",
  \"confianza\": 0.95
}
```

---

#### POST `/resultados/manual`
Guarda un resultado ingresado manualmente.

**Cookies Requeridas**:
- `user_email`

**Request Body**:
```json
{
  \"nombre_carrera\": \"Barcelona Marathon 2026\",
  \"anio\": 2026,
  \"tiempo_oficial\": \"1:30:45\",
  \"posicion_general\": 234,
  \"posicion_categoria\": 45,
  \"ritmo_medio\": \"2:08 min/km\"
}
```

**Response** (200 OK):
```json
{
  \"mensaje\": \"Resultado guardado\"
}
```

---

###  Páginas Públicas

#### GET `/`
Página principal (requiere autenticación).

---

#### GET `/share/{share_token}`
Versión pública del calendario de otro usuario.

**Response**: HTML renderizado con el calendario público

---

##  Estado HTTP

| Código | Significado |
|--------|------------|
| 200 |  Exitoso |
| 401 |  No autenticado (cookie faltante) |
| 404 |  Recurso no encontrado |
| 500 |  Error del servidor (IA, BD, etc.) |

---

##  Ejemplos con Python

### Buscar una carrera

```python
import requests
import json

# Autenticarse
response = requests.post(
    'http://127.0.0.1:8000/auth/login',
    json={'email': 'jaime@example.com'}
)
cookies = response.cookies

# Buscar carrera
response = requests.post(
    'http://127.0.0.1:8000/carreras/buscar',
    json={'nombre': 'Barcelona Marathon 2026'},
    cookies=cookies
)

datos = response.json()
print(json.dumps(datos, indent=2))
```

### Guardar una carrera

```python
# (después de obtener datos de /carreras/buscar)

response = requests.post(
    'http://127.0.0.1:8000/carreras/confirmar',
    json=datos,  # datos del endpoint anterior
    cookies=cookies
)

print(response.json())
```

### Buscar resultado en una carrera

```python
response = requests.post(
    'http://127.0.0.1:8000/resultados/buscar',
    json={
        'nombre_carrera': 'Barcelona Marathon 2026',
        'anio': 2026,
        'nombre_corredor': 'Jaime Espín'
    },
    cookies=cookies
)

resultado = response.json()
print(f\"Tiempo: {resultado['tiempo']}\")
print(f\"Posición: {resultado['posicion']}\")
```

---

##  Documentación Interactiva

Swagger UI (interfaz gráfica):
```
http://127.0.0.1:8000/docs
```

ReDoc (documentación offline):
```
http://127.0.0.1:8000/redoc
```

---

**Más ayuda**: [docs/05-TROUBLESHOOTING.md](./05-TROUBLESHOOTING.md)
