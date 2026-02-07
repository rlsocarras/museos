# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MuseoMuseoGaleria(models.Model):
    _name = 'museo.museo.galeria'
    _description = 'Galería de Fotos del Museo'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = 'sequence asc, id desc'
    
    name = fields.Char(
        string='Título',
        required=True,
        help='Título o descripción breve de la imagen'
    )
    
    museo_id = fields.Many2one(
        'museo.museo',
        string='Museo',
        required=True,
        ondelete='cascade'
    )
    
    imagen = fields.Binary(
        string='Imagen',
        attachment=True,
        required=True,
        help='Sube una imagen para la galería'
    )
    
    descripcion = fields.Text(
        string='Descripción Detallada',
        help='Descripción completa de la imagen'
    )
    
    fecha_captura = fields.Date(
        string='Fecha de Captura',
        help='Fecha en que se tomó la fotografía'
    )
    
    autor = fields.Char(
        string='Autor/Fotógrafo',
        help='Nombre de la persona que tomó la fotografía'
    )
    
    categoria = fields.Selection([
        ('exterior', 'Vistas Exteriores'),
        ('interior', 'Vistas Interiores'),
        ('salas', 'Salas de Exhibición'),
        ('objetos', 'Objetos Destacados'),
        ('actividades', 'Actividades'),
        ('eventos', 'Eventos Especiales'),
        ('historia', 'Históricas'),
        ('restauracion', 'Procesos de Restauración'),
        ('otros', 'Otros'),
    ], string='Categoría', default='exterior')
    
    es_imagen_principal = fields.Boolean(
        string='Usar como Imagen Principal',
        help='Si está marcado, esta imagen será la imagen principal del museo'
    )
    
    sequence = fields.Integer(
        string='Orden',
        default=10,
        help='Orden de visualización en la galería'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    @api.constrains('es_imagen_principal')
    def _check_imagen_principal(self):
        """Valida que solo haya una imagen principal por museo"""
        for foto in self:
            if foto.es_imagen_principal:
                # Buscar otras imágenes principales para el mismo museo
                otras_principales = self.search([
                    ('museo_id', '=', foto.museo_id.id),
                    ('es_imagen_principal', '=', True),
                    ('id', '!=', foto.id),
                    ('active', '=', True),
                ])
                
                if otras_principales:
                    raise ValidationError(
                        _('Solo puede haber una imagen principal por museo. '
                          'Existen otras imágenes marcadas como principales.')
                    )
    
    @api.model
    def create(self, vals):
        """Al crear una imagen marcada como principal, actualizar el museo"""
        foto = super(MuseoMuseoGaleria, self).create(vals)
        
        if foto.es_imagen_principal and foto.imagen:
            foto.museo_id.write({
                'imagen_principal': foto.imagen
            })
        
        return foto
    
    def write(self, vals):
        """Al actualizar una imagen marcada como principal, actualizar el museo"""
        result = super(MuseoMuseoGaleria, self).write(vals)
        
        for foto in self:
            if foto.es_imagen_principal and 'imagen' in vals:
                foto.museo_id.write({
                    'imagen_principal': foto.imagen
                })
        
        return result
    
    def action_set_as_principal(self):
        """Acción para establecer esta imagen como principal"""
        self.ensure_one()
        
        # Desmarcar todas las otras imágenes principales
        otras_principales = self.search([
            ('museo_id', '=', self.museo_id.id),
            ('es_imagen_principal', '=', True),
            ('id', '!=', self.id),
            ('active', '=', True),
        ])
        
        if otras_principales:
            otras_principales.write({'es_imagen_principal': False})
        
        # Marcar esta como principal y actualizar el museo
        self.write({
            'es_imagen_principal': True,
        })
        
        if self.imagen:
            self.museo_id.write({
                'imagen_principal': self.imagen
            })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Imagen Actualizada',
                'message': 'La imagen ha sido establecida como principal del museo.',
                'type': 'success',
                'sticky': False,
            }
        }