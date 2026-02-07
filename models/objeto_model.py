# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MuseoObjeto(models.Model):
    _name = 'museo.objeto'
    _description = 'Objeto del Museo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    
    name = fields.Char(
        string='Nombre del Objeto',
        required=True,
        tracking=True
    )
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True,
        ondelete='cascade'
    )
    
    codigo_inventario = fields.Char(
        string='Código de Inventario',
        required=True,
        unique=True,
        tracking=True
    )
    
    historia = fields.Html(
        string='Historia del Objeto',
        sanitize=True,
        required=True
    )
    
    fecha_adquisicion = fields.Date(
        string='Fecha de Adquisición',
        tracking=True
    )
    
    estado_conservacion = fields.Selection([
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
        ('restauracion', 'En Restauración'),
    ], string='Estado de Conservación', default='bueno')
    
    ubicacion_actual = fields.Char(
        string='Ubicación Actual'
    )
    
    valor_estimado = fields.Float(
        string='Valor Estimado',
        digits=(12, 2)
    )
    
    imagen = fields.Binary(
        string='Imagen',
        attachment=True
    )
    
    imagen_filename = fields.Char(
        string='Nombre de Archivo de Imagen'
    )
    
    categoria = fields.Selection([
        ('arqueologico', 'Arqueológico'),
        ('historico', 'Histórico'),
        ('artistico', 'Artístico'),
        ('etnografico', 'Etnográfico'),
        ('cientifico', 'Científico'),
        ('otros', 'Otros'),
    ], string='Categoría', default='otros')
    
    observaciones = fields.Text(
        string='Observaciones'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )