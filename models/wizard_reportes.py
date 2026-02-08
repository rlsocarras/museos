# ARCHIVO: wizard_reportes.py
######################################################################

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class MuseoWizardReporteRapido(models.TransientModel):
    _name = 'museo.wizard.reporte.rapido'
    _description = 'Wizard para Reportes Rápidos'
    
    tipo_reporte = fields.Selection([
        ('actividades_trabajador', 'Actividades por Trabajador'),
        ('actividades_fechas', 'Actividades por Rango de Fechas'),
    ], string='Tipo de Reporte', required=True, default='actividades_trabajador')
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True
    )
    
    rango_fechas = fields.Selection([
        ('hoy', 'Hoy'),
        ('semana_actual', 'Esta Semana'),
        ('mes_actual', 'Este Mes'),
        ('mes_anterior', 'Mes Anterior'),
        ('trimestre_actual', 'Este Trimestre'),
        ('personalizado', 'Personalizado'),
    ], string='Rango de Fechas', default='mes_actual', required=True)
    
    fecha_desde = fields.Date(string='Fecha Desde')
    fecha_hasta = fields.Date(string='Fecha Hasta')
    
    # Filtros adicionales para actividades por trabajador
    trabajador_ids = fields.Many2many(
        'res.partner',
        string='Trabajadores Específicos',
        domain="[('is_trabajador_museo', '=', True)]",
        help="Dejar vacío para incluir todos los trabajadores"
    )
    
    tipo_actividad = fields.Selection([
        ('todos', 'Todos los Tipos'),
        ('taller', 'Taller'),
        ('conferencia', 'Conferencia'),
        ('exposicion', 'Exposición'),
        ('visita_guiada', 'Visita Guiada'),
        ('actividad_infantil', 'Actividad Infantil'),
        ('evento_especial', 'Evento Especial'),
        ('festival', 'Festival'),
        ('otros', 'Otros'),
    ], string='Filtrar por Tipo', default='todos')
    
    estado_actividad = fields.Selection([
        ('todos', 'Todos los Estados'),
        ('planificada', 'Planificada'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('pospuesta', 'Pospuesta'),
    ], string='Filtrar por Estado', default='realizada')
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        hoy = fields.Date.today()
        
        # Configurar fechas por defecto para el mes actual
        primer_dia_mes = hoy.replace(day=1)
        ultimo_dia_mes = (hoy.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        res['fecha_desde'] = primer_dia_mes
        res['fecha_hasta'] = ultimo_dia_mes
        
        # Obtener el primer museo activo
        museo = self.env['museo.museo'].search([('active', '=', True)], limit=1)
        if museo:
            res['museo_id'] = museo.id
        
        return res
    
    @api.onchange('rango_fechas')
    def _onchange_rango_fechas(self):
        hoy = fields.Date.today()
        
        if self.rango_fechas == 'hoy':
            self.fecha_desde = hoy
            self.fecha_hasta = hoy
        elif self.rango_fechas == 'semana_actual':
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            fin_semana = inicio_semana + timedelta(days=6)
            self.fecha_desde = inicio_semana
            self.fecha_hasta = fin_semana
        elif self.rango_fechas == 'mes_actual':
            primer_dia_mes = hoy.replace(day=1)
            ultimo_dia_mes = (hoy.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            self.fecha_desde = primer_dia_mes
            self.fecha_hasta = ultimo_dia_mes
        elif self.rango_fechas == 'mes_anterior':
            primer_dia_mes_anterior = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
            ultimo_dia_mes_anterior = hoy.replace(day=1) - timedelta(days=1)
            self.fecha_desde = primer_dia_mes_anterior
            self.fecha_hasta = ultimo_dia_mes_anterior
        elif self.rango_fechas == 'trimestre_actual':
            mes_actual = hoy.month
            trimestre_actual = (mes_actual - 1) // 3
            mes_inicio_trimestre = trimestre_actual * 3 + 1
            primer_dia_trimestre = hoy.replace(month=mes_inicio_trimestre, day=1)
            mes_fin_trimestre = mes_inicio_trimestre + 2
            ultimo_dia_trimestre = (hoy.replace(month=mes_fin_trimestre, day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            self.fecha_desde = primer_dia_trimestre
            self.fecha_hasta = ultimo_dia_trimestre
    
    def action_generar_reporte(self):
        """Genera el reporte rápido"""
        self.ensure_one()
        
        # Validar fechas
        if not self.fecha_desde or not self.fecha_hasta:
            raise UserError(_('Debe especificar las fechas del reporte'))
        
        if self.fecha_desde > self.fecha_hasta:
            raise UserError(_('La fecha "Desde" no puede ser posterior a la fecha "Hasta"'))
        
        # Crear nombre del reporte
        nombre_reporte = f"Reporte {dict(self._fields['tipo_reporte'].selection).get(self.tipo_reporte)}"
        nombre_reporte += f" - {self.museo_id.name}"
        nombre_reporte += f" - {self.fecha_desde} al {self.fecha_hasta}"
        
        # Crear el reporte
        reporte_vals = {
            'name': nombre_reporte,
            'tipo_reporte': self.tipo_reporte,
            'museo_id': self.museo_id.id,
            'fecha_desde': self.fecha_desde,
            'fecha_hasta': self.fecha_hasta,
            'tipo_actividad': self.tipo_actividad,
            'estado_actividad': self.estado_actividad,
        }
        
        if self.trabajador_ids and self.tipo_reporte == 'actividades_trabajador':
            reporte_vals['trabajador_ids'] = [(6, 0, self.trabajador_ids.ids)]
        
        reporte = self.env['museo.reporte'].create(reporte_vals)
        
        # Generar el reporte
        reporte.action_generar_reporte()
        
        # Abrir el reporte generado
        return {
            'type': 'ir.actions.act_window',
            'name': nombre_reporte,
            'res_model': 'museo.reporte',
            'res_id': reporte.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_generar_y_exportar(self):
        """Genera el reporte y lo exporta a PDF"""
        self.ensure_one()
    
        # Primero generar el reporte
        action = self.action_generar_reporte()
    
        # Luego exportar a PDF
        reporte_id = action.get('res_id')
        if reporte_id:
            reporte = self.env['museo.reporte'].browse(reporte_id)
            return reporte.action_exportar_pdf()
    
        return action
    

    

class MuseoWizardReporteActividadesTrabajador(models.TransientModel):
    _name = 'museo.wizard.reporte.actividades.trabajador'
    _description = 'Wizard Específico para Reporte de Actividades por Trabajador'
    
    @api.model
    def _get_trabajadores_default(self):
        return self.env['res.partner'].search([
            ('is_trabajador_museo', '=', True),
            ('active', '=', True),
        ], limit=10)
    
    trabajador_ids = fields.Many2many(
        'res.partner',
        string='Trabajadores',
        domain="[('is_trabajador_museo', '=', True)]",
        default=_get_trabajadores_default,
        required=True
    )
    
    fecha_desde = fields.Date(
        string='Fecha Desde',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    fecha_hasta = fields.Date(
        string='Fecha Hasta',
        required=True,
        default=fields.Date.today
    )
    
    incluir_detalles = fields.Boolean(
        string='Incluir Detalles por Actividad',
        default=True
    )
    
    agrupar_por = fields.Selection([
        ('trabajador', 'Por Trabajador'),
        ('semana', 'Por Semana'),
        ('mes', 'Por Mes'),
        ('tipo_actividad', 'Por Tipo de Actividad'),
    ], string='Agrupar Por', default='trabajador')
    
    def action_generar_reporte(self):
        """Genera reporte específico de actividades por trabajador"""
        self.ensure_one()
        
        # Aquí implementarías la lógica específica para este reporte
        # Por ahora, usamos el wizard general
        wizard_general = self.env['museo.wizard.reporte.rapido'].create({
            'tipo_reporte': 'actividades_trabajador',
            'museo_id': self.env.context.get('default_museo_id', False),
            'rango_fechas': 'personalizado',
            'fecha_desde': self.fecha_desde,
            'fecha_hasta': self.fecha_hasta,
            'trabajador_ids': [(6, 0, self.trabajador_ids.ids)],
        })
        
        return wizard_general.action_generar_reporte()