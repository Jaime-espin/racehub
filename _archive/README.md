# 📁 Archive - Documentación y Archivos Históricos

Esta carpeta contiene documentación de versiones anteriores y notas de sesiones durante el desarrollo.

## Contenido

Los archivos aquí son **históricos** y se mantienen como referencia, pero **ya no se usan** en la documentación principal.

Ver documentación actual en: [/docs/](../docs/)

## 📝 Documentación Archivada

- `DIAGNOSTICO_BUSQUEDA.md` - Análisis de búsqueda (v1)
- `ESTADO_FINAL.md` - Estado final de v1
- `EVOLUCION_V2.md` - Evolución a v2
- `GUIA_COMPLETA.md` - Guía antigua
- `GUIA_USUARIO.md` - Guía antigua
- `IMPLEMENTACION_COMPLETADA.md` - Notas de implementación
- `LIMITACIONES_REALES.md` - Análisis de limitaciones
- `PLAN_IMPLEMENTACION.md` - Plan antiguo
- `REFERENCIA_RAPIDA.md` - Referencia rápida antigua
- `RESUMEN_EJECUTIVO_V2.md` - Resumen ejecutivo v2
- `RESUMEN_ESTADO.md` - Resumen de estado
- `RESUMEN_SOLUCION.md` - Resumen de solución
- `VERIFICACION_DESPLEGABLES.md` - Verificación
- `VERIFICACION_V2.md` - Verificación v2

## 🗄️ Scripts de Migración Archivados

- `migrate_db.py` - Script Python para agregar columnas a la BD (historicamente usado en v1)
- `migration.sql` - SQL puro para migraciones (alternativa a migrate_db.py)

**Nota**: Ya no son necesarios porque `src/database.py` incluye automáticamente la función `migrate_add_missing_columns()` que crea las columnas faltantes al iniciar la aplicación.

## 🔄 Información Consolidada

La información de estos archivos se ha consolidado en:

| Nuevo Documento | Reemplaza |
|-------|-----------|
| [../docs/01-SETUP.md](../docs/01-SETUP.md) | GUIA_COMPLETA.md, PLAN_IMPLEMENTACION.md |
| [../docs/02-ARCHITECTURE.md](../docs/02-ARCHITECTURE.md) | DIAGNOSTICO_BUSQUEDA.md, EVOLUCION_V2.md |
| [../docs/03-USER-GUIDE.md](../docs/03-USER-GUIDE.md) | GUIA_USUARIO.md, REFERENCIA_RAPIDA.md |
| [../docs/04-API-REFERENCE.md](../docs/04-API-REFERENCE.md) | IMPLEMENTACION_COMPLETADA.md |
| [../docs/05-TROUBLESHOOTING.md](../docs/05-TROUBLESHOOTING.md) | LIMITACIONES_REALES.md |

---

**Última actualización**: 25 de Marzo 2026
