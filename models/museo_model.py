# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class MuseoMuseo(models.Model):
    _name = 'museo.museo'
    _description = 'Museo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    
    name = fields.Char(
        string='Nombre del Museo',
        required=True,
        tracking=True
    )

    # FOTO PRINCIPAL - Campo para la imagen principal
    imagen_principal = fields.Binary(
        string='Foto Principal',
        attachment=True,
        help='Imagen principal del museo para mostrar en listados y perfiles'
    )

    # GALERÍA DE FOTOS - Campo para múltiples imágenes
    galeria_ids = fields.One2many(
        'museo.museo.galeria',
        'museo_id',
        string='Galería de Fotos'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    fecha_creacion = fields.Date(
        string='Fecha de Creación',
        required=True,
        tracking=True
    )
    
    resenna_historica = fields.Html(
        string='Reseña Histórica',
        sanitize=True
    )
    
    direccion = fields.Text(
        string='Dirección Completa'
    )
    
    telefono = fields.Char(
        string='Teléfono'
    )
    
    email = fields.Char(
        string='Email'
    )
    
    website = fields.Char(
        string='Sitio Web'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    # Campos relacionados
    objeto_ids = fields.One2many(
        'museo.objeto',
        'museo_id',
        string='Objetos'
    )
    
    historia_barrio_ids = fields.One2many(
        'museo.historia.barrio',
        'museo_id',
        string='Historias de Barrios'
    )
    
    convenio_ids = fields.One2many(
        'museo.convenio',
        'museo_id',
        string='Convenios'
    )
    
    actividad_ids = fields.One2many(
        'museo.actividad',
        'museo_id',
        string='Actividades'
    )
    
    informe_ids = fields.One2many(
        'museo.informe',
        'museo_id',
        string='Informes Estadísticos'
    )
    
    # Campos calculados
    total_objetos = fields.Integer(
        string='Total de Objetos',
        compute='_compute_totales',
        store=True
    )
    
    total_actividades = fields.Integer(
        string='Total de Actividades',
        compute='_compute_totales',
        store=True
    )
    
    total_convenios = fields.Integer(
        string='Total de Convenios',
        compute='_compute_totales',
        store=True
    )

     # Campos calculados para dashboard
    informes_publicados = fields.Integer(
        string='Informes Publicados',
        compute='_compute_informes_publicados',
        store=False
    )
    
    # Agregar campos para convenios
    convenios_por_vencer_count = fields.Integer(
        string='Convenios por Vencer',
        compute='_compute_convenios_por_vencer',
        store=False
    )
    
    actividades_proximas_count = fields.Integer(
        string='Actividades Próximas',
        compute='_compute_actividades_proximas',
        store=False
    )
    
    @api.depends('informe_ids')
    def _compute_informes_publicados(self):
        for museo in self:
            museo.informes_publicados = len(museo.informe_ids.filtered(
                lambda r: r.periodo == 'mensual' and r.estado == 'publicado'
            ))
    
    @api.depends('convenio_ids')
    def _compute_convenios_por_vencer(self):
        hoy = fields.Date.today()
        for museo in self:
            museo.convenios_por_vencer_count = len(museo.convenio_ids.filtered(
                lambda r: r.estado == 'vigente' 
                and r.fecha_fin 
                and (r.fecha_fin - hoy).days <= 30
            ))
    
    @api.depends('actividad_ids')
    def _compute_actividades_proximas(self):
        hoy = fields.Date.today()
        for museo in self:
            museo.actividades_proximas_count = len(museo.actividad_ids.filtered(
                lambda r: r.estado in ['planificada', 'confirmada'] 
                and r.fecha_inicio 
                and r.fecha_inicio.date() >= hoy
            ))
    
    # Métodos de acción para el dashboard
    def action_view_objetos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Objetos del Museo',
            'res_model': 'museo.objeto',
            'view_mode': 'kanban,list,form',
            'domain': [('museo_id', '=', self.id)],
            'context': {'default_museo_id': self.id}
        }
    
    def action_view_actividades(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Actividades del Museo',
            'res_model': 'museo.actividad',
            'view_mode': 'kanban,list,calendar,form',
            'domain': [('museo_id', '=', self.id)],
            'context': {'default_museo_id': self.id}
        }
    
    def action_view_convenios(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Convenios del Museo',
            'res_model': 'museo.convenio',
            'view_mode': 'kanban,list,form',
            'domain': [('museo_id', '=', self.id)],
            'context': {'default_museo_id': self.id}
        }
    
    def action_view_informes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Informes del Museo',
            'res_model': 'museo.informe',
            'view_mode': 'list,form',
            'domain': [('museo_id', '=', self.id)],
            'context': {'default_museo_id': self.id}
        }
    
    def action_view_galeria(self):
        """Acción para ver la galería de fotos del museo"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Galería de Fotos - {self.name}',
            'res_model': 'museo.museo.galeria',
            'view_mode': 'kanban,form',
            'domain': [('museo_id', '=', self.id)],
            'context': {
                'default_museo_id': self.id,
                'search_default_museo_id': self.id
            }
        }
    
    @api.depends('objeto_ids', 'actividad_ids', 'convenio_ids')
    def _compute_totales(self):
        for museo in self:
            museo.total_objetos = len(museo.objeto_ids)
            museo.total_actividades = len(museo.actividad_ids)
            museo.total_convenios = len(museo.convenio_ids)
    
    @api.constrains('fecha_creacion')
    def _check_fecha_creacion(self):
        for museo in self:
            if museo.fecha_creacion and museo.fecha_creacion > date.today():
                raise ValidationError(
                    _('La fecha de creación no puede ser futura.')
                )
         
    def action_ver_pagina_web(self):
        """Acción para abrir la página web del museo"""
        self.ensure_one()
        
        # Verificar si el módulo website está instalado
        if self.env['ir.module.module'].search([('name', '=', 'website'), ('state', '=', 'installed')]):
            # Construir la URL de la landing page
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            museo_url = f"{base_url}/museos/{self.id}"
            
            # Abrir en nueva pestaña
            return {
                'type': 'ir.actions.act_url',
                'url': museo_url,
                'target': 'new',
            }
        else:
            # Si website no está instalado, mostrar advertencia
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Módulo Website Requerido',
                    'message': 'El módulo Website no está instalado. Instálelo para acceder a las páginas web de los museos.',
                    'type': 'warning',
                    'sticky': True,
                }
            }
       