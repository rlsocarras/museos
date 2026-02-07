# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class MuseoHistoriaBarrio(models.Model):
    _name = 'museo.historia.barrio'
    _description = 'Historia de Barrio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_registro desc, name asc'
    
    name = fields.Char(
        string='Título de la Historia',
        required=True
    )
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True,
        ondelete='cascade'
    )
    
    contenido_historico = fields.Html(
        string='Contenido Histórico',
        sanitize=True,
        required=True
    )
    
    fecha_registro = fields.Date(
        string='Fecha de Registro',
        default=fields.Date.today,
        required=True
    )
    
    barrio = fields.Char(
        string='Barrio/Localidad',
        required=True
    )
    
    ciudad = fields.Char(
        string='Ciudad'
    )
    
    documentacion = fields.Binary(
        string='Documentación',
        attachment=True
    )
    
    documentacion_filename = fields.Char(
        string='Nombre de Archivo'
    )
    
    testimonios = fields.Text(
        string='Testimonios Recopilados'
    )
    
    fuente = fields.Selection([
        ('oral', 'Tradición Oral'),
        ('documental', 'Documental'),
        ('arqueologica', 'Evidencia Arqueológica'),
        ('mixta', 'Fuente Mixta'),
    ], string='Tipo de Fuente', default='mixta')
    
    investigador_responsable = fields.Char(
        string='Investigador Responsable'
    )
    
    estado_investigacion = fields.Selection([
        ('inicial', 'Investigación Inicial'),
        ('avanzada', 'Investigación Avanzada'),
        ('completada', 'Completada'),
        ('publicada', 'Publicada'),
    ], string='Estado de Investigación', default='inicial')
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )