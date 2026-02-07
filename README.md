# Sistema de Gestión de Museos - Módulo Odoo 18

![Odoo 18](https://img.shields.io/badge/Odoo-18-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

## 📋 Descripción

Módulo completo para la gestión integral de múltiples museos en Odoo 18. Permite administrar museos, sus objetos históricos, historias de barrios, convenios, actividades y generar informes estadísticos automatizados.

## ✨ Características Principales

### 🏛️ **Gestión de Museos**
- Creación y administración de múltiples museos
- Reseñas históricas detalladas
- Información de contacto y ubicación
- Campos calculados automáticos (total objetos, actividades, convenios)

### 🏺 **Gestión de Objetos Históricos**
- Catálogo completo de objetos/artefactos
- Historia detallada de cada objeto
- Estado de conservación y ubicación
- Valor estimado y categorización
- Gestión de imágenes

### 🏘️ **Historias de Barrios**
- Registro de historias locales y testimonios
- Tipos de fuentes (oral, documental, arqueológica)
- Estado de investigación
- Documentación adjunta

### 🤝 **Convenios de Trabajo**
- Gestión de acuerdos con instituciones
- Tipos de convenios (investigación, educación, cultural, etc.)
- Seguimiento de fechas y estados
- Documentos adjuntos
- Notificaciones automáticas de vencimiento

### 🗓️ **Actividades y Eventos**
- Planificación de actividades (talleres, conferencias, exposiciones)
- Asignación de trabajadores responsables
- Control de capacidad y asistencia
- Registro detallado de participación
- Vista de calendario integrada
- Análisis de público objetivo

### 📊 **Informes Estadísticos**
- Generación automática de informes
- Períodos: mensual, trimestral, anual
- Métricas clave (asistencia, ingresos, satisfacción)
- Exportación a PDF
- Análisis comparativos por tipo de actividad

### 👥 **Gestión de Personal**
- Extensión del modelo de contactos para trabajadores
- Asignación de especialidades y cargos
- Control de horas semanales
- Relación con actividades asignadas

## 🗂️ Estructura del Módulo

```
museos_gestion/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── museo_model.py          # Modelo Museo
│   ├── objeto_model.py         # Modelo Objetos
│   ├── historia_barrio_model.py # Historias de barrios
│   ├── convenio_model.py       # Convenios
│   ├── actividad_model.py      # Actividades
│   ├── informe_model.py        # Informes estadísticos
│   └── res_partner.py          # Extensión de Contactos
├── views/
│   ├── museo_views.xml         # Vistas de Museos
│   ├── objeto_views.xml        # Vistas de Objetos
│   ├── historia_barrio_views.xml # Vistas Historias
│   ├── convenio_views.xml      # Vistas Convenios
│   ├── actividad_views.xml     # Vistas Actividades
│   ├── informe_views.xml       # Vistas Informes
│   ├── menu_views.xml          # Estructura de menús
│   └── res_partner_views.xml   # Vistas de Contactos
├── security/
│   ├── ir.model.access.csv     # Permisos de acceso
│   └── museo_security.xml      # Grupos de seguridad
├── data/
│   └── museo_data.xml          # Datos de demostración
├── reports/
│   ├── informe_estadistico_report.xml  # Configuración de reportes
│   └── informe_estadistico_template.xml # Plantilla de reportes
├── static/
│   └── description/
│       └── icon.png            # Icono del módulo
└── controllers/
    └── main.py                 # Controladores (si aplica)
```

## 🔧 Requisitos Técnicos

### Versiones Compatibles
- **Odoo**: 18.0
- **Python**: 3.10+
- **Base de datos**: PostgreSQL 12+

### Dependencias
```python
'depends': [
    'base',
    'mail',
    'calendar',
    'contacts',
    'web',
]
```

## 🚀 Instalación

### Método 1: Instalación Manual
1. Copiar la carpeta `museos_gestion` a la carpeta `addons` de Odoo
2. Reiniciar el servidor Odoo
3. Actualizar la lista de módulos:
   - Modo Desarrollador → Aplicaciones → Actualizar lista de aplicaciones
4. Buscar "Sistema de Gestión de Museos"
5. Hacer clic en Instalar

### Método 2: Comando Odoo-bin
```bash
./odoo-bin -d mi_basedatos -i museos_gestion --stop-after-init
```

### Método 3: Desde Interfaz Web
1. Ir a **Aplicaciones**
2. Buscar "Museos" o "Sistema de Gestión de Museos"
3. Hacer clic en **Instalar**

## 🛠️ Configuración

### 1. Configuración Inicial
Después de instalar el módulo:
1. Ir al menú **Museos**
2. Crear el primer museo con sus datos básicos
3. Configurar trabajadores en **Contactos** → Marcar "¿Es Trabajador del Museo?"

### 2. Grupos de Seguridad
El módulo incluye 4 niveles de acceso:

| Grupo | Permisos |
|-------|----------|
| **Administrador de Museos** | Acceso completo, creación, modificación, eliminación |
| **Gestor de Museo** | Lectura/escritura en su museo, sin eliminación |
| **Trabajador de Museo** | Solo lectura, acceso limitado |
| **Visor de Museos** | Solo lectura, acceso público |

### 3. Configuración de Informes Automáticos
1. Ir a **Museos** → **Configuración**
2. Configurar frecuencia de generación automática
3. Establecer formatos de exportación

## 📖 Uso del Módulo

### 1. Gestión de Museos
**Crear un nuevo museo:**
1. Ir a **Museos** → **Gestión** → **Museos**
2. Hacer clic en **Crear**
3. Completar:
   - Nombre del museo
   - Fecha de creación
   - Reseña histórica
   - Información de contacto

### 2. Registrar Objetos Históricos
**Agregar un objeto:**
1. Desde el museo, pestaña **Objetos** → **Crear**
2. Especificar:
   - Código de inventario (único)
   - Historia del objeto
   - Estado de conservación
   - Ubicación actual
   - Imagen (opcional)

### 3. Planificar Actividades
**Crear una actividad:**
1. Ir a **Museos** → **Actividades** → **Actividades**
2. Hacer clic en **Crear**
3. Definir:
   - Tipo de actividad (taller, conferencia, etc.)
   - Fechas y horarios
   - Capacidad máxima
   - Trabajadores responsables
   - Costo (si aplica)

### 4. Generar Informes
**Informe manual:**
1. Ir a **Museos** → **Informes** → **Informes Estadísticos**
2. Hacer clic en **Crear**
3. Seleccionar:
   - Museo
   - Período (mensual, trimestral, anual)
   - Fechas de inicio y fin
4. Hacer clic en **Guardar** (las estadísticas se calculan automáticamente)
5. **Generar PDF** cuando esté listo

**Informes automáticos:**
- Los informes mensuales se generan automáticamente el primer día de cada mes
- Los trimestrales al final de cada trimestre
- Los anuales al final del año

## 📊 Características Avanzadas

### 📅 Calendario de Actividades
- Vista integrada de calendario
- Filtrado por tipo de actividad
- Color coding por estado
- Arrastrar y soltar para reprogramar

### 📈 Análisis Estadístico
- Gráficos de evolución de asistencia
- Pivotes por tipo de actividad y público objetivo
- Comparativas entre museos
- Tendencias mensuales/trimestrales/anuales

### 🔔 Notificaciones Automáticas
- Recordatorios de vencimiento de convenios
- Alertas de sobrecapacidad en actividades
- Notificaciones de actividades próximas

### 📎 Documentación Adjunta
- Imágenes de objetos
- Documentos de convenios
- Archivos PDF de informes
- Documentación de investigaciones

## 🔒 Seguridad y Permisos

### Reglas de Registro
- Cada usuario solo ve los datos de sus museos asignados
- Los trabajadores solo ven actividades donde están asignados
- Los visores solo tienen acceso de lectura

### Auditoría
- Tracking de cambios en campos importantes
- Registro de creación/modificación
- Historial de actividades en registros

## 🐛 Solución de Problemas

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| **No aparece el menú Museos** | Verificar que el usuario tenga asignado el grupo correspondiente |
| **Error al generar PDF** | Verificar que wkhtmltopdf esté instalado y configurado |
| **No se calculan estadísticas** | Verificar que las actividades estén marcadas como "realizadas" |
| **Permisos insuficientes** | Asignar al usuario al grupo "Administrador de Museos" |

### Logs de Depuración
```bash
./odoo-bin -d mi_basedatos --log-level=debug --log-handler=museos_gestion:DEBUG
```

## 🔄 Mantenimiento

### Tareas Programadas
- **Verificación de convenios vencidos**: Diariamente a las 06:00
- **Generación de informes mensuales**: Primer día de cada mes a las 00:00
- **Limpieza de registros temporales**: Semanalmente los domingos a las 02:00

### Backup de Datos
Se recomienda:
1. Backup regular de la base de datos
2. Almacenamiento seguro de documentos adjuntos
3. Exportación periódica de informes críticos

## 📈 Mejoras Futuras

### Planeadas para próximas versiones:
1. **API REST** para integración con sistemas externos
2. **App móvil** para registro de asistencia
3. **Sistema de reservas** en línea
4. **Integración con pasarelas de pago**
5. **Análisis predictivo** de asistencia
6. **Gamificación** para visitantes
7. **Realidad aumentada** para exposiciones

## 👥 Contribución

### Reportar Issues
1. Verificar que el problema no esté ya reportado
2. Proporcionar información detallada:
   - Versión de Odoo
   - Pasos para reproducir
   - Mensajes de error
   - Capturas de pantalla

### Desarrollo
1. Fork del repositorio
2. Crear rama de características
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

### Convenciones de Código
- Seguir las convenciones de código de Odoo
- Documentar funciones y métodos
- Incluir tests unitarios
- Mantener compatibilidad con versiones anteriores

## 📄 Licencia

Este módulo está licenciado bajo la **LGPL-3**. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Soporte

### Soporte Comunitario
- Foros de la comunidad Odoo
- Issues en GitHub
- Grupos de Telegram/WhatsApp

### Soporte Profesional
Para soporte empresarial o desarrollo personalizado, contactar a los desarrolladores del módulo.

## 📚 Recursos Adicionales

### Documentación
- [Documentación oficial de Odoo 18](https://www.odoo.com/documentation/18.0/)
- [Guías de desarrollo Odoo](https://www.odoo.com/documentation/18.0/developer/)
- [API Reference](https://www.odoo.com/documentation/18.0/developer/reference/)

### Tutoriales
- [Videos tutoriales en YouTube](https://www.youtube.com/results?search_query=odoo+18+tutorial)
- [Blogs de la comunidad](https://www.odoo.com/blog)
- [Cursos en línea](https://www.odoo.com/slides)

---

**⭐ Si este módulo te fue útil, considera darle una estrella en GitHub!**

**📧 Contacto:** [robertoleonsocarras@gmail.com](mailto:robertoleonsocarras@gmail.com)

**🌐 Sitio Web:** [www.tusitio.com](https://www.tusitio.com)

**💬 Comunidad:** [Foros Odoo](https://www.odoo.com/es_ES/forum)

---

*Última actualización: Febrero 2026*  
*Versión del módulo: 1.0.0*  
*Mantenido por: Roberto/Equipo*