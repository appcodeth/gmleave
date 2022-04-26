from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'gmleave.employee'
    effective_date = fields.Date('Effective Date')
    salary = fields.Float('Salary')
    emp_salary_line = fields.One2many('gmot.employee_salary', 'employee_id', string='Employee Salary')
    ot_emp_line = fields.One2many('gmot.ot_employee', 'employee_id', string='OT Employee')


class EmployeeSalary(models.Model):
    _name = 'gmot.employee_salary'
    _order = 'date desc'
    employee_id = fields.Many2one('gmleave.employee', ondelete='cascade')
    date = fields.Date('Date')
    salary = fields.Float('Salary')
    active = fields.Boolean(default=True)


class OT(models.Model):
    _name = 'gmot.ot'
    _order = 'date asc'
    date = fields.Date('Date')
    rate = fields.Float('Rate')
    ot_employee_line = fields.One2many('gmot.ot_employee', 'ot_id', string='OT Employee Line')


class OTEmployee(models.Model):
    _name = 'gmot.ot_employee'
    ot_id = fields.Many2one('gmot.ot', ondelete='cascade')
    employee_id = fields.Many2one('gmleave.employee', ondelete='cascade')
    salary_date = fields.Date('Salary Date')
    salary = fields.Float('Salary')
    cfg_workday_per_month = fields.Float('Config Workday Per Month')
    cfg_workhour_per_day = fields.Float('Config Workhour Per Day')
    hours = fields.Float('Hours')
    amount = fields.Float('Amount')
    approve_date = fields.Date('Approve Date')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
    ], default='draft', string='Status')
