{
    'name': 'Sistema de Gestión de Museos',
    'version': '1.0.0',
    'summary': 'Gestión integral de múltiples museos, objetos, actividades e informes',
    'description': """
        Sistema completo para gestionar múltiples museos, sus objetos históricos,
        historias de barrios, convenios, actividades y generación de informes estadísticos.
    """,
    'category': 'Services/Museums',
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'calendar',
        'contacts',
        'web',
        'website'
    ],
    'external_dependencies': {
        'python': ['reportlab', 'xlsxwriter'],
    },
    'data': [
    'security/museo_security.xml',
    'security/ir.model.access.csv',
    
    'data/museo_data.xml',
    #'data/museo_models_data.xml',
    'data/museo_demo.xml',
    'data/museo_categoria_data.xml',
    
    'views/res_partner_views.xml',
    'views/museo_views.xml',
    'views/objeto_views.xml',
    'views/historia_barrio_views.xml',
    'views/convenio_views.xml',
    'views/actividad_views.xml',
    'views/informe_views.xml',
    'views/configuracion_views.xml', 
    'views/registro_asistencia_views.xml',
    #'views/dashboard_views.xml',
    'views/configuracion_views.xml',
    'views/wizard_views.xml',

    'views/kanban_museo_views.xml',
    'views/kanban_objetos_views.xml',
    'views/kanban_actividades_views.xml',
    'views/kanban_galeria_views.xml',
    'views/kanban_convenios_views.xml',
    'views/kanban_historia_barrios_views.xml',
    'views/filtros_personalizados_views.xml',
    'views/actions_views.xml',
    'views/museo_galeria_views.xml',
    'views/reportes_views.xml',
    'views/menu_views.xml',

    'templates/museo_landing.xml',
    'templates/museo_templates.xml',
    'templates/layout_museo.xml',
    'templates/historia_barrio_detalle.xml',
    
    'reports/informe_estadistico_report.xml',
    'reports/informe_estadistico_template.xml',
],
    'demo': [
        'demo/museo_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        
        'web.assets_frontend': [
            'museos/static/css/museo_landing.css',  
            #'museos/static/js/app.js', 
            'museos/static/lib/fancybox/fancybox.css',
            'museos/static/lib/fancybox/fancybox.umd.js',
            'museos/static/lib/fancybox/cloudflare/all.min.css',
            'museos/static/lib/fancybox/cloudflare/googleapis.css',
            'museos/static/css/bootstrap-icons.css',
           
            'museos/static/css/museo_carousel.css',
            'museos/static/js/museo_effects.js',
        ],
        'web.assets_backend': [
            'museos/static/css/kanban_style.css',
        ],
    },
    
    
}



