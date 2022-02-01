import json
import pandas as pd
import base64
from datetime import datetime, date, timedelta
from odoo import http
from odoo.http import request, Response


class ReportApi(http.Controller):

    @http.route('/api/report/leave/personal', type='http', auth='public')
    def leave_personal_report(self, **kw):
        start_date = request.params.get('start_date') + ' 00:00:00'
        end_date = request.params.get('end_date') + ' 23:59:59'
        sql = """
            select
                em.code,
                em.name,
                dp.name as dept_name,
                po.name as pos_name,
                lt.name as leave_type,
                lv.duration as duration_day
            from gmleave_leave lv
                left join gmleave_leave_type lt on lv.leave_type_id=lt.id
                left join gmleave_employee em on lv.employee_id=em.id
                left join gmleave_employee_leavetype_line lin on lin.employee_id=em.id
                left join gmleave_department dp on em.department_id=dp.id
                left join gmleave_position po on em.position_id=po.id
            where lv.state='approve' and lv.start_date between '{0}' and '{1}'
        """.format(start_date, end_date)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        df = pd.DataFrame(results, columns=['code', 'name', 'dept_name', 'pos_name', 'leave_type', 'duration_day'])
        df = pd.crosstab([df.code, df.name, df.dept_name, df.pos_name], df.leave_type, values=df.duration_day, aggfunc=lambda x: x.astype(float).sum()).fillna(0)
        columns = [df.columns[i] for i in range(df.shape[1])]
        for row in df.itertuples():
            row_args = row.Index
            cols = {
                'code': row_args[0],
                'name': row_args[1],
                'department': row_args[2],
                'position': row_args[3],
            }

            for c in columns:
                value = getattr(row, c)
                cols[c] = value
            rows.append(cols)
        return Response(json.dumps({'ok': True, 'rows': rows, 'columns': columns}), content_type='application/json')

    @http.route('/api/report/leave/waiting', type='http', auth='public')
    def leave_waiting_report(self, **kw):
        year = request.params.get('year') or datetime.now().year
        sql = """
            select
                em.code,
                em.name,
                dp.name as dept_name,
                pos.name as pos_name,
                lt.name as leave_name,
                lv.start_date,
                lv.end_date,
                lv.duration
            from gmleave_leave lv
                left join gmleave_leave_type lt on lv.leave_type_id=lt.id
                left join gmleave_employee em on lv.employee_id=em.id
                left join gmleave_department dp on em.department_id=dp.id
                left join gmleave_position pos on em.position_id=pos.id
            where lv.state='draft' and year='{0}'
            order by lv.start_date desc
        """.format(year)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'code': r[0],
                'name': r[1],
                'department': r[2],
                'position': r[3],
                'leave_name': r[4],
                'start_date': r[5].strftime('%d/%m/%Y') if r[5] else '',
                'end_date': r[6].strftime('%d/%m/%Y') if r[6] else '',
                'duration': r[7],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/report/leave/usage', type='http', auth='public')
    def leave_usage_report(self, **kw):
        year = request.params.get('year') or datetime.now().year
        sql = """
            select
                em.code,
                em.name,
                dp.name as dept_name,
                pos.name as pos_name,
                lt.name as leave_name,
                lne.leave_day as leave_day_default,
                sum(lv.duration) as leave_day_used
            from gmleave_leave lv
                left join gmleave_leave_type lt on lv.leave_type_id=lt.id
                left join gmleave_employee em on lv.employee_id=em.id
                left join gmleave_employee_leavetype_line lne on lne.employee_id=em.id
                left join gmleave_department dp on em.department_id=dp.id
                left join gmleave_position pos on em.position_id=pos.id
            where lv.state='approve' and year='{0}'
            group by 1,2,3,4,5,6
            order by em.code
        """.format(year)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'code': r[0],
                'name': r[1],
                'department': r[2],
                'position': r[3],
                'leave_name': r[4],
                'leave_day_default': r[5],
                'leave_day_used': r[6],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/report/leave/toprank', type='http', auth='public')
    def leave_toprank_report(self, **kw):
        start_date = request.params.get('start_date') + ' 00:00:00'
        end_date = request.params.get('end_date') + ' 23:59:59'
        sql = """
            select
                em.code,
                em.name,
                dp.name as dept_name,
                pos.name as pos_name,
                sum(lv.duration) as total_day
            from gmleave_leave lv left join gmleave_employee em on lv.employee_id=em.id
                left join gmleave_department dp on em.department_id=dp.id
                left join gmleave_position pos on em.position_id=pos.id
            where lv.state='approve' and lv.start_date between '{0}' and '{1}'
            group by 1,2,3,4
            order by total_day desc
        """.format(start_date, end_date)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'code': r[0],
                'name': r[1],
                'department': r[2],
                'position': r[3],
                'total_day': r[4],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/report/leave/holiday', type='http', auth='public')
    def leave_holiday_report(self, **kw):
        year = request.params.get('year') or datetime.now().year
        sql = """
            select
                name,
                from_date,
                to_date
            from gmleave_holiday
            where year='{0}'
            order by from_date asc
        """.format(year)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'name': r[0],
                'from_date': r[1].strftime('%d/%m/%Y') if r[1] else '',
                'to_date': r[2].strftime('%d/%m/%Y') if r[2] else '',
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')
