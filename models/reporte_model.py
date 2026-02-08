import base64
import io
import json
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MuseoReporte(models.Model):
    _name = 'museo.reporte'
    _description = 'Reportes Personalizados del Museo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string='Nombre del Reporte',
        required=True,
        tracking=True
    )
    
    tipo_reporte = fields.Selection([
        ('actividades_trabajador', 'Actividades por Trabajador'),
        ('actividades_fechas', 'Actividades por Rango de Fechas'),
        ('asistencia', 'Reporte de Asistencia'),
        ('convenios', 'Reporte de Convenios'),
        ('objetos', 'Inventario de Objetos'),
    ], string='Tipo de Reporte', required=True, default='actividades_trabajador')
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
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
        default=lambda self: fields.Date.today()  # Hoy
    )
    
    # Filtros específicos
    trabajador_ids = fields.Many2many(
        'res.partner',
        string='Trabajadores',
        domain="[('is_trabajador_museo', '=', True)]"
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
    ], string='Tipo de Actividad', default='todos')
    
    estado_actividad = fields.Selection([
        ('todos', 'Todos los Estados'),
        ('planificada', 'Planificada'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('pospuesta', 'Pospuesta'),
    ], string='Estado de Actividad', default='todos')
    
    # Resultados del reporte
    datos_reportes = fields.Text(
        string='Datos del Reporte (JSON)',
        compute='_compute_datos_reportes',
        store=True
    )
    
    archivo_pdf = fields.Binary(
        string='Archivo PDF',
        attachment=True
    )
    
    archivo_excel = fields.Binary(
        string='Archivo Excel',
        attachment=True
    )
    
    archivo_pdf_filename = fields.Char(string='Nombre PDF')
    archivo_excel_filename = fields.Char(string='Nombre Excel')
    
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('generado', 'Generado'),
        ('exportado', 'Exportado'),
    ], string='Estado', default='borrador')
    
    observaciones = fields.Text(string='Observaciones')
    
    @api.depends('tipo_reporte', 'museo_id', 'fecha_desde', 'fecha_hasta', 
                 'trabajador_ids', 'tipo_actividad', 'estado_actividad')
    def _compute_datos_reportes(self):
        """Calcula los datos del reporte según los filtros seleccionados"""
        for reporte in self:
            datos = {}
            
            if reporte.tipo_reporte == 'actividades_trabajador':
                datos = self._generar_reporte_actividades_trabajador(reporte)
            elif reporte.tipo_reporte == 'actividades_fechas':
                datos = self._generar_reporte_actividades_fechas(reporte)
            
            reporte.datos_reportes = json.dumps(datos, ensure_ascii=False)
    
    def _generar_reporte_actividades_trabajador(self, reporte):
        """Genera reporte de actividades por trabajador"""
        # Construir dominio base
        dominio = [
            ('museo_id', '=', reporte.museo_id.id),
            ('fecha_inicio', '>=', reporte.fecha_desde),
            ('fecha_fin', '<=', reporte.fecha_hasta),
        ]
        
        # Aplicar filtros adicionales
        if reporte.tipo_actividad != 'todos':
            dominio.append(('tipo_actividad', '=', reporte.tipo_actividad))
        
        if reporte.estado_actividad != 'todos':
            dominio.append(('estado', '=', reporte.estado_actividad))
        
        # Obtener actividades
        actividades = self.env['museo.actividad'].search(dominio)
        
        # Agrupar por trabajador
        trabajadores_data = {}
        for actividad in actividades:
            for trabajador in actividad.trabajadores_ids:
                if trabajador.id not in trabajadores_data:
                    trabajadores_data[trabajador.id] = {
                        'nombre': trabajador.name,
                        'cargo': trabajador.cargo or '',
                        'actividades': [],
                        'total_actividades': 0,
                        'total_horas': 0,
                        'total_asistentes': 0,
                    }
                
                trabajadores_data[trabajador.id]['actividades'].append({
                    'nombre': actividad.name,
                    'fecha': actividad.fecha_inicio.strftime('%d/%m/%Y %H:%M'),
                    'tipo': dict(actividad._fields['tipo_actividad'].selection).get(actividad.tipo_actividad),
                    'estado': dict(actividad._fields['estado'].selection).get(actividad.estado),
                    'duracion_horas': actividad.duracion_horas,
                    'asistentes': actividad.asistentes_confirmados,
                    'capacidad': actividad.capacidad_maxima,
                    'sala': actividad.sala or '',
                })
                
                trabajadores_data[trabajador.id]['total_actividades'] += 1
                trabajadores_data[trabajador.id]['total_horas'] += actividad.duracion_horas
                trabajadores_data[trabajador.id]['total_asistentes'] += actividad.asistentes_confirmados
        
        # Ordenar por total de actividades (descendente)
        trabajadores_ordenados = sorted(
            trabajadores_data.values(),
            key=lambda x: x['total_actividades'],
            reverse=True
        )
        
        # Estadísticas generales
        estadisticas = {
            'periodo': f"{reporte.fecha_desde} al {reporte.fecha_hasta}",
            'total_trabajadores': len(trabajadores_ordenados),
            'total_actividades': sum(t['total_actividades'] for t in trabajadores_ordenados),
            'total_horas': sum(t['total_horas'] for t in trabajadores_ordenados),
            'total_asistentes': sum(t['total_asistentes'] for t in trabajadores_ordenados),
        }
        
        return {
            'tipo_reporte': 'actividades_trabajador',
            'estadisticas': estadisticas,
            'trabajadores': trabajadores_ordenados,
            'filtros_aplicados': {
                'museo': reporte.museo_id.name,
                'fecha_desde': reporte.fecha_desde.strftime('%d/%m/%Y'),
                'fecha_hasta': reporte.fecha_hasta.strftime('%d/%m/%Y'),
                'tipo_actividad': reporte.tipo_actividad,
                'estado_actividad': reporte.estado_actividad,
            }
        }
    
    def _generar_reporte_actividades_fechas(self, reporte):
        """Genera reporte de actividades por rango de fechas"""
        dominio = [
            ('museo_id', '=', reporte.museo_id.id),
            ('fecha_inicio', '>=', reporte.fecha_desde),
            ('fecha_fin', '<=', reporte.fecha_hasta),
        ]
        
        if reporte.tipo_actividad != 'todos':
            dominio.append(('tipo_actividad', '=', reporte.tipo_actividad))
        
        if reporte.estado_actividad != 'todos':
            dominio.append(('estado', '=', reporte.estado_actividad))
        
        actividades = self.env['museo.actividad'].search(dominio, order='fecha_inicio')
        
        # Agrupar por día
        actividades_por_dia = {}
        for actividad in actividades:
            fecha_str = actividad.fecha_inicio.strftime('%Y-%m-%d')
            fecha_formateada = actividad.fecha_inicio.strftime('%d/%m/%Y')
            
            if fecha_str not in actividades_por_dia:
                actividades_por_dia[fecha_str] = {
                    'fecha': fecha_formateada,
                    'dia_semana': actividad.fecha_inicio.strftime('%A'),
                    'actividades': [],
                    'total_actividades': 0,
                    'total_asistentes': 0,
                    'total_horas': 0,
                }
            
            actividades_por_dia[fecha_str]['actividades'].append({
                'nombre': actividad.name,
                'hora_inicio': actividad.fecha_inicio.strftime('%H:%M'),
                'hora_fin': actividad.fecha_fin.strftime('%H:%M'),
                'tipo': dict(actividad._fields['tipo_actividad'].selection).get(actividad.tipo_actividad),
                'estado': dict(actividad._fields['estado'].selection).get(actividad.estado),
                'duracion_horas': actividad.duracion_horas,
                'asistentes': actividad.asistentes_confirmados,
                'capacidad': actividad.capacidad_maxima,
                'sala': actividad.sala or '',
                'trabajadores': ', '.join(actividad.trabajadores_ids.mapped('name')),
            })
            
            actividades_por_dia[fecha_str]['total_actividades'] += 1
            actividades_por_dia[fecha_str]['total_asistentes'] += actividad.asistentes_confirmados
            actividades_por_dia[fecha_str]['total_horas'] += actividad.duracion_horas
        
        # Ordenar por fecha
        dias_ordenados = sorted(
            actividades_por_dia.values(),
            key=lambda x: x['fecha']
        )
        
        # Estadísticas por tipo de actividad
        actividades_por_tipo = {}
        for actividad in actividades:
            tipo = dict(actividad._fields['tipo_actividad'].selection).get(actividad.tipo_actividad)
            if tipo not in actividades_por_tipo:
                actividades_por_tipo[tipo] = {
                    'total': 0,
                    'asistentes': 0,
                    'horas': 0,
                }
            
            actividades_por_tipo[tipo]['total'] += 1
            actividades_por_tipo[tipo]['asistentes'] += actividad.asistentes_confirmados
            actividades_por_tipo[tipo]['horas'] += actividad.duracion_horas
        
        # Estadísticas generales
        estadisticas = {
            'periodo': f"{reporte.fecha_desde} al {reporte.fecha_hasta}",
            'total_dias': len(dias_ordenados),
            'total_actividades': len(actividades),
            'total_asistentes': sum(a.asistentes_confirmados for a in actividades),
            'total_horas': sum(a.duracion_horas for a in actividades),
            'actividades_por_tipo': actividades_por_tipo,
            'promedio_diario': len(actividades) / max(len(dias_ordenados), 1),
        }
        
        return {
            'tipo_reporte': 'actividades_fechas',
            'estadisticas': estadisticas,
            'dias': dias_ordenados,
            'filtros_aplicados': {
                'museo': reporte.museo_id.name,
                'fecha_desde': reporte.fecha_desde.strftime('%d/%m/%Y'),
                'fecha_hasta': reporte.fecha_hasta.strftime('%d/%m/%Y'),
                'tipo_actividad': reporte.tipo_actividad,
                'estado_actividad': reporte.estado_actividad,
            }
        }
    
    def action_generar_reporte(self):
        """Genera el reporte y cambia su estado"""
        self.ensure_one()
        
        if self.fecha_desde > self.fecha_hasta:
            raise UserError(_('La fecha "Desde" no puede ser posterior a la fecha "Hasta"'))
        
        # Forzar el cálculo de datos
        self._compute_datos_reportes()
        self.estado = 'generado'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reporte Generado',
                'message': f'El reporte "{self.name}" ha sido generado exitosamente.',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_exportar_pdf(self):
        """Exporta el reporte a PDF"""
        self.ensure_one()
        
        if self.estado != 'generado':
            raise UserError(_('Debe generar el reporte primero'))
        
        # Aquí iría la lógica para generar el PDF
        # Por ahora, solo simulamos la exportación
        self.archivo_pdf_filename = f'reporte_{self.name.replace(" ", "_")}.pdf'
        self.estado = 'exportado'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'PDF Exportado',
                'message': f'El reporte ha sido exportado como PDF.',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_exportar_excel(self):
        """Exporta el reporte a Excel"""
        self.ensure_one()
        
        if self.estado != 'generado':
            raise UserError(_('Debe generar el reporte primero'))
        
        # Aquí iría la lógica para generar el Excel
        self.archivo_excel_filename = f'reporte_{self.name.replace(" ", "_")}.xlsx'
        self.estado = 'exportado'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Excel Exportado',
                'message': f'El reporte ha sido exportado como Excel.',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_ver_detalles(self):
        """Muestra los detalles del reporte en una vista"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Detalles del Reporte: {self.name}',
            'res_model': 'museo.reporte',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'views': [(False, 'form')],
        }
    
    def action_exportar_pdf(self):
        """Genera y descarga el reporte en PDF"""
        self.ensure_one()
        
        if not self.datos_reportes:
            raise UserError(_('Debe generar el reporte primero.'))
        
        try:
            # Generar contenido PDF
            pdf_content = self._generar_pdf()
            
            # Nombre del archivo
            nombre_archivo = f"reporte_{self.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Actualizar el registro
            self.write({
                'archivo_pdf': base64.b64encode(pdf_content),
                'archivo_pdf_filename': nombre_archivo,
                'estado': 'exportado'
            })
            
            # Devolver acción de descarga
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/museo.reporte/{self.id}/archivo_pdf/{nombre_archivo}?download=true',
                'target': 'self',
            }
            
        except Exception as e:
            raise UserError(_('Error al generar PDF: %s') % str(e))
    
    def action_exportar_excel(self):
        """Genera y descarga el reporte en Excel"""
        self.ensure_one()
        
        if not self.datos_reportes:
            raise UserError(_('Debe generar el reporte primero.'))
        
        try:
            # Generar contenido Excel
            excel_content = self._generar_excel()
            
            # Nombre del archivo
            nombre_archivo = f"reporte_{self.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Actualizar el registro
            self.write({
                'archivo_excel': base64.b64encode(excel_content),
                'archivo_excel_filename': nombre_archivo,
                'estado': 'exportado'
            })
            
            # Devolver acción de descarga
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/museo.reporte/{self.id}/archivo_excel/{nombre_archivo}?download=true',
                'target': 'self',
            }
            
        except Exception as e:
            raise UserError(_('Error al generar Excel: %s') % str(e))
    
    def _generar_pdf(self):
        """Genera el contenido del PDF"""
        # Importar dependencias
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            raise UserError(_('Faltan dependencias. Instale: pip install reportlab'))
        
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        
        # Configurar documento
        if self.tipo_reporte == 'actividades_trabajador':
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        else:
            doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=10
        )
        
        normal_style = styles['Normal']
        
        # Contenido del PDF
        story = []
        
        # Título
        story.append(Paragraph(f"<b>REPORTE: {self.name}</b>", title_style))
        
        # Información básica
        story.append(Paragraph(f"<b>Museo:</b> {self.museo_id.name}", normal_style))
        story.append(Paragraph(f"<b>Tipo de Reporte:</b> {dict(self._fields['tipo_reporte'].selection).get(self.tipo_reporte)}", normal_style))
        story.append(Paragraph(f"<b>Período:</b> {self.fecha_desde} al {self.fecha_hasta}", normal_style))
        story.append(Paragraph(f"<b>Generado el:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Procesar datos del reporte
        if self.datos_reportes:
            datos = json.loads(self.datos_reportes)
            
            if 'error' in datos:
                story.append(Paragraph(f"<b>Error:</b> {datos.get('mensaje', 'Error desconocido')}", normal_style))
            else:
                # Mostrar estadísticas
                if 'estadisticas' in datos:
                    stats = datos['estadisticas']
                    story.append(Paragraph("<b>ESTADÍSTICAS GENERALES</b>", subtitle_style))
                    
                    stats_data = [
                        ['Total Actividades', str(stats.get('total_actividades', 0))],
                        ['Total Asistentes', str(stats.get('total_asistentes', 0))],
                        ['Total Horas', f"{stats.get('total_horas', 0):.2f}"],
                    ]
                    
                    if 'total_trabajadores' in stats:
                        stats_data.append(['Total Trabajadores', str(stats.get('total_trabajadores', 0))])
                    if 'total_dias' in stats:
                        stats_data.append(['Total Días', str(stats.get('total_dias', 0))])
                    
                    # Crear tabla de estadísticas
                    table = Table(stats_data, colWidths=[200, 100])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(table)
                    story.append(Spacer(1, 20))
                
                # Mostrar datos específicos según el tipo de reporte
                if self.tipo_reporte == 'actividades_trabajador' and 'trabajadores' in datos:
                    story.append(Paragraph("<b>DETALLE POR TRABAJADOR</b>", subtitle_style))
                    
                    for trabajador in datos['trabajadores'][:10]:  # Mostrar máximo 10
                        story.append(Paragraph(f"<b>{trabajador.get('nombre', 'N/A')}</b> - {trabajador.get('cargo', '')}", normal_style))
                        story.append(Paragraph(f"Actividades: {trabajador.get('total_actividades', 0)} | Horas: {trabajador.get('total_horas', 0):.2f} | Asistentes: {trabajador.get('total_asistentes', 0)}", normal_style))
                        story.append(Spacer(1, 10))
                
                elif self.tipo_reporte == 'actividades_fechas' and 'dias' in datos:
                    story.append(Paragraph("<b>ACTIVIDADES POR DÍA</b>", subtitle_style))
                    
                    for dia in datos['dias'][:15]:  # Mostrar máximo 15 días
                        story.append(Paragraph(f"<b>{dia.get('fecha', 'N/A')}</b> - {dia.get('dia_semana', '')}", normal_style))
                        story.append(Paragraph(f"Actividades: {dia.get('total_actividades', 0)} | Asistentes: {dia.get('total_asistentes', 0)}", normal_style))
                        story.append(Spacer(1, 10))
        
        # Construir PDF
        doc.build(story)
        
        # Obtener contenido del buffer
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _generar_excel(self):
        """Genera el contenido del Excel"""
        # Importar dependencias
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_('Faltan dependencias. Instale: pip install xlsxwriter'))
        
        # Crear buffer para Excel
        buffer = io.BytesIO()
        
        # Crear workbook
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        
        # Formato para encabezados
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Formato normal
        normal_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Formato numérico
        number_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Crear hoja
        worksheet = workbook.add_worksheet('Reporte')
        
        # Ancho de columnas
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        
        # Escribir información básica
        row = 0
        worksheet.write(row, 0, 'REPORTE', header_format)
        worksheet.write(row, 1, self.name, normal_format)
        row += 1
        
        worksheet.write(row, 0, 'Museo', header_format)
        worksheet.write(row, 1, self.museo_id.name, normal_format)
        row += 1
        
        worksheet.write(row, 0, 'Tipo de Reporte', header_format)
        worksheet.write(row, 1, dict(self._fields['tipo_reporte'].selection).get(self.tipo_reporte), normal_format)
        row += 1
        
        worksheet.write(row, 0, 'Período', header_format)
        worksheet.write(row, 1, f"{self.fecha_desde} al {self.fecha_hasta}", normal_format)
        row += 2
        
        # Procesar datos del reporte
        if self.datos_reportes:
            datos = json.loads(self.datos_reportes)
            
            if not 'error' in datos:
                # Escribir estadísticas
                if 'estadisticas' in datos:
                    worksheet.write(row, 0, 'ESTADÍSTICAS', header_format)
                    row += 1
                    
                    stats = datos['estadisticas']
                    for key, value in stats.items():
                        if key not in ['periodo']:
                            worksheet.write(row, 0, key.replace('_', ' ').title(), header_format)
                            if isinstance(value, (int, float)):
                                worksheet.write(row, 1, value, number_format)
                            else:
                                worksheet.write(row, 1, str(value), normal_format)
                            row += 1
                    
                    row += 1
                
                # Escribir datos específicos
                if self.tipo_reporte == 'actividades_trabajador' and 'trabajadores' in datos:
                    worksheet.write(row, 0, 'TRABAJADORES', header_format)
                    row += 1
                    
                    # Encabezados de tabla
                    headers = ['Nombre', 'Cargo', 'Actividades', 'Horas', 'Asistentes']
                    for col, header in enumerate(headers):
                        worksheet.write(row, col, header, header_format)
                    row += 1
                    
                    # Datos de trabajadores
                    for trabajador in datos['trabajadores']:
                        worksheet.write(row, 0, trabajador.get('nombre', ''), normal_format)
                        worksheet.write(row, 1, trabajador.get('cargo', ''), normal_format)
                        worksheet.write(row, 2, trabajador.get('total_actividades', 0), number_format)
                        worksheet.write(row, 3, trabajador.get('total_horas', 0), number_format)
                        worksheet.write(row, 4, trabajador.get('total_asistentes', 0), number_format)
                        row += 1
                
                elif self.tipo_reporte == 'actividades_fechas' and 'dias' in datos:
                    worksheet.write(row, 0, 'ACTIVIDADES POR DÍA', header_format)
                    row += 1
                    
                    # Encabezados de tabla
                    headers = ['Fecha', 'Día', 'Actividades', 'Asistentes', 'Horas']
                    for col, header in enumerate(headers):
                        worksheet.write(row, col, header, header_format)
                    row += 1
                    
                    # Datos por día
                    for dia in datos['dias']:
                        worksheet.write(row, 0, dia.get('fecha', ''), normal_format)
                        worksheet.write(row, 1, dia.get('dia_semana', ''), normal_format)
                        worksheet.write(row, 2, dia.get('total_actividades', 0), number_format)
                        worksheet.write(row, 3, dia.get('total_asistentes', 0), number_format)
                        worksheet.write(row, 4, dia.get('total_horas', 0), number_format)
                        row += 1
                        
                        # Detalle de actividades del día
                        for actividad in dia.get('actividades', []):
                            worksheet.write(row, 1, f"  • {actividad.get('nombre', '')}", normal_format)
                            worksheet.write(row, 2, actividad.get('tipo', ''), normal_format)
                            worksheet.write(row, 3, actividad.get('asistentes', 0), number_format)
                            row += 1
                        
                        row += 1
        
        # Cerrar workbook
        workbook.close()
        
        # Obtener contenido del buffer
        excel_content = buffer.getvalue()
        buffer.close()
        
        return excel_content