#Este módulo gestiona la persistencia de datos mediante SQLAlchemy. 
#Define el esquema de la base de datos utilizando un modelo ORM (CarreraDB) 
#y configura la fábrica de sesiones para interactuar con el servidor PostgreSQL

import os
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

# Formato: postgresql://usuario:contraseña@localhost:5432/nombre_db
DATABASE_URL = os.getenv("DATABASE_URL","postgresql://jaime:6999@localhost:5432/racehub")

engine = create_engine(DATABASE_URL) #Es el motor que se encarga de conectar con la base de datos. Le indicamos el destino
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #Crea una fábrica de "sesiones". Una sesión es como una conversación con la base de datos: la abres, haces cambios y la cierras.
#Es una clase. Cada vez que queramos guardar algo, haremos db = SessionLocal().
Base = declarative_base() #Es un molde maestro, nuestras tablas heredarán de ella para que SQLAlchemy sepa que existen

# Definimos el modelo que mapea a tu tabla de la base de datos
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    share_token = Column(String, unique=True, index=True, nullable=True)
    
    # Relación: Un usuario tiene muchas carreras guardadas
    carreras = relationship("CarreraDB", back_populates="usuario")

class CarreraDB(Base):
    __tablename__ = "carreras" # Nombre real de la tabla en Postgres

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # FK al usuario
    nombre = Column(String, nullable=False)
    deporte = Column(String, nullable=False)
    fecha = Column(Date)
    localizacion = Column(String)
    distancia_resumen = Column(String)
    url_oficial = Column(String)
    estado_inscripcion = Column(String, default="pendiente")
    
    # Relaciones
    usuario = relationship("UserDB", back_populates="carreras")
    resultados = relationship("ResultadoDB", back_populates="carrera")

class ResultadoDB(Base):
    __tablename__ = "resultados"

    id = Column(Integer, primary_key=True, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id")) # Conecta con la otra tabla
    tiempo_oficial = Column(String) # Sugiero String al principio para evitar líos con INTERVAL
    posicion_general = Column(Integer)
    ritmo_medio = Column(String)
    comentarios = Column(String, nullable=True)

    # Esto permite acceder a la info de la carrera desde un resultado: resultado.carrera.nombre
    carrera = relationship("CarreraDB", back_populates="resultados")

# Crea la tabla si no existe
Base.metadata.create_all(bind=engine)