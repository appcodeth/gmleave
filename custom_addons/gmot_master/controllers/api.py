import json
from datetime import datetime, date, timedelta
from odoo import http
from odoo.http import request, Response


class OTApi(http.Controller):

    @http.route('/api/employee/list/', type='http', auth='public')
    def get_employee_list(self, **kw):
        objects = request.env['gmleave.employee'].sudo().search([('is_active', '=', True)])
        rows = []
        for o in objects:
            rows.append({
                'id': o.id,
                'code': o.code,
                'name': o.name,
                'department': o.department_id.name,
                'postition': o.position_id.name,
                'effective_date': o.effective_date.strftime('%d/%m/%Y') if o.effective_date else '',
                'salary': o.salary,
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')
