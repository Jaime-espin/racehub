-- Limpieza inicial (orden importa por foreign keys)
DROP TABLE IF EXISTS resultados;
DROP TABLE IF EXISTS carreras;
DROP TABLE IF EXISTS users;

-- 0. Tabla de Usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    share_token VARCHAR(255) UNIQUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar usuario por defecto para desarrollo
INSERT INTO users (id, nombre_completo, email) 
VALUES (1, 'Usuario Demo', 'demo@racehub.com')
ON CONFLICT (id) DO NOTHING;

-- 1. Tabla de Carreras
CREATE TABLE carreras (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- Vinculación con el usuario
    nombre VARCHAR(255) NOT NULL,
    deporte VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    localizacion VARCHAR(255),
    distancia_resumen VARCHAR(255),
    url_oficial TEXT,
    estado_inscripcion VARCHAR(50) DEFAULT 'pendiente',
    CONSTRAINT carrera_usuario_unica UNIQUE (user_id, nombre, fecha) -- Evita duplicados POR usuario
);

-- 2. Tabla de Resultados (Tus marcas personales)
-- ... (resto igual)
CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    carrera_id INTEGER REFERENCES carreras(id), -- Esto conecta con la tabla de arriba
    tiempo_oficial VARCHAR(50),                 -- Formato texto para flexibilidad (ej: "01:30:45")
    posicion_general INTEGER,
    ritmo_medio VARCHAR(50),                    -- Ej: "4:15 min/km"
    comentarios TEXT                            -- Para sensaciones o clima
);