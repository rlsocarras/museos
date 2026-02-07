# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_trabajador_museo = fields.Boolean(
        string='¿Es Trabajador del Museo?',
        default=False
    )
    
    cargo = fields.Char(
        string='Cargo'
    )
    
    especialidad = fields.Char(
        string='Especialidad'
    )
    
    fecha_ingreso = fields.Date(
        string='Fecha de Ingreso'
    )
    
    horas_semanales = fields.Float(
        string='Horas Semanales'
    )
    
    actividad_ids = fields.Many2many(
        'museo.actividad',
        'museo_actividad_trabajador_rel',
        'trabajador_id',
        'actividad_id',
        string='Actividades Asignadas'
    )
    
    # Campos relacionados con convenios
    convenio_ids = fields.One2many(
        'museo.convenio',
        'responsable_museo',
        string='Convenios Responsables'
    )