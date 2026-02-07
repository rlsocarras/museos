# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class MuseoConvenio(models.Model):
    _name = 'museo.convenio'
    _description = 'Convenio de Trabajo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc, name asc'
    
    name = fields.Char(
        string='Nombre del Convenio',
        required=True,
        tracking=True
    )
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True,
        ondelete='cascade'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Institución/Entidad',
        required=False,
        domain="[('is_company', '=', True)]"
    )
    
    fecha_inicio = fields.Date(
        string='Fecha de Inicio',
        required=True,
        tracking=True
    )
    
    fecha_fin = fields.Date(
        string='Fecha de Finalización',
        tracking=True
    )
    
    tipo_convenio = fields.Selection([
        ('investigacion', 'Investigación'),
        ('educacion', 'Educación'),
        ('cultural', 'Intercambio Cultural'),
        ('tecnico', 'Cooperación Técnica'),
        ('financiero', 'Financiero'),
        ('otros', 'Otros'),
    ], string='Tipo de Convenio', default='cultural', required=True)
    
    descripcion = fields.Html(
        string='Descripción del Convenio',
        sanitize=True
    )
    
    objetivos = fields.Text(
        string='Objetivos Específicos'
    )
    
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('vigente', 'Vigente'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
        ('renovado', 'Renovado'),
    ], string='Estado', default='borrador', tracking=True)
    
    documento = fields.Binary(
        string='Documento del Convenio',
        attachment=True
    )
    
    documento_filename = fields.Char(
        string='Nombre del Documento'
    )
    
    responsable_museo = fields.Many2one(
        'res.partner',
        string='Responsable por el Museo',
        domain="[('is_trabajador_museo', '=', True)]"
    )
    
    monto = fields.Float(
        string='Monto del Convenio',
        digits=(12, 2)
    )
    
    observaciones = fields.Text(
        string='Observaciones')
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    

    """ ---------------- """
    
    dias_para_vencer = fields.Integer(
        string='Días para Vencer',
        compute='_compute_dias_para_vencer',
        store=False
    )
    
    @api.depends('fecha_fin')
    def _compute_dias_para_vencer(self):
        hoy = fields.Date.today()
        for convenio in self:
            if convenio.fecha_fin and convenio.estado == 'vigente':
                convenio.dias_para_vencer = (convenio.fecha_fin - hoy).days
            else:
                convenio.dias_para_vencer = 0
    """ ---------------- """
    
    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas(self):
        for convenio in self:
            if convenio.fecha_fin and convenio.fecha_inicio > convenio.fecha_fin:
                raise ValidationError(
                    _('La fecha de inicio no puede ser posterior a la fecha de fin.')
                )
    
    @api.model
    def _cron_verificar_vencimientos(self):
        hoy = date.today()
        convenios = self.search([
            ('estado', '=', 'vigente'),
            ('fecha_fin', '!=', False),
            ('active', '=', True)
        ])
        
        for convenio in convenios:
            if convenio.fecha_fin < hoy:
                convenio.estado = 'vencido'
                _logger.info(f'Convenio {convenio.name} marcado como vencido')