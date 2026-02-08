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

    nombre_archivo = fields.Char(
        string='Nombre del Archivo',
        help='Nombre original del archivo subido'
    )

    # Y actualiza la vista para capturar el nombre:
    @api.onchange('archivo')
    def _onchange_archivo(self):
        if self.archivo and self._context.get('filename'):
            self.nombre_archivo = self._context['filename']
    
    def action_importar(self):
        """Importa objetos desde el archivo seleccionado"""
        self.ensure_one()
        
        if not self.archivo:
            raise UserError(_('Debe seleccionar un archivo para importar'))
        
        try:
            # Decodificar el archivo
            archivo_decodificado = base64.b64decode(self.archivo)
            
            # Procesar según el formato
            if self.formato_archivo == 'json':
                objetos = self._procesar_json(archivo_decodificado)
            elif self.formato_archivo == 'csv':
                objetos = self._procesar_csv(archivo_decodificado)
            elif self.formato_archivo == 'excel':
                objetos = self._procesar_excel(archivo_decodificado)
            else:
                raise UserError(_('Formato de archivo no soportado'))
            
            # Validar objetos
            objetos_validados = self._validar_objetos(objetos)
            
            # Importar objetos
            resultados = self._importar_objetos(objetos_validados)
            
            # Mostrar resultados
            return self._mostrar_resultados(resultados)
            
        except json.JSONDecodeError:
            raise UserError(_('El archivo JSON no tiene un formato válido'))
        except Exception as e:
            raise UserError(_('Error al importar: %s') % str(e))

    def _procesar_json(self, contenido):
        """Procesa archivo JSON"""
        try:
            datos = json.loads(contenido.decode('utf-8'))
            
            # Buscar la lista de objetos (puede estar en diferentes estructuras)
            if isinstance(datos, dict):
                # Buscar en diferentes claves posibles
                for key in ['objetos_museo', 'objetos', 'items', 'data']:
                    if key in datos and isinstance(datos[key], list):
                        return datos[key]
                
                # Si no encuentra lista específica, asume que el diccionario es la lista
                if 'name' in datos or 'codigo_inventario' in datos:
                    return [datos]
                else:
                    # Buscar cualquier lista en el diccionario
                    for value in datos.values():
                        if isinstance(value, list) and len(value) > 0:
                            if isinstance(value[0], dict) and ('name' in value[0] or 'codigo_inventario' in value[0]):
                                return value
            
            elif isinstance(datos, list):
                return datos
            
            raise UserError(_('No se encontraron objetos en el archivo JSON'))
            
        except Exception as e:
            raise UserError(_('Error al procesar JSON: %s') % str(e))

    def _procesar_csv(self, contenido):
        """Procesa archivo CSV"""
        try:
            import csv
            import io
            
            # Decodificar a string
            contenido_str = contenido.decode('utf-8')
            
            # Detectar delimitador
            delimitador = self._detectar_delimitador_csv(contenido_str)
            
            # Leer CSV
            file_like = io.StringIO(contenido_str)
            reader = csv.DictReader(file_like, delimiter=delimitador)
            
            objetos = []
            for i, row in enumerate(reader, 1):
                # Convertir valores vacíos a None
                row_limpio = {k: (v if v != '' else None) for k, v in row.items()}
                
                # Mapear campos si hay configuración
                if self.mapeo_campos:
                    row_mapeado = self._aplicar_mapeo_campos(row_limpio)
                else:
                    row_mapeado = self._inferir_campos_csv(row_limpio)
                
                objetos.append(row_mapeado)
            
            return objetos
            
        except ImportError:
            raise UserError(_('No se pudo importar el módulo CSV'))
        except Exception as e:
            raise UserError(_('Error al procesar CSV: %s') % str(e))

    def _procesar_excel(self, contenido):
        """Procesa archivo Excel"""
        try:
            import pandas as pd
            import io
            
            # Leer Excel
            df = pd.read_excel(io.BytesIO(contenido))
            
            # Convertir a lista de diccionarios
            objetos = df.replace({pd.np.nan: None}).to_dict('records')
            
            # Mapear campos si hay configuración
            if self.mapeo_campos:
                objetos_mapeados = []
                for obj in objetos:
                    objetos_mapeados.append(self._aplicar_mapeo_campos(obj))
                return objetos_mapeados
            else:
                # Inferir campos automáticamente
                objetos_inferidos = []
                for obj in objetos:
                    objetos_inferidos.append(self._inferir_campos_excel(obj))
                return objetos_inferidos
                
        except ImportError:
            raise UserError(_('No se pudo importar pandas. Instale: pip install pandas openpyxl'))
        except Exception as e:
            raise UserError(_('Error al procesar Excel: %s') % str(e))

    def _detectar_delimitador_csv(self, contenido):
        """Detecta el delimitador del CSV"""
        # Muestras de las primeras líneas
        lineas = contenido.split('\n')[:5]
        
        # Contar ocurrencias de delimitadores comunes
        delimitadores = [',', ';', '\t', '|']
        conteos = {}
        
        for delim in delimitadores:
            conteo = sum(line.count(delim) for line in lineas if line)
            if conteo > 0:
                conteos[delim] = conteo / len([l for l in lineas if l])
        
        if conteos:
            # Elegir el delimitador con mayor frecuencia
            return max(conteos.items(), key=lambda x: x[1])[0]
        
        return ','  # Por defecto

    def _aplicar_mapeo_campos(self, fila):
        """Aplica el mapeo de campos configurado"""
        resultado = {}
        
        for mapeo in self.mapeo_campos:
            campo_archivo = mapeo.campo_archivo.strip()
            campo_sistema = mapeo.campo_sistema
            
            if campo_archivo in fila:
                valor = fila[campo_archivo]
                
                # Convertir según el formato
                valor_convertido = self._convertir_valor(valor, mapeo.formato)
                
                resultado[campo_sistema] = valor_convertido
            elif mapeo.requerido:
                raise UserError(_('Campo requerido no encontrado: %s') % campo_archivo)
        
        return resultado

    def _inferir_campos_csv(self, fila):
        """Infere los campos del CSV automáticamente"""
        mapeo_auto = {
            # Patrones comunes para nombres de columnas
            'nombre': ['name', 'nombre', 'objeto', 'descripcion', 'title'],
            'codigo_inventario': ['codigo', 'inventario', 'codigo_inventario', 'id', 'referencia'],
            'categoria': ['categoria', 'tipo', 'clasificacion', 'category', 'type'],
            'historia': ['historia', 'descripcion', 'description', 'detalles', 'info'],
            'fecha_adquisicion': ['fecha', 'adquisicion', 'fecha_adquisicion', 'date', 'fecha_compra'],
            'estado_conservacion': ['estado', 'conservacion', 'estado_conservacion', 'condicion', 'condition'],
            'ubicacion_actual': ['ubicacion', 'localizacion', 'ubicacion_actual', 'location', 'lugar'],
            'valor_estimado': ['valor', 'precio', 'valor_estimado', 'costo', 'value', 'price'],
            'observaciones': ['observaciones', 'notas', 'comentarios', 'remarks', 'notes'],
        }
        
        resultado = {}
        campos_encontrados = set()
        
        # Normalizar nombres de columnas (minúsculas, sin espacios)
        fila_normalizada = {}
        for key, value in fila.items():
            if key:
                key_normalizado = str(key).lower().strip().replace(' ', '_').replace('-', '_')
                fila_normalizada[key_normalizado] = value
        
        # Buscar coincidencias
        for campo_sistema, posibles_nombres in mapeo_auto.items():
            for nombre in posibles_nombres:
                if nombre in fila_normalizada:
                    resultado[campo_sistema] = fila_normalizada[nombre]
                    campos_encontrados.add(campo_sistema)
                    break
        
        # Campos obligatorios
        if 'name' not in campos_encontrados and 'codigo_inventario' not in campos_encontrados:
            # Intentar usar cualquier campo como nombre
            for key, value in fila_normalizada.items():
                if value and len(str(value)) < 100:  # No demasiado largo
                    resultado['name'] = value
                    break
        
        return resultado

    def _inferir_campos_excel(self, fila):
        """Infere los campos de Excel automáticamente"""
        # Similar al CSV pero con manejo de tipos de datos de pandas
        resultado = {}
        
        for key, value in fila.items():
            if pd.isna(value):
                continue
                
            key_str = str(key).lower().strip().replace(' ', '_')
            
            # Mapeo básico
            if 'nombre' in key_str or 'name' in key_str or 'objeto' in key_str:
                resultado['name'] = str(value)
            elif 'codigo' in key_str or 'inventario' in key_str or 'id' in key_str:
                resultado['codigo_inventario'] = str(value)
            elif 'categoria' in key_str or 'tipo' in key_str:
                resultado['categoria'] = str(value).lower()
            elif 'historia' in key_str or 'descripcion' in key_str:
                resultado['historia'] = str(value)
            elif 'fecha' in key_str:
                # Intentar convertir fecha
                if isinstance(value, (pd.Timestamp, datetime)):
                    resultado['fecha_adquisicion'] = value.strftime('%Y-%m-%d')
            elif 'valor' in key_str or 'precio' in key_str:
                try:
                    resultado['valor_estimado'] = float(value)
                except:
                    pass
        
        return resultado

    def _convertir_valor(self, valor, formato):
        """Convierte el valor según el formato especificado"""
        if valor is None:
            return None
        
        try:
            if formato == 'numero':
                return float(str(valor).replace(',', '.').strip())
            elif formato == 'fecha':
                # Intentar varios formatos de fecha
                from datetime import datetime
                formatos = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
                
                for fmt in formatos:
                    try:
                        return datetime.strptime(str(valor).strip(), fmt).strftime('%Y-%m-%d')
                    except:
                        continue
                
                # Si no coincide, devolver como está
                return str(valor)
            elif formato == 'moneda':
                # Eliminar símbolos de moneda y espacios
                valor_limpio = str(valor).replace('$', '').replace('€', '').replace(',', '').strip()
                return float(valor_limpio)
            else:  # texto
                return str(valor).strip()
                
        except Exception:
            return valor

    def _validar_objetos(self, objetos):
        """Valida los objetos antes de importar"""
        objetos_validados = []
        errores = []
        
        for i, obj in enumerate(objetos, 1):
            try:
                # Validar campos requeridos
                if not obj.get('name'):
                    raise UserError(_('Falta el nombre del objeto'))
                
                if not obj.get('codigo_inventario'):
                    raise UserError(_('Falta el código de inventario'))
                
                # Validar unicidad (si no se va a sobrescribir)
                if not self.sobrescribir_existentes and self.validar_duplicados:
                    existente = self.env['museo.objeto'].search([
                        ('codigo_inventario', '=', obj['codigo_inventario']),
                        ('museo_id', '=', self.museo_id.id)
                    ], limit=1)
                    
                    if existente:
                        raise UserError(_('Ya existe un objeto con este código de inventario'))
                
                # Validar categoría
                categoria = obj.get('categoria', 'otros')
                categorias_validas = dict(self.env['museo.objeto']._fields['categoria'].selection).keys()
                
                if categoria not in categorias_validas:
                    if self.crear_categorias:
                        # Usar 'otros' si la categoría no es válida
                        obj['categoria'] = 'otros'
                    else:
                        raise UserError(_('Categoría no válida: %s') % categoria)
                
                # Validar estado de conservación
                estado = obj.get('estado_conservacion', 'bueno')
                estados_validos = dict(self.env['museo.objeto']._fields['estado_conservacion'].selection).keys()
                
                if estado not in estados_validos:
                    obj['estado_conservacion'] = 'bueno'  # Valor por defecto
                
                # Validar fecha
                fecha = obj.get('fecha_adquisicion')
                if fecha:
                    try:
                        # Asegurar formato YYYY-MM-DD
                        from datetime import datetime
                        if isinstance(fecha, str):
                            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                            obj['fecha_adquisicion'] = fecha_obj.strftime('%Y-%m-%d')
                    except:
                        obj['fecha_adquisicion'] = None
                
                # Validar valor estimado
                valor = obj.get('valor_estimado', 0.0)
                try:
                    obj['valor_estimado'] = float(valor) if valor else 0.0
                except:
                    obj['valor_estimado'] = 0.0
                
                # Agregar museo_id
                obj['museo_id'] = self.museo_id.id
                
                objetos_validados.append(obj)
                
            except UserError as e:
                errores.append(f"Fila {i}: {str(e)}")
            except Exception as e:
                errores.append(f"Fila {i}: Error desconocido - {str(e)}")
        
        if errores and len(errores) == len(objetos):
            # Todos los objetos tienen errores
            raise UserError(_('No se pudo importar ningún objeto:\n%s') % '\n'.join(errores[:10]))
        
        return objetos_validados

    def _importar_objetos(self, objetos):
        """Importa los objetos validados a la base de datos"""
        creados = 0
        actualizados = 0
        errores_importacion = []
        
        for obj in objetos:
            try:
                # Buscar si ya existe
                existente = self.env['museo.objeto'].search([
                    ('codigo_inventario', '=', obj['codigo_inventario']),
                    ('museo_id', '=', self.museo_id.id)
                ], limit=1)
                
                if existente and self.sobrescribir_existentes:
                    # Actualizar existente
                    existente.write(obj)
                    actualizados += 1
                elif not existente:
                    # Crear nuevo
                    self.env['museo.objeto'].create(obj)
                    creados += 1
                else:
                    # Saltar (ya existe y no sobrescribir)
                    pass
                    
            except Exception as e:
                errores_importacion.append(f"{obj.get('name', 'Sin nombre')} ({obj.get('codigo_inventario', 'Sin código')}): {str(e)}")
        
        return {
            'creados': creados,
            'actualizados': actualizados,
            'errores': errores_importacion,
            'total_procesados': len(objetos)
        }

    def _mostrar_resultados(self, resultados):
        """Muestra los resultados de la importación"""
        mensaje = f"""
        IMPORTACIÓN COMPLETADA
        ======================
        Objetos creados: {resultados['creados']}
        Objetos actualizados: {resultados['actualizados']}
        Total procesados: {resultados['total_procesados']}
        """
        
        if resultados['errores']:
            mensaje += f"\nErrores ({len(resultados['errores'])}):\n"
            mensaje += '\n'.join(resultados['errores'][:5])  # Mostrar solo primeros 5 errores
            if len(resultados['errores']) > 5:
                mensaje += f"\n... y {len(resultados['errores']) - 5} errores más"
        
        # Crear registro de importación
        registro = self.env['museo.importacion.registro'].create({
            'fecha': fields.Date.today(),
            'museo_id': self.museo_id.id,
            'tipo': 'objetos',
            'creados': resultados['creados'],
            'actualizados': resultados['actualizados'],
            'errores': len(resultados['errores']),
            'total': resultados['total_procesados'],
            'archivo': self.archivo,
            'nombre_archivo': self.nombre_archivo or 'importacion.json',
        })
        
        # Mostrar notificación
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Importación Completada',
                'message': mensaje,
                'type': 'info' if resultados['errores'] else 'success',
                'sticky': True,
                'next': {
                    'type': 'ir.actions.act_window',
                    'name': 'Registro de Importación',
                    'res_model': 'museo.importacion.registro',
                    'res_id': registro.id,
                    'views': [(False, 'form')],
                    'target': 'current',
                }
            }
        }
    
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

# Agrega esta clase al mismo archivo o en uno nuevo
class MuseoImportacionRegistro(models.Model):
    _name = 'museo.importacion.registro'
    _description = 'Registro de Importaciones'
    _order = 'fecha desc'
    
    fecha = fields.Date(
        string='Fecha',
        default=fields.Date.today,
        required=True
    )
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True
    )
    
    tipo = fields.Selection([
        ('objetos', 'Objetos'),
        ('actividades', 'Actividades'),
        ('convenios', 'Convenios'),
        ('trabajadores', 'Trabajadores'),
    ], string='Tipo', required=True)
    
    creados = fields.Integer(string='Creados')
    actualizados = fields.Integer(string='Actualizados')
    errores = fields.Integer(string='Errores')
    total = fields.Integer(string='Total Procesados')
    
    archivo = fields.Binary(string='Archivo Importado')
    nombre_archivo = fields.Char(string='Nombre del Archivo')
    
    log_detallado = fields.Text(string='Log Detallado')
    
    usuario_id = fields.Many2one(
        'res.users',
        string='Usuario',
        default=lambda self: self.env.user
    )

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