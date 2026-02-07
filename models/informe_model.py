# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
import json

class MuseoInforme(models.Model):
    _name = 'museo.informe'
    _description = 'Informe Estadístico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_generacion desc'
    
    name = fields.Char(
        string='Nombre del Informe',
        compute='_compute_name',
        store=True
    )
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True,
        ondelete='cascade'
    )
    
    periodo = fields.Selection([
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
        ('personalizado', 'Personalizado'),
    ], string='Período', default='mensual', required=True)
    
    fecha_inicio = fields.Date(
        string='Fecha de Inicio',
        required=True
    )
    
    fecha_fin = fields.Date(
        string='Fecha de Fin',
        required=True
    )
    
    fecha_generacion = fields.Datetime(
        string='Fecha de Generación',
        default=fields.Datetime.now
    )
    
    # Estadísticas principales
    total_actividades = fields.Integer(
        string='Total de Actividades',
        compute='_compute_estadisticas',
        store=True
    )
    
    total_asistentes = fields.Integer(
        string='Total de Asistentes',
        compute='_compute_estadisticas',
        store=True
    )
    
    promedio_asistencia = fields.Float(
        string='Promedio de Asistencia por Actividad',
        compute='_compute_estadisticas',
        store=True,
        digits=(10, 2)
    )
    
    actividades_por_tipo = fields.Text(
        string='Actividades por Tipo',
        compute='_compute_estadisticas',
        store=True
    )
    
    ingresos_totales = fields.Float(
        string='Ingresos Totales',
        compute='_compute_estadisticas',
        store=True,
        digits=(12, 2)
    )
    
    # Métricas específicas
    metricas_especificas = fields.Text(
        string='Métricas Específicas (JSON)',
        compute='_compute_metricas_especificas',
        store=True
    )
    
    # Archivo generado
    archivo_pdf = fields.Binary(
        string='Archivo PDF',
        attachment=True
    )
    
    archivo_pdf_filename = fields.Char(
        string='Nombre del Archivo PDF'
    )
    
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('generado', 'Generado'),
        ('validado', 'Validado'),
        ('publicado', 'Publicado'),
    ], string='Estado', default='borrador', tracking=True)
    
    observaciones = fields.Text(
        string='Observaciones'
    )
    
    @api.depends('museo_id', 'periodo', 'fecha_inicio', 'fecha_fin')
    def _compute_name(self):
        for informe in self:
            periodo_str = dict(informe._fields['periodo'].selection).get(informe.periodo)
            informe.name = f'Informe {periodo_str} - {informe.museo_id.name} - {informe.fecha_inicio} al {informe.fecha_fin}'
    
    @api.depends('museo_id', 'fecha_inicio', 'fecha_fin')
    def _compute_estadisticas(self):
        for informe in self:
            actividades = self.env['museo.actividad'].search([
                ('museo_id', '=', informe.museo_id.id),
                ('fecha_inicio', '>=', informe.fecha_inicio),
                ('fecha_fin', '<=', informe.fecha_fin),
                ('estado', '=', 'realizada'),
            ])
            
            informe.total_actividades = len(actividades)
            informe.total_asistentes = sum(actividades.mapped('asistentes_confirmados'))
            
            if informe.total_actividades > 0:
                informe.promedio_asistencia = informe.total_asistentes / informe.total_actividades
            else:
                informe.promedio_asistencia = 0.0
            
            # Agrupar actividades por tipo
            actividades_por_tipo = {}
            for actividad in actividades:
                tipo = dict(actividad._fields['tipo_actividad'].selection).get(actividad.tipo_actividad)
                actividades_por_tipo[tipo] = actividades_por_tipo.get(tipo, 0) + 1
            
            informe.actividades_por_tipo = json.dumps(actividades_por_tipo, ensure_ascii=False)
            
            # Calcular ingresos
            informe.ingresos_totales = sum(
                actividad.costo * actividad.asistentes_confirmados 
                for actividad in actividades
            )
    
    @api.depends('museo_id', 'fecha_inicio', 'fecha_fin')
    def _compute_metricas_especificas(self):
        for informe in self:
            metricas = {}
            
            # Obtener datos adicionales
            actividades = self.env['museo.actividad'].search([
                ('museo_id', '=', informe.museo_id.id),
                ('fecha_inicio', '>=', informe.fecha_inicio),
                ('fecha_fin', '<=', informe.fecha_fin),
                ('estado', '=', 'realizada'),
            ])
            
            # Calcular métricas por tipo de público
            publico_objetivo = {}
            for actividad in actividades:
                publico = dict(actividad._fields['publico_objetivo'].selection).get(actividad.publico_objetivo)
                publico_objetivo[publico] = publico_objetivo.get(publico, 0) + actividad.asistentes_confirmados
            
            metricas['publico_objetivo'] = publico_objetivo
            
            # Calcular actividades por trabajador
            trabajadores_actividades = {}
            for actividad in actividades:
                for trabajador in actividad.trabajadores_ids:
                    trabajadores_actividades[trabajador.name] = trabajadores_actividades.get(trabajador.name, 0) + 1
            
            metricas['trabajadores_actividades'] = trabajadores_actividades
            
            informe.metricas_especificas = json.dumps(metricas, ensure_ascii=False)
    
    @api.model
    def generar_informe_automatico(self, periodo='mensual'):
        """Genera informes automáticos según el período"""
        hoy = date.today()
        museos = self.env['museo.museo'].search([('active', '=', True)])
        
        for museo in museos:
            if periodo == 'mensual':
                fecha_inicio = hoy.replace(day=1) - timedelta(days=30)
                fecha_fin = hoy.replace(day=1) - timedelta(days=1)
            elif periodo == 'trimestral':
                # Último trimestre completo
                mes_actual = hoy.month
                trimestre_actual = (mes_actual - 1) // 3
                mes_inicio_trimestre = trimestre_actual * 3 + 1
                fecha_inicio = hoy.replace(month=mes_inicio_trimestre-3 if mes_inicio_trimestre > 3 else 10, 
                                          day=1, year=hoy.year-1 if mes_inicio_trimestre <= 3 else hoy.year)
                fecha_fin = hoy.replace(month=mes_inicio_trimestre-1 if mes_inicio_trimestre > 1 else 12,
                                       day=31, year=hoy.year-1 if mes_inicio_trimestre <= 1 else hoy.year)
            elif periodo == 'anual':
                fecha_inicio = hoy.replace(month=1, day=1, year=hoy.year-1)
                fecha_fin = hoy.replace(month=12, day=31, year=hoy.year-1)
            else:
                continue
            
            # Verificar si ya existe un informe para este período
            informe_existente = self.search([
                ('museo_id', '=', museo.id),
                ('periodo', '=', periodo),
                ('fecha_inicio', '=', fecha_inicio),
                ('fecha_fin', '=', fecha_fin),
            ], limit=1)
            
            if not informe_existente:
                informe_vals = {
                    'museo_id': museo.id,
                    'periodo': periodo,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'estado': 'generado',
                }
                self.create(informe_vals)
        
        return True
    
    def action_generar_pdf(self):
        """Genera el archivo PDF del informe"""
        self.ensure_one()
        # Esta función se implementaría en el controlador de reportes
        raise UserError(_('Función de generación de PDF pendiente de implementar'))
    
    def action_validar_informe(self):
        """Valida el informe"""
        self.ensure_one()
        self.estado = 'validado'
        return True
    
    def action_publicar_informe(self):
        """Publica el informe"""
        self.ensure_one()
        self.estado = 'publicado'
        return True
    def action_limpiar_datos_temporales(self):
        """Acción para limpiar datos temporales"""
        fecha_limite = datetime.now() - timedelta(days=30)
        informes_borrador = self.search([
            ('estado', '=', 'borrador'),
            ('fecha_generacion', '<', fecha_limite)
        ])
        
        cantidad = len(informes_borrador)
        informes_borrador.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Limpieza Completada',
                'message': f'Se eliminaron {cantidad} informes en borrador antiguos.',
                'type': 'info',
                'sticky': False,
            }
        }
    
    def action_generar_informes_automaticos(self):
        """Acción para generar informes automáticos"""
        self.generar_informe_automatico('mensual')
        self.generar_informe_automatico('trimestral')
        self.generar_informe_automatico('anual')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Informes Generados',
                'message': 'Los informes automáticos han sido generados exitosamente.',
                'type': 'success',
                'sticky': False,
            }
        }