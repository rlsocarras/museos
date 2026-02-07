# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MuseoConfigSettings(models.TransientModel):
    _name = 'museo.config.settings'
    _inherit = 'res.config.settings'
    _description = 'Configuración del Sistema de Museos'
    
    # Informes Automáticos
    generar_informes_auto = fields.Boolean(
        string='Generar Informes Automáticamente',
        default=True,
        config_parameter='museos.generar_informes_auto'
    )
    
    frecuencia_informes = fields.Selection([
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
    ], string='Frecuencia de Informes', default='mensual',
    config_parameter='museos.frecuencia_informes')
    
    dias_previos_aviso = fields.Integer(
        string='Días Previos para Aviso',
        default=30,
        config_parameter='museos.dias_previos_aviso'
    )
    
    # Actividades
    capacidad_maxima_default = fields.Integer(
        string='Capacidad Máxima por Defecto',
        default=50,
        config_parameter='museos.capacidad_maxima_default'
    )
    
    dias_antelacion_reserva = fields.Integer(
        string='Días de Antelación para Reservas',
        default=7,
        config_parameter='museos.dias_antelacion_reserva'
    )
    
    # Convenios
    aviso_vencimiento_convenio = fields.Integer(
        string='Aviso Vencimiento Convenios (días)',
        default=15,
        config_parameter='museos.aviso_vencimiento_convenio'
    )
    
    # Notificaciones
    notificar_actividades = fields.Boolean(
        string='Notificar Actividades Próximas',
        default=True,
        config_parameter='museos.notificar_actividades'
    )
    
    dias_previos_notificacion = fields.Integer(
        string='Días Previos para Notificación',
        default=3,
        config_parameter='museos.dias_previos_notificacion'
    )