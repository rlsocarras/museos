# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MuseoRegistroAsistencia(models.Model):
    _name = 'museo.registro.asistencia'
    _description = 'Registro de Asistencia a Actividades'
    _order = 'fecha desc'
    
    actividad_id = fields.Many2one(
        'museo.actividad',
        string='Actividad',
        required=True,
        ondelete='cascade'
    )
    
    fecha = fields.Date(
        string='Fecha de Registro',
        default=fields.Date.today,
        required=True
    )
    
    asistentes = fields.Integer(
        string='Número de Asistentes',
        required=True,
        default=1
    )
    
    grupo_edad = fields.Selection([
        ('0-12', '0-12 años'),
        ('13-17', '13-17 años'),
        ('18-25', '18-25 años'),
        ('26-40', '26-40 años'),
        ('41-60', '41-60 años'),
        ('61+', '61+ años'),
        ('mixto', 'Mixto'),
    ], string='Grupo de Edad', default='mixto')
    
    origen = fields.Selection([
        ('local', 'Local'),
        ('nacional', 'Nacional'),
        ('internacional', 'Internacional'),
        ('escolar', 'Grupo Escolar'),
        ('universitario', 'Grupo Universitario'),
        ('turista', 'Turista'),
        ('otros', 'Otros'),
    ], string='Origen', default='local')
    
    satisfaccion = fields.Float(
        string='Nivel de Satisfacción (1-5)',
        digits=(2, 1),
        help="Calificación de 1 a 5 estrellas"
    )
    
    comentarios = fields.Text(
        string='Comentarios Adicionales'
    )
    
    # Campos calculados
    actividad_nombre = fields.Char(
        string='Nombre de Actividad',
        related='actividad_id.name',
        store=True
    )
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        related='actividad_id.museo_id',
        store=True
    )
    
    @api.constrains('asistentes')
    def _check_asistentes(self):
        for registro in self:
            if registro.asistentes < 1:
                raise ValidationError(
                    _('El número de asistentes debe ser al menos 1.')
                )
    
    @api.constrains('satisfaccion')
    def _check_satisfaccion(self):
        for registro in self:
            if registro.satisfaccion and (registro.satisfaccion < 1 or registro.satisfaccion > 5):
                raise ValidationError(
                    _('La satisfacción debe estar entre 1 y 5.')
                )