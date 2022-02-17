from odoo import models, fields
from odoo.http import request


class LeaveCancelWizard(models.TransientModel):
    _name = 'gmleave.leave.cancel.wizard'
    leave_id = fields.Integer('Leave ID')
    leave_name = fields.Char('Leave Name')

    def do_confirm_cancel(self):
        # get current url
        url = ''
        params = request.__dict__['params']
        menu = self.env.ref('gmleave_leave.menu_leave')
        leave_data = {
            'state': 'refuse',
            'approve_date': fields.datetime.now(),
        }
        emp_id = self.env['gmleave.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if emp_id:
            leave_data['approve_id'] = emp_id.id
        leave = self.env['gmleave.leave'].browse([self.leave_id])
        leave.sudo().write(leave_data)

        # delete event calendar
        self.env['calendar.event'].search([('leave_id', '=', leave.id)]).unlink()

        # send email
        cc_list = []
        users = self.env.ref('gmleave_leave.group_leave_manager').users
        for u in users:
            if '@' in u.login:
                cc_list.append(u.login)
        try:
            msg = 'ใบลา {0} ของท่าน ไม่ได้รับการอนุมัติ'.format(leave.code)
            if url:
                msg = 'ใบลา <a href="{0}">{1}</a> ของท่าน ไม่ได้รับการอนุมัติ'.format(url, leave.code)
            mail = self.env['mail.mail'].create({
                'subject': 'ใบลาไม่ได้รับการอนุมัติ',
                'email_from': self.env.company.email,
                'email_to': leave.employee_id.email,
                'body_html': msg,
                'email_cc': ','.join(cc_list)
            })
            mail.with_delay(eta=60).send()
        except Exception as e:
            print('Send email error!', e)
