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
        objects = request.env['gmot.employee_salary'].sudo().search([('employee_id.id', '=', id)], order='date desc')
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
            # set active or can be delete history salary
            if obj.date > date.today():
                cols['is_delete'] = True
            elif obj.date <= date.today():
                last_date_count += 1
                if last_date_count == 1:
                    cols['is_active'] = True
            rows.append(cols)
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/employee/save/', methods=['POST'], csrf=False, type='json', auth='public')
    def save_employee(self, **kw):
        rows = request.params.get('data')
        for r in rows:
            if r['effective_date'] and r['salary']:
                eff_date = datetime.strptime(r['effective_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
                # update employee salary
                employee = request.env['gmleave.employee'].sudo().search([('id', '=', r['id'])])
                employee.write({
                    'effective_date': eff_date,
                    'salary': r['salary'],
                })

                # check duplicate history
                duplicated = request.env['gmot.employee_salary'].sudo().search_count([('employee_id.id', '=', r['id']), ('date', '=', eff_date), ('salary', '=', r['salary'])])
                if not duplicated:
                    request.env['gmot.employee_salary'].sudo().create({
                        'employee_id': r['id'],
                        'date': eff_date,
                        'salary': r['salary'],
                        'active': True,
                    })
        return {'ok': True}

    @http.route('/api/employee/history/delete/', methods=['GET'], csrf=False, type='http', auth='public')
    def delete_employee_history(self, **kw):
        id = request.params.get('id')
        emp_id = request.params.get('emp_id')
        # remove history
        request.env['gmot.employee_salary'].sudo().search([('id', '=', id)]).unlink()

        # find lastest history and update them
        lastest_history = request.env['gmot.employee_salary'].sudo().search([('employee_id.id', '=', emp_id)], order='date desc', limit=1)
        employee = request.env['gmleave.employee'].sudo().search([('id', '=', emp_id)])
        if lastest_history:
            employee.write({
                'effective_date': lastest_history.date,
                'salary': lastest_history.salary,
            })
        else:
            employee.write({
                'effective_date': None,
                'salary': None,
            })
        return Response(json.dumps({'ok': True}), content_type='application/json')
