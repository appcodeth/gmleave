from odoo import models, fields, api


class LeaveType(models.Model):
    _name = 'gmleave.leave_type'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)
    default_day = fields.Integer('Default Days')
