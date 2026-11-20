"""
Script de consulta y exportacion de la base de datos de RaceHub.
Permite visualizar los registros por consola o exportarlos a un archivo SQLite (.db) o JSON.
"""

import sys
from src.database import SessionLocal, UserDB, CarreraDB, ResultadoDB

def mostrar_datos():
    db = SessionLocal()
    try:
        users = db.query(UserDB).all()
        carreras = db.query(CarreraDB).all()
        resultados = db.query(ResultadoDB).all()

        print("=" * 60)
        print("USUARIOS REGISTRADOS")
        print("=" * 60)
        if not users:
            print("No hay usuarios registrados.")
        for u in users:
            print(f"ID: {u.id} | Nombre: {u.nombre_completo} | Email: {u.email} | Token: {u.share_token or 'N/A'}")

        print("\n" + "=" * 60)
        print("CARRERAS EN EL CALENDARIO")
        print("=" * 60)
        if not carreras:
            print("No hay carreras registradas.")
        for c in carreras:
            print(f"[{c.id}] {c.fecha} - {c.nombre}")
            print(f"    Deporte: {c.deporte} | Lugar: {c.localizacion or 'N/A'} | Distancias: {c.distancia_resumen or 'N/A'}")
            print(f"    Inscripcion: {c.estado_inscripcion} | Plan: {c.estado_planificacion} | User ID: {c.user_id}")

        print("\n" + "=" * 60)
        print("RESULTADOS Y MARCAS GUARDADAS")
        print("=" * 60)
        if not resultados:
            print("No hay resultados guardados.")
        for r in resultados:
            carrera_nombre = r.carrera.nombre if r.carrera else f"Carrera ID {r.carrera_id}"
            print(f"Carrera: {carrera_nombre}")
            print(f"    Tiempo: {r.tiempo_oficial} | Pos. General: {r.posicion_general} | Pos. Cat: {r.posicion_categoria or 'N/A'} | Ritmo: {r.ritmo_medio or 'N/A'}")
        print("=" * 60)

    except Exception as e:
        print(f"Error consultando la base de datos: {e}")
    finally:
        db.close()

def exportar_sqlite(archivo="racehub.db"):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.database import Base

    print(f"Exportando datos a archivo SQLite local: {archivo}...")
    sqlite_engine = create_engine(f"sqlite:///{archivo}")
    Base.metadata.create_all(bind=sqlite_engine)
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_db = SqliteSession()

    pg_db = SessionLocal()
    try:
        users = pg_db.query(UserDB).all()
        for u in users:
            sqlite_db.merge(UserDB(
                id=u.id,
                nombre_completo=u.nombre_completo,
                email=u.email,
                share_token=u.share_token
            ))

        carreras = pg_db.query(CarreraDB).all()
        for c in carreras:
            sqlite_db.merge(CarreraDB(
                id=c.id,
                user_id=c.user_id,
                nombre=c.nombre,
                deporte=c.deporte,
                fecha=c.fecha,
                localizacion=c.localizacion,
                distancia_resumen=c.distancia_resumen,
                url_oficial=c.url_oficial,
                estado_inscripcion=c.estado_inscripcion,
                estado_planificacion=c.estado_planificacion,
                fecha_inscripcion=c.fecha_inscripcion
            ))

        resultados = pg_db.query(ResultadoDB).all()
        for r in resultados:
            sqlite_db.merge(ResultadoDB(
                id=r.id,
                carrera_id=r.carrera_id,
                tiempo_oficial=r.tiempo_oficial,
                posicion_general=r.posicion_general,
                posicion_categoria=r.posicion_categoria,
                ritmo_medio=r.ritmo_medio,
                confianza=r.confianza,
                comentarios=r.comentarios
            ))

        sqlite_db.commit()
        print(f"Exportacion completada con exito. Archivo generado: {archivo}")
        print(f"Puedes abrir '{archivo}' con cualquier visor SQLite como 'DB Browser for SQLite'.")
    except Exception as e:
        print(f"Error durante la exportacion: {e}")
        sqlite_db.rollback()
    finally:
        pg_db.close()
        sqlite_db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sqlite":
        nombre_archivo = sys.argv[2] if len(sys.argv) > 2 else "racehub.db"
        exportar_sqlite(nombre_archivo)
    else:
        mostrar_datos()
