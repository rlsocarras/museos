# controllers/test_controller.py
from odoo import http
from odoo.http import request

class TestController(http.Controller):
    
    @http.route('/test/museos', type='http', auth="public")
    def test_museos(self, **kw):
        return "<h1>Test funcionando</h1><p>Los controladores web están funcionando.</p>"