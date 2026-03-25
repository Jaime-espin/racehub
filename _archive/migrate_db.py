#!/usr/bin/env python3
"""
Script para migrar la BD e agregar las nuevas columnas
"""

import os
from sqlalchemy import text
from src.database import engine

def migrate_db():
    """Añade columnas faltantes si no existen"""
    
    try:
        connection = engine.connect()
        
        # Agregar posicion_categoria si no existe
        try:
            connection.execute(text("ALTER TABLE resultados ADD COLUMN posicion_categoria INTEGER"))
            connection.commit()
            print("✅ Columna posicion_categoria agregada")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e):
                print("✓ Columna posicion_categoria ya existe")
            else:
                print(f"⚠️ Error al agregar posicion_categoria: {e}")
        
        # Agregar confianza si no existe
        try:
            connection.execute(text("ALTER TABLE resultados ADD COLUMN confianza INTEGER"))
            connection.commit()
            print("✅ Columna confianza agregada")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e):
                print("✓ Columna confianza ya existe")
            else:
                print(f"⚠️ Error al agregar confianza: {e}")
        
        connection.close()
        print("\n✅ Migración completada")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    migrate_db()
