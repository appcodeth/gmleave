import numpy as np
from datetime import datetime
from odoo import models, fields, api
from odoo.http import request

# from .time_utils import float_to_time

HALF_DAY = 4


class Leave(models.Model):
    _name = 'gmleave.leave'
    _rec_name = 'name'
    _order = 'code desc'
    code = fields.Char('Code')
    name = fields.Char('Name')
    description = fields.Text('Description')
    year = fields.Char('Year', default=datetime.now().year)
    leave_type_id = fields.Many2one('gmleave.leave_type', string='Leave Type', required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    all_day = fields.Boolean('All Day', default=True)
    by_time = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
    ], default='morning', string='By Time')
    start_time = fields.Char('Start Time')
    end_time = fields.Char('End Time')
    employee_id = fields.Many2one('gmleave.employee', string='Employee', default=lambda x: x.get_default_employee())
    approve_id = fields.Many2one('gmleave.employee', string='Approver')
    approve_date = fields.Datetime('Approve Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('refuse', 'Refuse'),
        ('cancel', 'Cancel'),
    ], default='draft', string='State')
    duration = fields.Float('Duration')
    duration_text = fields.Char('Duration', store=True, readonly=True)
    sick_leave_stat = fields.Char('Sick Leave', readonly=True, default=lambda x: x.get_sick_leave())
    personal_leave_stat = fields.Char('Personal Leave', readonly=True, default=lambda x: x.get_personal_leave())
    annual_leave_stat = fields.Char('Annual Leave', readonly=True, default=lambda x: x.get_annual_leave())
    attachment = fields.Binary('File Attachment', attachment=True)

    def send_email(self, vals):
        # get current url
        url = ''
        emp_id = self.env['gmleave.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if emp_id:
            #
            # send email to requester
            #
            try:
                msg = '???????????? {0} ????????????????????? ????????????????????????????????????'.format(vals['code'])
                if url:
                    msg = '???????????? <a href="{0}">{1}</a> ????????????????????? ????????????????????????????????????'.format(url, vals['code'])
                mail = self.env['mail.mail'].create({
                    'subject': '????????????????????????????????????????????????',
                    'email_from': self.env.company.email,
                    'email_to': emp_id.email,
                    'body_html': msg,
                })
                mail.with_delay(eta=60).send()
            except Exception as e:
                print('Send email error!', e)

            #
            # send mail to approver
            #
            cc_list = []
            users = self.env.ref('gmleave_leave.group_leave_manager').users
            for u in users:
                if '@' in u.login:
                    cc_list.append(u.login)
            try:
                msg = '?????????????????????????????? "{0} - {1}" ?????????????????????????????????????????????????????????'.format(vals['code'], vals['name'])
                if url:
                    msg = '?????????????????????????????? <a href="{0}">{1} - {2}</a> ?????????????????????????????????????????????????????????'.format(url, vals['code'], vals['name'])
                mail = self.env['mail.mail'].create({
                    'subject': '????????????????????????????????????????????????',
                    'email_from': self.env.company.email,
                    'email_to': ','.join(cc_list),
                    'body_html': msg,
                })
                mail.with_delay(eta=60).send()
            except Exception as e:
                print('Send email error!', e)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('gmleave.leave_no') or '-'
        vals['code'] = seq
        self.send_email(vals)
        return super(Leave, self).create(vals)

    @api.onchange('all_day')
    def change_all_day(self):
        if not self.all_day:
            self.start_time = '09:00'
            self.end_time = '12:00'
            self.by_time = 'morning'

    @api.onchange('by_time')
    def change_by_time(self):
        if self.by_time == 'morning':
            self.start_time = '09:00'
            self.end_time = '12:00'
        else:
            self.start_time = '13:00'
            self.end_time = '18:00'

    @api.onchange('leave_type_id')
    def change_leave_type(self):
        self.name = '{0} ({1}) {2}'.format(self.employee_id.name, self.leave_type_id.name, self.duration_text)

    @api.onchange('start_date', 'end_date', 'all_day', 'start_time', 'end_time')
    def change_leave(self):
        self.name = ''
        if self.start_date and self.end_date:
            start_date = fields.Date.from_string(self.start_date)
            end_date = fields.Date.from_string(self.end_date)
            diff_day = np.busday_count(start_date, end_date)
            self.duration = 0
            self.duration_text = ''
            if self.all_day:
                self.duration = diff_day + 1
                self.duration_text = '{0} ?????????'.format(diff_day + 1)

            if not self.all_day and self.start_time and self.end_time:
                # start_time = float_to_time(self.start_time)
                # end_time = float_to_time(self.end_time)
                start_time = self.start_time
                end_time = self.end_time
                data1 = datetime.strptime(self.start_date.strftime('%Y-%m-%d') + ' ' + start_time, '%Y-%m-%d %H:%M')
                data2 = datetime.strptime(self.end_date.strftime('%Y-%m-%d') + ' ' + end_time, '%Y-%m-%d %H:%M')
                diff = data2 - data1
                diff_day = np.busday_count(start_date, end_date)
                hours = divmod(diff.total_seconds(), 3600)[0]

                duration_day = diff_day + 0.5
                self.duration = duration_day
                self.duration_text = '{0} ?????????'.format(duration_day)

                # # half day leave in 1 day
                # duration_day = 0
                # if (hours + 1) <= HALF_DAY:
                #     duration_day = diff_day + 0.5
                #     self.duration = diff_day + 0.5
                #     self.duration_text = '{0} ?????????'.format(duration_day)
                # # more than one days
                # else:
                #     if ((hours + 1) % 24) <= HALF_DAY:
                #         duration_day = diff_day + 0.5
                #     else:
                #         duration_day = diff_day + 1
                #     self.duration = duration_day
                #     self.duration_text = '{0} ?????????'.format(duration_day)

            if self.employee_id and self.leave_type_id:
                self.name = '{0} ({1}) {2}'.format(self.employee_id.name, self.leave_type_id.name, self.duration_text)

    def get_default_employee(self):
        emp_id = self.env['gmleave.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if emp_id:
            return emp_id.id
        return None

    def get_sick_leave(self):
        return self.get_leave_dashboard('??????????????????')

    def get_personal_leave(self):
        return self.get_leave_dashboard('???????????????')

    def get_annual_leave(self):
        return self.get_leave_dashboard('???????????????????????????')

    def get_leave_dashboard(self, type):
        sql = """
        select
            sum(lv.duration) as usage_day,
            max(lin.leave_day) as total_day
        from gmleave_leave lv
            left join gmleave_leave_type lt on lv.leave_type_id=lt.id
            left join gmleave_employee em on lv.employee_id=em.id
            left join gmleave_employee_leavetype_line lin on lin.employee_id=em.id and lin.leave_type_id=lt.id
        where
            em.user_id={0} and
            lv.state='approve' and
            lv.year='{1}' and
            lt.name='{2}'
        """.format(self.env.user.id, datetime.now().year, type)
        self.env.cr.execute(sql)
        data = self.env.cr.fetchone()
        return '{0} / {1}'.format(data[0], data[1]) if data[1] else '{0}'.format(data[0] or '0')

    def do_leave_approve(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'gmleave.leave.approve.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_leave_id': self.id,
                'default_leave_name': self.name,
            }
        }

    def do_leave_refuse(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'gmleave.leave.cancel.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_leave_id': self.id,
                'default_leave_name': self.name,
            }
        }

    def unlink(self):
        for slf in self:
            self.env['calendar.event'].search([('leave_id', '=', slf.id)]).unlink()
        return super(Leave, self).unlink()
