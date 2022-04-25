import json
from odoo import http
from odoo.http import request, Response
from werkzeug import utils


class MainController(http.Controller):
    @http.route('/gmot/', type='http', auth='public', website=True)
    def index(self, **kwargs):
        return request.render('gmot_master.index_page', {})
