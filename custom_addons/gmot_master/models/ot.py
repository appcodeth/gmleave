from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'gmleave.employee'
    effective_date = fields.Date('Effective Date')
    salary = fields.Float('Salary')


class EmployeeSalary(models.Model):
    _name = 'gmot.employee_salary'
    _order = 'date desc'
    employee_id = fields.Many2one('gmleave.employee', ondelete='cascade')
    date = fields.Date('Date')
    salary = fields.Float('Salary')
    active = fields.Boolean(default=False)
