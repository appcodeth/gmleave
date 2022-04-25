from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'gmleave.employee'
    effective_date = fields.Date('Effective Date')
    salary = fields.Float('Salary')
