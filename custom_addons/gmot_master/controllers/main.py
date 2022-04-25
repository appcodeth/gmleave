import json
from odoo import http
from odoo.http import request, Response
from werkzeug import utils


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
        return request.render('gmot_master.ot_jobs_page', {
            'menu': 'ot_jobs',
        })

    @http.route('/gmot/ot/approve/', type='http', auth='public', website=True)
    def ot_approve(self, **kwargs):
        return request.render('gmot_master.ot_approve_page', {
            'menu': 'ot_approve',
        })

    @http.route('/gmot/ot/approve/draft/', type='http', auth='public', website=True)
    def ot_approve_draft(self, **kwargs):
        return request.render('gmot_master.ot_approve_draft_page', {
            'menu': 'ot_approve_draft',
        })

    @http.route('/gmot/ot/approve/history/', type='http', auth='public', website=True)
    def ot_approve_history(self, **kwargs):
        return request.render('gmot_master.ot_approve_history_page', {
            'menu': 'ot_approve_history',
        })
