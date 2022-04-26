import json
from odoo import http
from odoo.http import request, Response
from werkzeug import utils

EMPLOYEE_ID = 1
CFG_WORKDAY_PER_MONTH = 30
CFG_WORKHOUR_PER_DAY = 8


class MainController(http.Controller):
    @http.route('/gmot/', type='http', auth='public', website=True)
    def index(self, **kwargs):
        return request.render('gmot_master.index_page', {
            'menu': 'index',
        })

    @http.route('/gmot/salary/', type='http', auth='public', website=True)
    def salary(self, **kwargs):
        return request.render('gmot_master.salary_page', {
            'menu': 'salary',
        })

    @http.route('/gmot/report/', type='http', auth='public', website=True)
    def report(self, **kwargs):
        return request.render('gmot_master.report_page', {
            'menu': 'report',
        })

    @http.route('/gmot/config/', type='http', auth='public', website=True)
    def config(self, **kwargs):
        return request.render('gmot_master.config_page', {
            'menu': 'config',
        })

    @http.route('/gmot/ot/open/', type='http', auth='public', website=True)
    def ot_open(self, **kwargs):
        return request.render('gmot_master.ot_open_page', {
            'menu': 'ot_open',
        })

    @http.route('/gmot/ot/jobs/', type='http', auth='public', website=True)
    def ot_jobs(self, **kwargs):
        employee = request.env['gmleave.employee'].sudo().search([('id', '=', EMPLOYEE_ID)])
        approve_date_list = []
        rows = request.env['gmot.ot_employee'].sudo().search([('employee_id.id', '=', EMPLOYEE_ID), ('status', '=', 'approve')], order='approve_date')
        for r in rows:
            approve_date = r.approve_date.strftime('%d/%m/%Y') if r.approve_date else ''
            if approve_date in approve_date_list:
                pass
            else:
                approve_date_list.append(approve_date)
        return request.render('gmot_master.ot_jobs_page', {
            'menu': 'ot_jobs',
            'employee': employee,
            'approve_date_list': approve_date_list,
            'approve_date_list_length': len(approve_date_list),
        })

    @http.route('/gmot/ot/approve/', type='http', auth='public', website=True)
    def ot_approve(self, **kwargs):
        return request.render('gmot_master.ot_approve_page', {
            'menu': 'ot_approve',
        })

    @http.route('/gmot/ot/approve/draft/', type='http', auth='public', website=True)
    def ot_approve_draft(self, **kwargs):
        employee = request.env['gmleave.employee'].sudo().search([('id', '=', request.params.get('id'))])
        return request.render('gmot_master.ot_approve_draft_page', {
            'menu': 'ot_approve_draft',
            'employee': employee,
        })

    @http.route('/gmot/ot/approve/history/', type='http', auth='public', website=True)
    def ot_approve_history(self, **kwargs):
        emp_id = request.params.get('id')
        employee = request.env['gmleave.employee'].sudo().search([('id', '=', emp_id)])
        approve_date_list = []
        rows = request.env['gmot.ot_employee'].sudo().search([('employee_id.id', '=', emp_id), ('status', '=', 'approve')], order='approve_date')
        for r in rows:
            approve_date = r.approve_date.strftime('%d/%m/%Y') if r.approve_date else ''
            if approve_date in approve_date_list:
                pass
            else:
                approve_date_list.append(approve_date)
        return request.render('gmot_master.ot_approve_history_page', {
            'menu': 'ot_approve_history',
            'employee': employee,
            'approve_date_list': approve_date_list,
            'approve_date_list_length': len(approve_date_list),
        })
