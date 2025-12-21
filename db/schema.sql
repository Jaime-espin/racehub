-- 1. Tabla de Carreras (La información general)
DROP TABLE IF EXISTS carreras CASCADE;
CREATE TABLE carreras (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    deporte VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    localizacion VARCHAR(255),
    distancia_resumen VARCHAR(255),
    url_oficial TEXT,
    estado_inscripcion VARCHAR(50) DEFAULT 'pendiente',
    CONSTRAINT carrera_unica UNIQUE (nombre, fecha) -- Evita duplicados
);
ALTER TABLE carreras ADD CONSTRAINT carrera_unica UNIQUE (nombre, fecha);

-- 2. Tabla de Resultados (Tus marcas personales)
CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    carrera_id INTEGER REFERENCES carreras(id), -- Esto conecta con la tabla de arriba
    tiempo_oficial INTERVAL,                    -- Formato HH:MM:SS
    posicion_general INTEGER,
    ritmo_medio VARCHAR(20),                    -- Ej: "4:15 min/km"
    comentarios TEXT                            -- Para sensaciones o clima
);