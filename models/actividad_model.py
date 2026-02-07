# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class MuseoActividad(models.Model):
    _name = 'museo.actividad'
    _description = 'Actividad o Evento del Museo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc, name asc'
    
    # Campos de calendario (reemplazan la herencia directa)
    start = fields.Datetime(string='Fecha Inicio', compute='_compute_calendar_fields', store=True)
    stop = fields.Datetime(string='Fecha Fin', compute='_compute_calendar_fields', store=True)
    allday = fields.Boolean(string='Todo el día', default=False)
    name = fields.Char(
        string='Nombre de la Actividad',
        required=True,
        tracking=True
    )
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True,
        ondelete='cascade'
    )
    
    fecha_inicio = fields.Datetime(
        string='Fecha y Hora de Inicio',
        required=True,
        tracking=True
    )
    
    fecha_fin = fields.Datetime(
        string='Fecha y Hora de Finalización',
        required=True,
        tracking=True
    )
    
    tipo_actividad = fields.Selection([
        ('taller', 'Taller'),
        ('conferencia', 'Conferencia'),
        ('exposicion', 'Exposición'),
        ('visita_guiada', 'Visita Guiada'),
        ('actividad_infantil', 'Actividad Infantil'),
        ('evento_especial', 'Evento Especial'),
        ('festival', 'Festival'),
        ('otros', 'Otros'),
    ], string='Tipo de Actividad', default='taller', required=True)
    
    descripcion = fields.Html(
        string='Descripción Detallada',
        sanitize=True,
        required=True
    )
    
    costo = fields.Float(
        string='Costo de Participación',
        digits=(10, 2),
        default=0.0
    )
    
    capacidad_maxima = fields.Integer(
        string='Capacidad Máxima',
        default=50
    )
    
    asistentes_confirmados = fields.Integer(
        string='Asistentes Confirmados',
        compute='_compute_asistentes',
        store=True
    )
    
    estado = fields.Selection([
        ('planificada', 'Planificada'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('pospuesta', 'Pospuesta'),
    ], string='Estado', default='planificada', tracking=True)
    
    trabajadores_ids = fields.Many2many(
        'res.partner',
        'museo_actividad_trabajador_rel',
        'actividad_id',
        'trabajador_id',
        string='Trabajadores Responsables',
        domain="[('is_trabajador_museo', '=', True)]"
    )
    
    registro_asistencia_ids = fields.One2many(
        'museo.registro.asistencia',
        'actividad_id',
        string='Registros de Asistencia'
    )
    
    # Campos relacionados con ubicación
    sala = fields.Char(
        string='Sala/Ubicación'
    )
    
    publico_objetivo = fields.Selection([
        ('infantil', 'Infantil (0-12 años)'),
        ('juvenil', 'Juvenil (13-17 años)'),
        ('adultos', 'Adultos'),
        ('adultos_mayores', 'Adultos Mayores'),
        ('familiar', 'Familiar'),
        ('escolar', 'Escolar'),
        ('universitario', 'Universitario'),
        ('general', 'Público General'),
    ], string='Público Objetivo', default='general')
    
    # Campos calculados
    duracion_horas = fields.Float(
        string='Duración (horas)',
        compute='_compute_duracion',
        store=True
    )
    
    # Campos para integración con calendario
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Evento de Calendario',
        ondelete='cascade'
    )
    
    @api.depends('fecha_inicio', 'fecha_fin')
    def _compute_calendar_fields(self):
        """Calcula campos para integración con calendario"""
        for actividad in self:
            actividad.start = actividad.fecha_inicio
            actividad.stop = actividad.fecha_fin
    
    @api.depends('fecha_inicio', 'fecha_fin')
    def _compute_duracion(self):
        """Calcula la duración en horas"""
        for actividad in self:
            if actividad.fecha_inicio and actividad.fecha_fin:
                delta = actividad.fecha_fin - actividad.fecha_inicio
                actividad.duracion_horas = delta.total_seconds() / 3600
            else:
                actividad.duracion_horas = 0.0
    
    @api.depends('registro_asistencia_ids')
    def _compute_asistentes(self):
        """Calcula el total de asistentes confirmados"""
        for actividad in self:
            actividad.asistentes_confirmados = sum(
                actividad.registro_asistencia_ids.mapped('asistentes')
            )
    
    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas(self):
        """Valida que la fecha de inicio no sea posterior a la de fin"""
        for actividad in self:
            if actividad.fecha_fin and actividad.fecha_inicio > actividad.fecha_fin:
                raise ValidationError(
                    _('La fecha de inicio no puede ser posterior a la fecha de fin.')
                )
    
    @api.constrains('asistentes_confirmados', 'capacidad_maxima')
    def _check_capacidad(self):
        """Valida que los asistentes no superen la capacidad máxima"""
        for actividad in self:
            if actividad.asistentes_confirmados > actividad.capacidad_maxima:
                raise ValidationError(
                    _('Los asistentes confirmados superan la capacidad máxima.')
                )
    
    @api.model
    def create(self, vals):
        """Sobrescribir create para crear evento de calendario"""
        actividad = super(MuseoActividad, self).create(vals)
        
        # Crear evento de calendario asociado
        if actividad.fecha_inicio and actividad.fecha_fin:
            calendar_event = self.env['calendar.event'].create({
                'name': actividad.name,
                'start': actividad.fecha_inicio,
                'stop': actividad.fecha_fin,
                'description': actividad.descripcion,
                'location': actividad.sala,
                'partner_ids': [(6, 0, actividad.trabajadores_ids.ids)],
                'categ_ids': [(6, 0, [self.env.ref('museos.categoria_actividad_museo').id])],
            })
            actividad.calendar_event_id = calendar_event.id
        
        return actividad
    
    def write(self, vals):
        """Sobrescribir write para actualizar evento de calendario"""
        result = super(MuseoActividad, self).write(vals)
        
        # Actualizar evento de calendario si existe
        for actividad in self:
            if actividad.calendar_event_id and any(field in vals for field in ['name', 'fecha_inicio', 'fecha_fin', 'descripcion', 'sala']):
                calendar_vals = {}
                if 'name' in vals:
                    calendar_vals['name'] = vals['name']
                if 'fecha_inicio' in vals:
                    calendar_vals['start'] = vals['fecha_inicio']
                if 'fecha_fin' in vals:
                    calendar_vals['stop'] = vals['fecha_fin']
                if 'descripcion' in vals:
                    calendar_vals['description'] = vals['descripcion']
                if 'sala' in vals:
                    calendar_vals['location'] = vals['sala']
                if 'trabajadores_ids' in vals:
                    calendar_vals['partner_ids'] = [(6, 0, actividad.trabajadores_ids.ids)]
                
                if calendar_vals:
                    actividad.calendar_event_id.write(calendar_vals)
        
        return result
    
    def unlink(self):
        """Sobrescribir unlink para eliminar evento de calendario"""
        # Eliminar eventos de calendario asociados
        for actividad in self:
            if actividad.calendar_event_id:
                actividad.calendar_event_id.unlink()
        
        return super(MuseoActividad, self).unlink()
    
    def action_crear_evento_calendario(self):
        """Acción para crear evento de calendario manualmente"""
        self.ensure_one()
        
        if not self.calendar_event_id:
            calendar_event = self.env['calendar.event'].create({
                'name': self.name,
                'start': self.fecha_inicio,
                'stop': self.fecha_fin,
                'description': self.descripcion,
                'location': self.sala,
                'partner_ids': [(6, 0, self.trabajadores_ids.ids)],
                'categ_ids': [(6, 0, [self.env.ref('museos.categoria_actividad_museo').id])],
            })
            self.calendar_event_id = calendar_event.id
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'calendar.event',
                'res_id': calendar_event.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_res_model': 'museo.actividad', 'default_res_id': self.id}
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'res_id': self.calendar_event_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_abrir_calendario(self):
        """Acción para abrir vista de calendario"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Calendario de Actividades',
            'res_model': 'calendar.event',
            'view_mode': 'calendar',
            'target': 'current',
            'domain': [('id', '=', self.calendar_event_id.id)],
            'context': {
                'search_default_museo_id': self.museo_id.id,
                'default_res_model': 'museo.actividad',
                'default_res_id': self.id
            }
        }