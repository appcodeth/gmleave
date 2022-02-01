from odoo import models, fields


class LeaveCancelWizard(models.TransientModel):
    _name = 'gmleave.leave.cancel.wizard'
    leave_id = fields.Integer('Leave ID')
    leave_name = fields.Char('Leave Name')

    def do_confirm_cancel(self):
        leave_data = {
            'state': 'refuse',
            'approve_date': fields.datetime.now(),
        }
        emp_id = self.env['gmleave.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if emp_id:
            leave_data['approve_id'] = emp_id.id
        self.env['gmleave.leave'].browse([self.leave_id]).sudo().write(leave_data)
