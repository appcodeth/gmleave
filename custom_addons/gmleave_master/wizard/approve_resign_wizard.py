from odoo import models, fields


class ApproveResignWizard(models.TransientModel):
    _name = 'gmleave.approve.resign.wizard'
    employee_id = fields.Integer('Employee ID')
    employee_name = fields.Char('Employee Name')

    def do_confirm_approve(self):
        employee = self.env['gmleave.employee'].browse([self.employee_id])
        employee.sudo().write({'is_active': False})
        if employee.user_id:
            users = self.env['res.users'].search([('id', '=', employee.user_id.id)], limit=1)
            if users:
                users.toggle_active()
