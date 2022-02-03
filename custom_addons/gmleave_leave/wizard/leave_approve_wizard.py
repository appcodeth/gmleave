from odoo import models, fields
from odoo.http import request
from ..models.time_utils import float_to_time


class LeaveApproveWizard(models.TransientModel):
    _name = 'gmleave.leave.approve.wizard'
    leave_id = fields.Integer('Leave ID')
    leave_name = fields.Char('Leave Name')

    def do_confirm_approve(self):
        # get current url
        url = ''
        params = request.__dict__['params']
        menu = self.env.ref('gmleave_leave.menu_leave')
        if params.get('kwargs'):
            kwargs = params.get('kwargs')
            if kwargs.get('context'):
                context = kwargs.get('context')
                url += request.httprequest.environ['HTTP_REFERER']
                url += '#id={0}&model={1}&view_type=form&menu_id=82'.format(context.get('active_id'), context.get('active_model'), menu.id)

        # approve leave
        leave_data = {
            'state': 'approve',
            'approve_date': fields.datetime.now(),
        }
        emp_id = self.env['gmleave.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if emp_id:
            leave_data['approve_id'] = emp_id.id
        leave = self.env['gmleave.leave'].browse([self.leave_id])
        leave.sudo().write(leave_data)

        # send email
        try:
            msg = 'ใบลา {0} ของท่าน ได้รับการอนุมัติแล้ว'.format(leave.code)
            if url:
                msg = 'ใบลา <a href="{0}">{1}</a> ของท่าน ได้รับการอนุมัติแล้ว'.format(url, leave.code)
            mail = self.env['mail.mail'].create({
                'subject': 'อนุมัติการลา',
                'email_from': self.env.company.email,
                'email_to': leave.employee_id.email,
                'body_html': msg,
            })
            mail.with_delay(eta=60).send()
        except Exception as e:
            print('Send email error!', e)

        # add event to calendar
        start_time = ''
        if leave.start_time:
            start_time = float_to_time(leave.start_time) + ':00'
        end_time = ''
        if leave.end_time:
            end_time = float_to_time(leave.end_time) + ':00'

        start = leave.start_date.strftime('%Y-%m-%d') + ' ' + ('00:00:00' if leave.all_day else start_time)
        end = leave.end_date.strftime('%Y-%m-%d') + ' ' + ('00:00:00' if leave.all_day else end_time)

        self.env['calendar.event'].create({
            'name': leave.name,
            'start': start,
            'start_date': leave.start_date,
            'start_datetime': False,
            'stop': end,
            'stop_date': leave.end_date,
            'stop_datetime': False,
            'allday': True,
        })
