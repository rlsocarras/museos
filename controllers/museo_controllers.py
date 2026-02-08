# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class MuseoController(http.Controller):
    
    @http.route('/museos/<int:museo_id>', type='http', auth='public', website=True)
    def museo_detalle(self, museo_id, **kwargs):
        """Mostrar detalle completo de un museo"""
        try:
            museo = request.env['museo.museo'].sudo().search([
                ('id', '=', museo_id),
                ('active', '=', True)
            ])
            
            if not museo:
                return request.render('website.404')
            
            # Preparar datos adicionales
            valores = {
                'museo': museo,
                'format_amount': self._format_amount,
            }
            
            return request.render('museos.museo_template', valores)
            
        except Exception as e:
            _logger.error(f"Error al mostrar museo: {e}")
            return request.render('website.500')
    
    @http.route('/museos', type='http', auth='public', website=True)
    def museo_lista(self, **kwargs):
        """Listar todos los museos"""
        try:
            museos = request.env['museo.museo'].sudo().search([
                ('active', '=', True)
            ], order='name')
            
            valores = {
                'museos': museos,
            }
            
            return request.render('museos.museo_lista_template', valores)
            
        except Exception as e:
            _logger.error(f"Error al listar museos: {e}")
            return request.render('website.500')
    
    def _format_amount(self, amount, currency):
        """Formatear cantidad monetaria"""
        if currency:
            return f"{amount:,.2f} {currency.symbol}"
        return f"{amount:,.2f}"
    
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