from odoo import models, fields, api


class Calendar(models.Model):
    _inherit = 'calendar.event'
    leave_id = fields.Integer('Leave ID')
