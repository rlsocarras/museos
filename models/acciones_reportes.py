# ARCHIVO: acciones_reportes.py
######################################################################

# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MuseoAccionesReportes(models.Model):
    _inherit = 'museo.museo'
    
    def action_abrir_reportes(self):
        """Abre la vista de reportes del museo"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Reportes - {self.name}',
            'res_model': 'museo.reporte',
            'view_mode': 'tree,form',
            'domain': [('museo_id', '=', self.id)],
            'context': {
                'default_museo_id': self.id,
                'search_default_museo_id': self.id
            }
        }
    
    def action_reporte_actividades_trabajador(self):
        """Abre wizard para reporte de actividades por trabajador"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Reporte Actividades por Trabajador - {self.name}',
            'res_model': 'museo.wizard.reporte.rapido',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_museo_id': self.id,
                'default_tipo_reporte': 'actividades_trabajador',
            }
        }
    
    def action_reporte_actividades_fechas(self):
        """Abre wizard para reporte de actividades por fechas"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Reporte Actividades por Fechas - {self.name}',
            'res_model': 'museo.wizard.reporte.rapido',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_museo_id': self.id,
                'default_tipo_reporte': 'actividades_fechas',
            }
        }
    
    def action_reporte_rapido_mes_actual(self):
        """Genera reporte rápido del mes actual"""
        self.ensure_one()
        
        hoy = fields.Date.today()
        primer_dia_mes = hoy.replace(day=1)
        ultimo_dia_mes = (hoy.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Crear reporte automático
        nombre = f"Reporte Mensual - {self.name} - {hoy.strftime('%B %Y')}"
        
        reporte = self.env['museo.reporte'].create({
            'name': nombre,
            'tipo_reporte': 'actividades_fechas',
            'museo_id': self.id,
            'fecha_desde': primer_dia_mes,
            'fecha_hasta': ultimo_dia_mes,
            'estado_actividad': 'realizada',
        })
        
        reporte.action_generar_reporte()
        
        return {
            'type': 'ir.actions.act_window',
            'name': nombre,
            'res_model': 'museo.reporte',
            'res_id': reporte.id,
            'view_mode': 'form',
            'target': 'current',
        }