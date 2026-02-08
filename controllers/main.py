# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class MuseoWebsiteController(http.Controller):
    
    @http.route(['/museos', '/museos/page/<int:page>'], type='http', auth="public", website=True)
    def museos_landing(self, page=1, **kw):
        """Página principal de museos"""
        try:
            # Verificar si website está instalado
            if not request.website:
                return request.redirect('/web')
            
            Museos = request.env['museo.museo']
            museos = Museos.search([('active', '=', True)], limit=20)
            
            return request.render('museos_gestion.museo_landing_template', {
                'museos': museos,
            })
            
        except Exception as e:
            _logger.error(f"Error en landing page: {str(e)}")
            return request.not_found()
    
    @http.route('/museos/<int:museo_id>', type='http', auth="public", website=True)
    def museo_detalle(self, museo_id, **kw):
        """Página de detalle de un museo"""
        try:
            if not request.website:
                return request.redirect('/web')
            
            Museo = request.env['museo.museo']
            museo = Museo.browse(museo_id)
            
            if not museo.exists() or not museo.active:
                _logger.error(f"Error en landing page: {str(e)}")
                return request.not_found()
            
            return request.render('museos_gestion.museo_detalle_template', {
                'museo': museo,
            })
            
        except Exception as e:
            _logger.error(f"Error en detalle de museo: {str(e)}")
            return request.not_found()
        
    @http.route('/historia/barrio/<int:historia_id>', type='http', auth='public', website=True)
    def historia_barrio_detalle(self, historia_id, **kwargs):
        historia = request.env['museo.historia.barrio'].browse(historia_id)
        
        # Verificar que existe y está activa
        if not historia.exists() or not historia.active:
            return request.redirect('/404')
        
        valores = {
            'historia': historia,
            'museo': historia.museo_id,
            'main_object': historia,
        }
        
        return request.render('museos.historia_barrio_detalle', valores)