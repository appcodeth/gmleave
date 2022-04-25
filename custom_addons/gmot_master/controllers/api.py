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
                'position': o.position_id.name,
                'effective_date': o.effective_date.strftime('%d/%m/%Y') if o.effective_date else '',
                'salary': o.salary,
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')


    @http.route('/api/employee/history/', type='http', auth='public')
    def get_employee_history(self, **kw):
        id = request.params.get('id')
        objects = request.env['gmot.employee_salary'].sudo().search([('employee_id.id', '=', id)])

        rows = []
        last_date_count = 0
        for obj in objects:
            cols = {
                'id': obj.id,
                'date': obj.date.strftime('%d/%m/%Y') if obj.date else '',
                'salary': obj.salary,
                'is_delete': False,
                'is_active': False,
            }

            if obj.date > date.today():
                cols['is_delete']= True
            elif obj.date <= date.today():
                last_date_count += 1
                if last_date_count == 1:
                    cols['is_active'] = True
            rows.append(cols)
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')
