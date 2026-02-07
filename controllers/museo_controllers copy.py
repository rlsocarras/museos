# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class MuseoWebsiteController(http.Controller):
    
    @http.route(['/museos', '/museos/page/<int:page>'], 
                type='http', auth="public", website=True, sitemap=True)
    def museos_landing(self, page=1, **kw):
        """Página principal de museos"""
        try:
            Museos = request.env['museo.museo']
            
            # Solo museos activos
            domain = [('active', '=', True)]
            
            # Configurar paginación
            museos_per_page = 12
            total_museos = Museos.search_count(domain)
            
            # Calcular páginas
            pager = request.website.pager(
                url='/museos',
                total=total_museos,
                page=page,
                step=museos_per_page,
                scope=7
            )
            
            # Obtener museos para la página actual
            offset = (page - 1) * museos_per_page
            museos = Museos.search(
                domain,
                limit=museos_per_page,
                offset=offset,
                order='name asc'
            )
            
            return request.render('museos.museo_landing_template', {
                'museos': museos,
                'pager': pager,
                'current_page': page,
            })
            
        except Exception as e:
            _logger.error(f"Error en landing page de museos: {str(e)}")
            return request.not_found()
    
    @http.route('/museos/<int:museo_id>', 
                type='http', auth="public", website=True, sitemap=True)
    def museo_detalle(self, museo_id, **kw):
        """Página de detalle de un museo específico"""
        try:
            Museo = request.env['museo.museo']
            
            # Buscar museo por ID
            museo = Museo.browse(museo_id)
            
            # Verificar que exista y esté activo
            if not museo.exists() or not museo.active:
                _logger.warning(f"Museo {museo_id} no encontrado o inactivo")
                return request.not_found()
            
            # Obtener datos relacionados
            objetos_recientes = request.env['museo.objeto'].search([
                ('museo_id', '=', museo.id),
                ('active', '=', True)
            ], limit=6, order='id desc')
            
            actividades_proximas = request.env['museo.actividad'].search([
                ('museo_id', '=', museo.id),
                ('estado', 'in', ['planificada', 'confirmada']),
                ('fecha_inicio', '>=', datetime.now().date())
            ], limit=5, order='fecha_inicio asc')
            
            return request.render('museos.museo_detalle_template', {
                'museo': museo,
                'objetos_recientes': objetos_recientes,
                'actividades_proximas': actividades_proximas,
            })
            
        except Exception as e:
            _logger.error(f"Error en detalle de museo {museo_id}: {str(e)}")
            return request.not_found()
    
    @http.route('/museos/<int:museo_id>/objetos', 
                type='http', auth="public", website=True, sitemap=False)
    def museo_objetos(self, museo_id, page=1, **kw):
        """Página de objetos de un museo"""
        try:
            Museo = request.env['museo.museo']
            Objeto = request.env['museo.objeto']
            
            museo = Museo.browse(museo_id)
            
            if not museo.exists() or not museo.active:
                return request.not_found()
            
            # Configurar paginación
            objetos_per_page = 20
            total_objetos = Objeto.search_count([
                ('museo_id', '=', museo.id),
                ('active', '=', True)
            ])
            
            pager = request.website.pager(
                url=f'/museos/{museo_id}/objetos',
                total=total_objetos,
                page=page,
                step=objetos_per_page,
                scope=7
            )
            
            # Obtener objetos
            offset = (page - 1) * objetos_per_page
            objetos = Objeto.search([
                ('museo_id', '=', museo.id),
                ('active', '=', True)
            ], limit=objetos_per_page, offset=offset, order='name asc')
            
            return request.render('museos.museo_objetos_template', {
                'museo': museo,
                'objetos': objetos,
                'pager': pager,
                'current_page': page,
            })
            
        except Exception as e:
            _logger.error(f"Error en página de objetos del museo {museo_id}: {str(e)}")
            return request.not_found()
    
    @http.route('/api/museos', type='json', auth="public", methods=['GET'])
    def api_museos(self, limit=20, **kw):
        """API para obtener lista de museos (JSON)"""
        try:
            Museos = request.env['museo.museo']
            museos = Museos.search([('active', '=', True)], limit=limit)
            
            result = []
            for museo in museos:
                result.append({
                    'id': museo.id,
                    'name': museo.name,
                    'descripcion_corta': (museo.resenna_historica[:200] + '...' 
                                        if museo.resenna_historica else ''),
                    'direccion': museo.direccion or '',
                    'telefono': museo.telefono or '',
                    'email': museo.email or '',
                    'website': museo.website or '',
                    'total_objetos': len(museo.objeto_ids),
                    'url': f"/museos/{museo.id}",
                })
            
            return {
                'success': True,
                'data': result,
                'count': len(result)
            }
            
        except Exception as e:
            _logger.error(f"Error en API museos: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }