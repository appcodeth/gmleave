import json
import pandas as pd
import base64
from datetime import datetime, date, timedelta
from odoo import http
from odoo.http import request, Response


class DashboardApi(http.Controller):

    @http.route('/api/dashboard/count', type='http', auth='public')
    def dashboard_count(self, **kw):
        sql = """
            select
                (select count(*) from gmleave_leave where year='{0}') as count_all,
                (select count(*) from gmleave_leave where year='{0}' and state='approve') as count_approve,
                (select count(*) from gmleave_leave where year='{0}' and state in ('refuse', 'cancel')) as count_cancel,
                (select count(*) from gmleave_employee where is_active=true) as count_employee
            """.format(datetime.now().year)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'count_all': r[0],
                'count_approve': r[1],
                'count_cancel': r[2],
                'count_employee': r[3],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/dashboard/overviewAll', type='http', auth='public')
    def dashboard_leave_overview_all(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
            select
                sum(case when to_char(lv.start_date, 'MM')='01' then lv.duration else 0 end) as m01,
                sum(case when to_char(lv.start_date, 'MM')='02' then lv.duration else 0 end) as m02,
                sum(case when to_char(lv.start_date, 'MM')='03' then lv.duration else 0 end) as m03,
                sum(case when to_char(lv.start_date, 'MM')='04' then lv.duration else 0 end) as m04,
                sum(case when to_char(lv.start_date, 'MM')='05' then lv.duration else 0 end) as m05,
                sum(case when to_char(lv.start_date, 'MM')='06' then lv.duration else 0 end) as m06,
                sum(case when to_char(lv.start_date, 'MM')='07' then lv.duration else 0 end) as m07,
                sum(case when to_char(lv.start_date, 'MM')='08' then lv.duration else 0 end) as m08,
                sum(case when to_char(lv.start_date, 'MM')='09' then lv.duration else 0 end) as m09,
                sum(case when to_char(lv.start_date, 'MM')='10' then lv.duration else 0 end) as m10,
                sum(case when to_char(lv.start_date, 'MM')='11' then lv.duration else 0 end) as m11,
                sum(case when to_char(lv.start_date, 'MM')='12' then lv.duration else 0 end) as m12
            from gmleave_leave lv where lv.start_date between '{0}' and '{1}' and lv.state='approve'
            """.format(start, end)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'name': 'ทุกประเภท',
                'data': [r[i] for i in range(0, 12)]
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/dashboard/overviewByType', type='http', auth='public')
    def dashboard_leave_overview_by_type(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
            select
                lv.leave_type_id,
                lt.name as leave_name,
                sum(case when to_char(lv.start_date, 'MM')='01' then lv.duration else 0 end) as m01,
                sum(case when to_char(lv.start_date, 'MM')='02' then lv.duration else 0 end) as m02,
                sum(case when to_char(lv.start_date, 'MM')='03' then lv.duration else 0 end) as m03,
                sum(case when to_char(lv.start_date, 'MM')='04' then lv.duration else 0 end) as m04,
                sum(case when to_char(lv.start_date, 'MM')='05' then lv.duration else 0 end) as m05,
                sum(case when to_char(lv.start_date, 'MM')='06' then lv.duration else 0 end) as m06,
                sum(case when to_char(lv.start_date, 'MM')='07' then lv.duration else 0 end) as m07,
                sum(case when to_char(lv.start_date, 'MM')='08' then lv.duration else 0 end) as m08,
                sum(case when to_char(lv.start_date, 'MM')='09' then lv.duration else 0 end) as m09,
                sum(case when to_char(lv.start_date, 'MM')='10' then lv.duration else 0 end) as m10,
                sum(case when to_char(lv.start_date, 'MM')='11' then lv.duration else 0 end) as m11,
                sum(case when to_char(lv.start_date, 'MM')='12' then lv.duration else 0 end) as m12
            from gmleave_leave lv
                left join gmleave_leave_type lt on lv.leave_type_id=lt.id
            where lv.start_date between '{0}' and '{1}' and lv.state='approve'
            group by lv.leave_type_id, lt.name
            order by leave_type_id asc
        """.format(start, end)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'name': r[1],
                'data': [r[i] for i in range(2, 14)]
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/dashboard/leaveRatioPie', type='http', auth='public')
    def dashboard_leave_ratio_pie(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
           select
                lt.id,
                lt.name,
                sum(lv.duration) as sum_leave,
                (select sum(lv1.duration) from gmleave_leave lv1 where  lv1.start_date between '{0}' and '{1}' and lv1.state='approve') as total_leave
            from gmleave_leave lv
                left join gmleave_leave_type lt on lv.leave_type_id=lt.id
            where lv.start_date between '{0}' and '{1}' and lv.state='approve'
            group by lt.id, lt.name
        """.format(start, end)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'name': r[1],
                'y': float('{:.2f}'.format((r[2] / r[3]) * 100)),
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')

    @http.route('/api/dashboard/leavePersonalType', type='http', auth='public')
    def dashboard_leave_personal_by_type(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
            select
                lt.id,
                lt.name,
                em.name,
                sum(lv.duration) as total_day
            from gmleave_leave lv
                left join gmleave_leave_type lt on lv.leave_type_id=lt.id
                left join gmleave_employee em on lv.employee_id=em.id
            where lv.start_date between '{0}' and '{1}' and lv.state='approve'
            group by lt.id, lt.name, em.name
            order by em.name
        """.format(start, end)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        df = pd.DataFrame(results, columns=['type_id', 'leave', 'employee', 'days'])
        df = pd.crosstab([df.type_id, df.leave], df.employee, values=df.days, aggfunc=lambda x: x.astype(float).sum()).fillna(0)
        columns = [df.columns[i] for i in range(df.shape[1])]
        for row in df.itertuples():
            cols = {
                'name': row.Index[1],
                'data': [],
            }
            for i in range(df.shape[1]):
                value = getattr(row, '_' + str(i + 1))
                cols['data'].append(value)
            rows.append(cols)
        return Response(json.dumps({'ok': True, 'rows': rows, 'columns': columns}), content_type='application/json')

    @http.route('/api/dashboard/leavePersonalAll', type='http', auth='public')
    def dashboard_leave_personal_all(self, **kw):
        start = request.params.get('start') + ' 00:00:00'
        end = request.params.get('end') + ' 23:59:59'
        sql = """
            select
                em.id as emp_id,
                em.name,
                sum(lv.duration) as total_day
            from gmleave_leave lv
                left join gmleave_leave_type lt on lv.leave_type_id=lt.id
                left join gmleave_employee em on lv.employee_id=em.id
            where lv.start_date between '{0}' and '{1}' and lv.state='approve'
            group by em.id,em.name
        """.format(start, end)
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        values = []
        columns = []
        for r in results:
            values.append(float(r[2]))
            columns.append(r[1])
        rows.append({'name': 'ทุกประเภท', 'data': values})
        return Response(json.dumps({'ok': True, 'rows': rows, 'columns': columns}), content_type='application/json')

    @http.route('/api/dashboard/approveList', type='http', auth='public')
    def dashboard_approve_list(self, **kw):
        sql = """
            select
                id,
                code,
                name,
                duration
            from gmleave_leave
            where state='draft'
        """
        request.cr.execute(sql)
        results = request.cr.fetchall()
        rows = []
        for r in results:
            rows.append({
                'id': r[0],
                'code': r[1],
                'name': r[2],
                'duration': r[3],
            })
        return Response(json.dumps({'ok': True, 'rows': rows}), content_type='application/json')
