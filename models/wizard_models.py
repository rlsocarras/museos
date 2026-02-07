# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta
import base64
import json

class MuseoWizardGenerarInforme(models.TransientModel):
    _name = 'museo.wizard.generar.informe'
    _description = 'Wizard para Generación Rápida de Informes'
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True
    )
    
    periodo = fields.Selection([
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
        ('personalizado', 'Personalizado'),
    ], string='Período', default='mensual', required=True)
    
    fecha_inicio = fields.Date(
        string='Fecha de Inicio',
        required=True,
        default=fields.Date.today().replace(day=1)
    )
    
    fecha_fin = fields.Date(
        string='Fecha de Fin',
        required=True,
        default=fields.Date.today()
    )
    
    incluir_graficos = fields.Boolean(
        string='Incluir Gráficos',
        default=True
    )
    
    incluir_detalles = fields.Boolean(
        string='Incluir Detalles por Actividad',
        default=True
    )
    
    formato_exportacion = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('ambos', 'PDF y Excel'),
    ], string='Formato de Exportación', default='pdf')
    
    enviar_email = fields.Boolean(
        string='Enviar por Email',
        default=False
    )
    
    email_destinatario = fields.Char(
        string='Email Destinatario'
    )
    
    opciones_avanzadas = fields.One2many(
        'museo.wizard.opcion.avanzada',
        'wizard_id',
        string='Opciones Avanzadas'
    )
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        
        # Obtener el primer museo activo por defecto
        museo = self.env['museo.museo'].search([('active', '=', True)], limit=1)
        if museo:
            res['museo_id'] = museo.id
        
        # Configurar fechas por defecto para el mes actual
        hoy = date.today()
        res['fecha_inicio'] = hoy.replace(day=1)
        res['fecha_fin'] = hoy
        
        return res
    
    def action_generar(self):
        self.ensure_one()
        
        # Validar fechas
        if self.fecha_inicio > self.fecha_fin:
            raise UserError(_('La fecha de inicio no puede ser posterior a la fecha de fin.'))
        
        # Crear el informe
        informe_vals = {
            'museo_id': self.museo_id.id,
            'periodo': self.periodo,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
            'estado': 'generado',
        }
        
        informe = self.env['museo.informe'].create(informe_vals)
        
        # Preparar mensaje de éxito
        message = f'Informe generado exitosamente: {informe.name}'
        
        if self.enviar_email and self.email_destinatario:
            # Lógica para enviar email
            message += f'\nSe enviará a: {self.email_destinatario}'
        
        # Mostrar notificación
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Informe Generado',
                'message': message,
                'type': 'success',
                'sticky': True,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'museo.informe',
                    'res_id': informe.id,
                    'views': [(False, 'form')],
                }
            }
        }
    
    def action_cancelar(self):
        return {'type': 'ir.actions.act_window_close'}

class MuseoWizardOpcionAvanzada(models.TransientModel):
    _name = 'museo.wizard.opcion.avanzada'
    _description = 'Opciones Avanzadas para Generación de Informes'
    
    wizard_id = fields.Many2one(
        'museo.wizard.generar.informe',
        string='Wizard'
    )
    
    tipo_dato = fields.Selection([
        ('actividades', 'Actividades'),
        ('asistentes', 'Asistentes'),
        ('ingresos', 'Ingresos'),
        ('satisfaccion', 'Satisfacción'),
        ('trabajadores', 'Trabajadores'),
        ('publico', 'Público Objetivo'),
    ], string='Tipo de Dato', required=True)
    
    incluir = fields.Boolean(
        string='Incluir',
        default=True
    )
    
    nivel_detalle = fields.Selection([
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ], string='Nivel de Detalle', default='intermedio')

