import json
import io
from math import ceil
from datetime import datetime, date, timedelta
from odoo import http
from odoo.http import request, Response
from odoo.tools.misc import xlsxwriter

CFG_WORKDAY_PER_MONTH = 30
CFG_WORKHOUR_PER_DAY = 8


class OTApi(http.Controller):
    def get_employee_id(self):
        login_id = request.env.user.id
        employee = request.env['gmleave.employee'].sudo().search([('user_id', '=', login_id)])
        if not employee:
            employee = request.env['gmleave.employee'].sudo().search([('name', '=', request.env.user.name)])
        return employee.id

    @http.route('/api/employee/list/', type='http', auth='user')
    def get_employee_list(self, **kw):
        objects = request.env['gmleave.employee'].sudo().search([('is_active', '=', True)], order='code asc')
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

    @http.route('/api/employee/history/', type='http', auth='user')
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
            # find salary can be delete or is active?
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
                employee = request.env['gmleave.employee'].sudo().search([('id', '=', r['id'])])
                employee.write({
                    'effective_date': eff_date,
                    'salary': r['salary'],
                })

                # check is duplicated for salary history
                duplicated = request.env['gmot.employee_salary'].sudo().search_count([
                    ('employee_id.id', '=', r['id']),
                    ('date', '=', eff_date),
                    ('salary', '=', r['salary']),
                ])
                if not duplicated:
                    request.env['gmot.employee_salary'].sudo().create({
                        'employee_id': r['id'],
                        'date': eff_date,
                        'salary': r['salary'],
                        'active': True,
                    })
        return {'ok': True}

    @http.route('/api/employee/history/delete/', type='http', auth='user')
    def delete_employee_history(self, **kw):
        id = request.params.get('id')
        emp_id = request.params.get('emp_id')
        request.env['gmot.employee_salary'].sudo().search([('id', '=', id)]).unlink()

        # find latest history and update them
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

    @http.route('/api/ot/list/', type='http', auth='user')
    def ot_list(self, **kw):
        rp = int(request.params.get('rp') or '2')
        page = int(request.params.get('page') or '1')
        sort = request.params.get('sort') or ''
        desc = request.params.get('desc') or ''

        total = request.env['gmot.ot'].sudo().search_count([])
        total_pages = int(ceil(float(total) / rp))
        results = page * rp
        page_count = results if results <= total else total

        sort_by = 'date'
        if sort:
            sort_by = sort + ' ' + ('desc' if desc == 'true' else 'asc')
        objects = request.env['gmot.ot'].sudo().search([], limit=rp, offset=(page - 1) * rp, order=sort_by)

        rows = []
        for o in objects:
            emp_names = []
            for e in o.ot_employee_line:
                emp_names.append('{0}'.format(e.employee_id.name.split(' ')[0]))
            rows.append({
                'id': o.id,
                'date': o.date.strftime('%d/%m/%Y') if o.date else '',
                'rate': o.rate,
                'emp_names': emp_names,
                'emp_strs': ', '.join(emp_names),
            })

        return Response(json.dumps({
            'ok': True,
            'rows': rows,
            'total': total,
            'total_pages': total_pages,
            'page_count': page_count,
        }), content_type='application/json')

    @http.route('/api/ot/save/', methods=['POST'], csrf=False, type='json', auth='user')
    def ot_save(self, **kw):
        data = request.params.get('data')

        ot_id = data.get('id')
        if ot_id:
            # update ot data
            request.env['gmot.ot'].sudo().search([('id', '=', ot_id)]).write({
                'date': datetime.strptime(data['date'], '%d/%m/%Y').strftime('%Y-%m-%d'),
                'rate': data['rate'] or 0
            })
            request.env['gmot.ot_employee'].sudo().search([('ot_id.id', '=', ot_id)]).unlink()
        else:
            # create new ot data
            result = request.env['gmot.ot'].sudo().create({
                'date': datetime.strptime(data['date'], '%d/%m/%Y').strftime('%Y-%m-%d'),
                'rate': data['rate'] or 0
            })
            ot_id = result.id
        for e in data['employees']:
            request.env['gmot.ot_employee'].sudo().create({
                'ot_id': ot_id,
                'employee_id': e,
            })
        return {'ok': True}

    @http.route('/api/ot/delete/', type='http', auth='user')
    def ot_delete(self, **kw):
        id = request.params.get('id')
        count_status = request.env['gmot.ot_employee'].sudo().search_count([
            ('status', '=', 'approve'),
            ('ot_id.id', '=', id),
        ])
        if count_status:
            return Response(json.dumps({'ok': False, 'msg': 'ไม่สามารถลบได้ เนื่องจาก OT มีการอนุมัติแล้ว!'}), content_type='application/json')
        request.env['gmot.ot'].sudo().search([('id', '=', id)]).unlink()
        request.env['gmot.ot_employee'].sudo().search([('ot_id.id', '=', id)]).unlink()
        return Response(json.dumps({'ok': True}), content_type='application/json')

    @http.route('/api/ot/get/', type='http', auth='user')
    def ot_get(self, **kw):
        id = request.params.get('id')
        obj = request.env['gmot.ot'].sudo().search([('id', '=', id)])
        emp_ids = []
        for e in obj.ot_employee_line:
            emp_ids.append(e.employee_id.id)
        rows = {
            'id': obj.id,
            'date': obj.date.strftime('%Y-%m-%d') if obj.date else '',
            'rate': obj.rate,
            'employees': emp_ids,
        }
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/ot/employee/list/', type='http', auth='user')
    def ot_employee_list(self, **kw):
        EMPLOYEE_ID = self.get_employee_id()
        emp = request.env['gmleave.employee'].sudo().search([('id', '=', EMPLOYEE_ID)])
        eff_date = emp.effective_date
        eff_salary = emp.salary

        # find latest active salary
        objects = request.env['gmot.employee_salary'].sudo().search([('employee_id.id', '=', EMPLOYEE_ID)], order='date desc')
        rows = []
        last_date_count = 0
        for obj in objects:
            if obj.date <= date.today():
                last_date_count += 1
                if last_date_count == 1:
                    eff_date = obj.date
                    eff_salary = obj.salary
                    break

        if not eff_salary:
            return Response(json.dumps({'ok': False, 'msg': 'พนักงาน [{0}] ยังไม่ได้กำหนดข้อมูลเงินเดือน!'.format(emp.code)}), content_type='application/json')

        objects = request.env['gmot.ot_employee'].sudo().search([('employee_id.id', '=', EMPLOYEE_ID), ('status', '=', 'draft')], order='ot_id')
        rows = []
        for o in objects:
            rows.append({
                'id': o.id,
                'ot_date': o.ot_id.date.strftime('%d/%m/%Y') if o.ot_id.date else '',
                'ot_rate': o.ot_id.rate,
                'salary_date': eff_date.strftime('%d/%m/%Y') if eff_date else '',
                'salary': eff_salary,
                'cfg_workday_per_month': CFG_WORKDAY_PER_MONTH,
                'cfg_workhour_per_day': CFG_WORKHOUR_PER_DAY,
                'hours': o.hours,
                'amount': o.amount,
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/ot/employee/save/', methods=['POST'], csrf=False, type='json', auth='user')
    def ot_employee_save(self, **kw):
        rows = request.params.get('data')
        for r in rows:
            request.env['gmot.ot_employee'].sudo().search([('id', '=', r['id'])]).write({
                'salary_date': datetime.strptime(r['salary_date'], '%d/%m/%Y').strftime('%Y-%m-%d'),
                'salary': r['salary'],
                'cfg_workday_per_month': r['cfg_workday_per_month'],
                'cfg_workhour_per_day': r['cfg_workhour_per_day'],
                'hours': r['hours'] if r['hours'] else None,
                'amount': r['amount']
            })
        return {'ok': True}

    @http.route('/api/ot/employee/history/', type='http', auth='user')
    def ot_employee_history(self, **kw):
        EMPLOYEE_ID = self.get_employee_id()
        context = [('employee_id.id', '=', EMPLOYEE_ID), ('status', '=', 'approve')]
        approve_date = request.params.get('approve_date')
        if approve_date:
            context.append(('approve_date', '=', datetime.strptime(approve_date, '%d/%m/%Y').strftime('%Y-%m-%d')))
        objects = request.env['gmot.ot_employee'].sudo().search(context, order='ot_id')
        rows = []
        for o in objects:
            rows.append({
                'id': o.id,
                'ot_date': o.ot_id.date.strftime('%d/%m/%Y') if o.ot_id.date else '',
                'ot_rate': o.ot_id.rate,
                'salary_date': o.salary_date.strftime('%d/%m/%Y') if o.salary_date else '',
                'salary': o.salary,
                'cfg_workday_per_month': o.cfg_workday_per_month,
                'cfg_workhour_per_day': o.cfg_workhour_per_day,
                'hours': o.hours,
                'amount': o.amount,
                'approve_date': o.approve_date.strftime('%d/%m/%Y') if o.approve_date else '',
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/ot/approve/list/', type='http', auth='user')
    def ot_approve_list(self, **kw):
        sql = """
                select
                    e.id,
                    e.code,
                    e.name,
                    p.name as position,
                    d.name as department,
                    (select sum(ot.amount) from gmot_ot_employee ot where ot.employee_id=e.id and ot.status='draft') as total_amount,
                    (select sum(ot.amount) from gmot_ot_employee ot where ot.employee_id=e.id and ot.status='approve') as cumulative_amount
                from
                    gmleave_employee e
                        left join gmleave_position p on e.position_id=p.id
                        left join gmleave_department d on e.department_id=d.id
                where e.is_active=true
                order by e.code asc, total_amount desc
            """
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        for o in results:
            rows.append({
                'id': o[0],
                'code': o[1],
                'name': o[2],
                'position': o[3],
                'department': o[4],
                'total_amount': o[5],
                'cumulative_amount': o[6],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/ot/approve/draft/list/', type='http', auth='user')
    def ot_approve_draft_list(self, **kw):
        emp_id = request.params.get('emp_id')
        objects = request.env['gmot.ot_employee'].sudo().search([('employee_id.id', '=', emp_id), ('status', '=', 'draft'), ('amount', '>', 0)], order='ot_id')
        rows = []
        for o in objects:
            rows.append({
                'id': o.id,
                'ot_date': o.ot_id.date.strftime('%d/%m/%Y') if o.ot_id.date else '',
                'ot_rate': o.ot_id.rate,
                'salary_date': o.salary_date.strftime('%d/%m/%Y') if o.salary_date else '',
                'salary': o.salary,
                'cfg_workday_per_month': o.cfg_workday_per_month,
                'cfg_workhour_per_day': o.cfg_workhour_per_day,
                'hours': o.hours,
                'amount': o.amount,
                'approve_date': o.approve_date.strftime('%d/%m/%Y') if o.approve_date else '',
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/ot/approve/history/list/', type='http', auth='user')
    def ot_approve_history_list(self, **kw):
        emp_id = request.params.get('emp_id')
        context = [('employee_id.id', '=', emp_id), ('status', '=', 'approve')]
        approve_date = request.params.get('approve_date')
        if approve_date:
            context.append(('approve_date', '=', datetime.strptime(approve_date, '%d/%m/%Y').strftime('%Y-%m-%d')))
        objects = request.env['gmot.ot_employee'].sudo().search(context, order='ot_id')

        rows = []
        for o in objects:
            rows.append({
                'id': o.id,
                'ot_date': o.ot_id.date.strftime('%d/%m/%Y') if o.ot_id.date else '',
                'ot_rate': o.ot_id.rate,
                'salary_date': o.salary_date.strftime('%d/%m/%Y') if o.salary_date else '',
                'salary': o.salary,
                'cfg_workday_per_month': o.cfg_workday_per_month,
                'cfg_workhour_per_day': o.cfg_workhour_per_day,
                'hours': o.hours,
                'amount': o.amount,
                'approve_date': o.approve_date.strftime('%d/%m/%Y') if o.approve_date else '',
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/ot/approve/confirm/', type='http', auth='user')
    def ot_approve_confirm(self, **kw):
        emp_id = request.params.get('emp_id')
        objects = request.env['gmot.ot_employee'].sudo().search([('employee_id.id', '=', emp_id), ('status', '=', 'draft'), ('amount', '>', 0)], order='ot_id')
        for obj in objects:
            obj.write({
                'approve_date': datetime.today(),
                'status': 'approve',
            })
        return Response(json.dumps({'ok': True}), content_type='application/json')

    @http.route('/api/dashboard/hours/all/', type='http', auth='user')
    def dashboard_hour_all(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
            select
                sum(case when to_char(lv.approve_date, 'MM')='01' then lv.hours else 0 end) as m01,
                sum(case when to_char(lv.approve_date, 'MM')='02' then lv.hours else 0 end) as m02,
                sum(case when to_char(lv.approve_date, 'MM')='03' then lv.hours else 0 end) as m03,
                sum(case when to_char(lv.approve_date, 'MM')='04' then lv.hours else 0 end) as m04,
                sum(case when to_char(lv.approve_date, 'MM')='05' then lv.hours else 0 end) as m05,
                sum(case when to_char(lv.approve_date, 'MM')='06' then lv.hours else 0 end) as m06,
                sum(case when to_char(lv.approve_date, 'MM')='07' then lv.hours else 0 end) as m07,
                sum(case when to_char(lv.approve_date, 'MM')='08' then lv.hours else 0 end) as m08,
                sum(case when to_char(lv.approve_date, 'MM')='09' then lv.hours else 0 end) as m09,
                sum(case when to_char(lv.approve_date, 'MM')='10' then lv.hours else 0 end) as m10,
                sum(case when to_char(lv.approve_date, 'MM')='11' then lv.hours else 0 end) as m11,
                sum(case when to_char(lv.approve_date, 'MM')='12' then lv.hours else 0 end) as m12
            from gmot_ot_employee lv where lv.approve_date between '{0}' and '{1}' and lv.status='approve'
        """.format(start, end)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        for o in results:
            rows.append({
                'name': 'ทั้งหมด',
                'data': [o[i] for i in range(0, 12)]
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/dashboard/hours/employee/', type='http', auth='user')
    def dashboard_hour_by_employee(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
            select
                lv.employee_id,
                em.name,
                sum(case when to_char(lv.approve_date, 'MM')='01' then lv.hours else 0 end) as m01,
                sum(case when to_char(lv.approve_date, 'MM')='02' then lv.hours else 0 end) as m02,
                sum(case when to_char(lv.approve_date, 'MM')='03' then lv.hours else 0 end) as m03,
                sum(case when to_char(lv.approve_date, 'MM')='04' then lv.hours else 0 end) as m04,
                sum(case when to_char(lv.approve_date, 'MM')='05' then lv.hours else 0 end) as m05,
                sum(case when to_char(lv.approve_date, 'MM')='06' then lv.hours else 0 end) as m06,
                sum(case when to_char(lv.approve_date, 'MM')='07' then lv.hours else 0 end) as m07,
                sum(case when to_char(lv.approve_date, 'MM')='08' then lv.hours else 0 end) as m08,
                sum(case when to_char(lv.approve_date, 'MM')='09' then lv.hours else 0 end) as m09,
                sum(case when to_char(lv.approve_date, 'MM')='10' then lv.hours else 0 end) as m10,
                sum(case when to_char(lv.approve_date, 'MM')='11' then lv.hours else 0 end) as m11,
                sum(case when to_char(lv.approve_date, 'MM')='12' then lv.hours else 0 end) as m12
            from gmot_ot_employee lv left join gmleave_employee em on lv.employee_id=em.id
            where lv.approve_date between '{0}' and '{1}' and lv.status='approve'
            group by lv.employee_id, em.name
        """.format(start, end)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        for o in results:
            rows.append({
                'name': o[1],
                'data': [o[i] for i in range(2, 14)]
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/dashboard/amount/all/', type='http', auth='user')
    def dashboard_amount_all(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
            select
                sum(case when to_char(lv.approve_date, 'MM')='01' then lv.amount else 0 end) as m01,
                sum(case when to_char(lv.approve_date, 'MM')='02' then lv.amount else 0 end) as m02,
                sum(case when to_char(lv.approve_date, 'MM')='03' then lv.amount else 0 end) as m03,
                sum(case when to_char(lv.approve_date, 'MM')='04' then lv.amount else 0 end) as m04,
                sum(case when to_char(lv.approve_date, 'MM')='05' then lv.amount else 0 end) as m05,
                sum(case when to_char(lv.approve_date, 'MM')='06' then lv.amount else 0 end) as m06,
                sum(case when to_char(lv.approve_date, 'MM')='07' then lv.amount else 0 end) as m07,
                sum(case when to_char(lv.approve_date, 'MM')='08' then lv.amount else 0 end) as m08,
                sum(case when to_char(lv.approve_date, 'MM')='09' then lv.amount else 0 end) as m09,
                sum(case when to_char(lv.approve_date, 'MM')='10' then lv.amount else 0 end) as m10,
                sum(case when to_char(lv.approve_date, 'MM')='11' then lv.amount else 0 end) as m11,
                sum(case when to_char(lv.approve_date, 'MM')='12' then lv.amount else 0 end) as m12
            from gmot_ot_employee lv where lv.approve_date between '{0}' and '{1}' and lv.status='approve'
        """.format(start, end)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        for o in results:
            rows.append({
                'name': 'ทั้งหมด',
                'data': [o[i] for i in range(0, 12)]
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/dashboard/amount/employee/', type='http', auth='user')
    def dashboard_amount_by_employee(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
            select
                lv.employee_id,
                em.name,
                sum(case when to_char(lv.approve_date, 'MM')='01' then lv.amount else 0 end) as m01,
                sum(case when to_char(lv.approve_date, 'MM')='02' then lv.amount else 0 end) as m02,
                sum(case when to_char(lv.approve_date, 'MM')='03' then lv.amount else 0 end) as m03,
                sum(case when to_char(lv.approve_date, 'MM')='04' then lv.amount else 0 end) as m04,
                sum(case when to_char(lv.approve_date, 'MM')='05' then lv.amount else 0 end) as m05,
                sum(case when to_char(lv.approve_date, 'MM')='06' then lv.amount else 0 end) as m06,
                sum(case when to_char(lv.approve_date, 'MM')='07' then lv.amount else 0 end) as m07,
                sum(case when to_char(lv.approve_date, 'MM')='08' then lv.amount else 0 end) as m08,
                sum(case when to_char(lv.approve_date, 'MM')='09' then lv.amount else 0 end) as m09,
                sum(case when to_char(lv.approve_date, 'MM')='10' then lv.amount else 0 end) as m10,
                sum(case when to_char(lv.approve_date, 'MM')='11' then lv.amount else 0 end) as m11,
                sum(case when to_char(lv.approve_date, 'MM')='12' then lv.amount else 0 end) as m12
            from gmot_ot_employee lv left join gmleave_employee em on lv.employee_id=em.id
            where lv.approve_date between '{0}' and '{1}' and lv.status='approve'
            group by lv.employee_id, em.name
        """.format(start, end)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        for o in results:
            rows.append({
                'name': o[1],
                'data': [o[i] for i in range(2, 14)]
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/report/list/', type='http', auth='user')
    def report_list(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'

        if request.env.user.user_has_groups('gmot_master.group_gmot_master_manager'):
            sql = """
                select
                    ot.approve_date,
                    sum(ot.amount) as ot_amount
                from gmot_ot_employee ot
                where
                    ot.approve_date between '{0}' and '{1}' and ot.status='approve'
                group by ot.approve_date
                order by ot.approve_date
            """.format(start, end)
        else:
            emp_id = self.get_employee_id()
            sql = """
                select
                    ot.approve_date,
                    sum(ot.amount) as ot_amount
                from gmot_ot_employee ot
                where
                    ot.approve_date between '{0}' and '{1}' and
                    ot.status='approve' and
                    ot.employee_id={2}
                group by ot.approve_date
                order by ot.approve_date
            """.format(start, end, emp_id)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        for o in results:
            rows.append({
                'approve_date': o[0].strftime('%d/%m/%Y') if o[0] else '',
                'ot_amount': o[1],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/report/detail/', type='http', auth='user')
    def report_detail(self, **kw):
        approve = request.params.get('approve') + ' 00:00:00'
        if request.env.user.user_has_groups('gmot_master.group_gmot_master_manager'):
            sql = """
                    select
                        ot.id,
                        ot.date,
                        em.approve_date,
                        ot.rate,
                        sum(em.hours) as sum_hours,
                        sum(em.amount) as sum_amount
                    from gmot_ot_employee em left join gmot_ot ot on em.ot_id=ot.id
                    where em.status='approve' and em.approve_date='{0}'
                    group by ot.id, ot.date, em.approve_date, ot.rate
                """.format(approve)
        else:
            emp_id = self.get_employee_id()
            sql = """
                    select
                        ot.id,
                        ot.date,
                        em.approve_date,
                        ot.rate,
                        sum(em.hours) as sum_hours,
                        sum(em.amount) as sum_amount
                    from gmot_ot_employee em left join gmot_ot ot on em.ot_id=ot.id
                    where em.status='approve' and em.approve_date='{0}' and em.employee_id={1}
                    group by ot.id, ot.date, em.approve_date, ot.rate
                """.format(approve, emp_id)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()

        for o in results:
            rows.append({
                'id': o[0],
                'date': o[1].strftime('%d/%m/%Y') if o[1] else '',
                'approve_date': o[2].strftime('%d/%m/%Y') if o[2] else '',
                'rate': o[3],
                'sum_hours': o[4],
                'sum_amount': o[5],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/report/detail/xlsx/', type='http', auth='user')
    def report_detail_xls(self, **kw):
        approve = request.params.get('approve') + ' 00:00:00'
        if request.env.user.user_has_groups('gmot_master.group_gmot_master_manager'):
            sql = """
                select
                    ot.id,
                    ot.date,
                    em.approve_date,
                    ot.rate,
                    sum(em.hours) as sum_hours,
                    sum(em.amount) as sum_amount
                from gmot_ot_employee em left join gmot_ot ot on em.ot_id=ot.id
                where em.status='approve' and em.approve_date='{0}'
                group by ot.id, ot.date, em.approve_date, ot.rate
            """.format(approve)
        else:
            emp_id = self.get_employee_id()
            sql = """
                select
                    ot.id,
                    ot.date,
                    em.approve_date,
                    ot.rate,
                    sum(em.hours) as sum_hours,
                    sum(em.amount) as sum_amount
                from gmot_ot_employee em left join gmot_ot ot on em.ot_id=ot.id
                where em.status='approve' and em.approve_date='{0}' and em.employee_id={1}
                group by ot.id, ot.date, em.approve_date, ot.rate
            """.format(approve, emp_id)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=ot_detail_report_{0}.xlsx;'.format(request.params.get('approve')))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Sheet1')
        sheet.write(0, 0, 'ลำดับ')
        sheet.write(0, 1, 'วันที่ OT')
        sheet.write(0, 2, 'วันที่อนุมัติ')
        sheet.write(0, 3, 'Rate')
        sheet.write(0, 4, 'ชั่วโมงทำงาน')
        sheet.write(0, 5, 'จำนวนเงิน')
        row_num = 1
        for o in results:
            sheet.write(row_num, 0, row_num)
            sheet.write(row_num, 1, o[1].strftime('%Y-%m-%d') if o[1] else '')
            sheet.write(row_num, 2, o[2].strftime('%Y-%m-%d') if o[2] else '')
            sheet.write(row_num, 3, o[3])
            sheet.write(row_num, 4, o[4])
            sheet.write(row_num, 5, o[5])
            row_num += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        return response

    @http.route('/api/report/detail/employee/', type='http', auth='user')
    def report_detail_employee(self, **kw):
        ot_id = request.params.get('id')
        approve_date = request.params.get('approve') + ' 00:00:00'
        sql = """
            select
                em.code,
                em.name,
                d.name as dept_name,
                p.name as pos_name,
                sum(emot.hours) as total_hour,
                sum(emot.amount) as total_amount
            from gmot_ot_employee emot
                left join gmleave_employee em on emot.employee_id=em.id
                left join gmleave_position p on em.position_id=p.id
                left join gmleave_department d on em.department_id=d.id
            where emot.status='approve' and emot.ot_id={0} and emot.approve_date='{1}'
            group by em.code, em.name, d.name, p.name
            order by em.code asc
            """.format(ot_id, approve_date)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        for o in results:
            rows.append({
                'code': o[0],
                'name': o[1],
                'dept_name': o[2],
                'pos_name': o[3],
                'total_hour': o[4],
                'total_amount': o[5],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/report/detail/employee/xlsx/', type='http', auth='user')
    def report_detail_employee_excel(self, **kw):
        ot_id = request.params.get('id')
        approve_date = request.params.get('approve') + ' 00:00:00'
        sql = """
            select
                em.code,
                em.name,
                d.name as dept_name,
                p.name as pos_name,
                sum(emot.hours) as total_hour,
                sum(emot.amount) as total_amount
            from gmot_ot_employee emot
                left join gmleave_employee em on emot.employee_id=em.id
                left join gmleave_position p on em.position_id=p.id
                left join gmleave_department d on em.department_id=d.id
            where emot.status='approve' and emot.ot_id={0} and emot.approve_date='{1}'
            group by em.code, em.name, d.name, p.name
            order by em.code asc
            """.format(ot_id, approve_date)
        rows = []
        request.cr.execute(sql)
        results = request.cr.fetchall()
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=ot_detail_report_by_employee_{0}.xlsx;'.format(request.params.get('approve')))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Sheet1')
        sheet.write(0, 0, 'ลำดับ')
        sheet.write(0, 1, 'รหัสพนักงาน')
        sheet.write(0, 2, 'ชื่อ-นามสกุล')
        sheet.write(0, 3, 'แผนก')
        sheet.write(0, 4, 'ตำแหน่ง')
        sheet.write(0, 5, 'ชั่วโมงทำงาน')
        sheet.write(0, 6, 'จำนวนเงิน')
        row_num = 1
        for o in results:
            sheet.write(row_num, 0, row_num)
            sheet.write(row_num, 1, o[0])
            sheet.write(row_num, 2, o[1])
            sheet.write(row_num, 3, o[2])
            sheet.write(row_num, 4, o[3])
            sheet.write(row_num, 5, o[4])
            sheet.write(row_num, 6, o[5])
            row_num += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        return response

    @http.route('/api/dashboard/ot/amount/summary/', type='http', auth='public')
    def dashboard_ot_amout_summary(self, **kw):
        sql = """
            select
                (select sum(emp.amount) from gmot_ot_employee emp left join gmot_ot ot on emp.ot_id=ot.id where to_char(ot.date, 'YYYY')='{0}') as total_ot,
                (select sum(emp.amount) from gmot_ot_employee emp left join gmot_ot ot on emp.ot_id=ot.id where to_char(ot.date, 'YYYY')='{0}' and emp.status='approve') as total_approve,
                (select sum(emp.amount) from gmot_ot_employee emp left join gmot_ot ot on emp.ot_id=ot.id where to_char(ot.date, 'YYYY')='{0}' and emp.status='draft') as total_draft,
                (select sum(emp.hours) from gmot_ot_employee emp left join gmot_ot ot on emp.ot_id=ot.id where to_char(ot.date, 'YYYY')='{0}' and emp.status='draft') as total_draft_hours
            """.format(datetime.now().year)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'total_ot': r[0],
                'total_approve': r[1],
                'total_draft': r[2],
                'total_draft_hours': r[3],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')