class MuseoWizardImportarObjetos(models.TransientModel):
    _name = 'museo.wizard.importar.objetos'
    _description = 'Wizard para Importación Masiva de Objetos'
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True
    )
    
    archivo = fields.Binary(
        string='Archivo a Importar',
        required=True
    )
    
    formato_archivo = fields.Selection([
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ], string='Formato del Archivo', default='excel', required=True)
    
    sobrescribir_existentes = fields.Boolean(
        string='Sobrescribir Objetos Existentes',
        default=False
    )
    
    validar_duplicados = fields.Boolean(
        string='Validar Duplicados',
        default=True
    )
    
    crear_categorias = fields.Boolean(
        string='Crear Categorías Automáticamente',
        default=True
    )
    
    mapeo_campos = fields.One2many(
        'museo.wizard.mapeo.campo',
        'wizard_id',
        string='Mapeo de Campos'
    )
    
    def action_importar(self):
        self.ensure_one()
        raise UserError(_('Función de importación pendiente de implementar'))
    
    def action_cancelar(self):
        return {'type': 'ir.actions.act_window_close'}

class MuseoWizardMapeoCampo(models.TransientModel):
    _name = 'museo.wizard.mapeo.campo'
    _description = 'Mapeo de Campos para Importación'
    
    wizard_id = fields.Many2one(
        'museo.wizard.importar.objetos',
        string='Wizard'
    )
    
    campo_archivo = fields.Char(
        string='Campo en Archivo',
        required=True
    )
    
    campo_sistema = fields.Selection([
        ('name', 'Nombre'),
        ('codigo_inventario', 'Código de Inventario'),
        ('historia', 'Historia'),
        ('categoria', 'Categoría'),
        ('estado_conservacion', 'Estado de Conservación'),
        ('valor_estimado', 'Valor Estimado'),
        ('ubicacion_actual', 'Ubicación Actual'),
    ], string='Campo en Sistema', required=True)
    
    formato = fields.Selection([
        ('texto', 'Texto'),
        ('numero', 'Número'),
        ('fecha', 'Fecha'),
        ('moneda', 'Moneda'),
    ], string='Formato', default='texto')
    
    requerido = fields.Boolean(
        string='Requerido',
        default=False
    )

class MuseoWizardAsignarTrabajadores(models.TransientModel):
    _name = 'museo.wizard.asignar.trabajadores'
    _description = 'Wizard para Asignación Masiva de Trabajadores'
    
    actividad_ids = fields.Many2many(
        'museo.actividad',
        string='Actividades',
        required=True
    )
    
    trabajadores_ids = fields.Many2many(
        'res.partner',
        string='Trabajadores',
        required=True,
        domain="[('is_trabajador_museo', '=', True)]"
    )
    
    fecha_desde = fields.Date(
        string='Fecha Desde',
        widget="date"
    )
    
    fecha_hasta = fields.Date(
        string='Fecha Hasta',
        widget="date"
    )
    
    tipo_asignacion = fields.Selection([
        ('agregar', 'Agregar a existentes'),
        ('reemplazar', 'Reemplazar existentes'),
        ('rotar', 'Rotación semanal'),
    ], string='Tipo de Asignación', default='agregar', required=True)
    
    limitar_horas = fields.Boolean(
        string='Limitar Horas Semanales',
        default=False
    )
    
    maximo_horas_semanales = fields.Float(
        string='Máximo Horas Semanales',
        default=40.0
    )
    
    notificar_trabajadores = fields.Boolean(
        string='Notificar a Trabajadores',
        default=True
    )
    
    previsualizacion_asignaciones = fields.One2many(
        'museo.wizard.previsualizacion.asignacion',
        'wizard_id',
        string='Previsualización'
    )
    
    def action_asignar(self):
        self.ensure_one()
        raise UserError(_('Función de asignación pendiente de implementar'))
    
    def action_cancelar(self):
        return {'type': 'ir.actions.act_window_close'}

class MuseoWizardPrevisualizacionAsignacion(models.TransientModel):
    _name = 'museo.wizard.previsualizacion.asignacion'
    _description = 'Previsualización de Asignaciones'
    
    wizard_id = fields.Many2one(
        'museo.wizard.asignar.trabajadores',
        string='Wizard'
    )
    
    actividad = fields.Char(
        string='Actividad'
    )
    
    trabajador = fields.Char(
        string='Trabajador'
    )
    
    horas_asignadas = fields.Float(
        string='Horas Asignadas'
    )
    
    conflicto = fields.Boolean(
        string='Conflicto'
    )