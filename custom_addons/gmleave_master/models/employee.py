from odoo import models, fields, api, tools
from datetime import datetime


class EmployeeType(models.Model):
    _name = 'gmleave.employee_type'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)
    name_en = fields.Char('Name English')


class Employee(models.Model):
    _name = 'gmleave.employee'
    _rec_name = 'name'
    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    name_en = fields.Char('Name English')
    nickname = fields.Char('Nickname')
    email = fields.Char('Email', required=True)
    password = fields.Char('Password')
    image = fields.Image('Image')
    phone = fields.Char('Phone')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('na', 'N/A'),
    ], default='na', string='Gender')
    emptype_id = fields.Many2one('gmleave.employee_type', string='Employee Type')
    department_id = fields.Many2one('gmleave.department', string='Department')
    position_id = fields.Many2one('gmleave.position', string='Position')
    user_id = fields.Many2one('res.users', string='Related User')
    is_active = fields.Boolean('Is Active', default=True)
    leave_type_line = fields.One2many('gmleave.employee.leavetype.line', 'employee_id', string='Leave Type Line')
    leave_history_line = fields.One2many('gmleave.employee_leave_history', 'employee_id')

    @api.model
    def create(self, vals):
        user_count = self.env['res.users'].search_count([('login', '=', vals.get('email'))])
        if not user_count:
            user_vals = {
                'name': vals.get('name'),
                'login': vals.get('email'),
            }

            if vals.get('password'):
                user_vals['password'] = vals.get('password')

            if vals.get('image'):
                user_vals['image_1920'] = vals.get('image')
            user_id = self.env['res.users'].create(user_vals)
            vals['user_id'] = user_id.id
        return super(Employee, self).create(vals)

    def write(self, vals):
        user_vals = {}
        if vals.get('name'):
            user_vals['name'] = vals.get('name')
        if vals.get('email'):
            user_vals['login'] = vals.get('email')
        if vals.get('password'):
            user_vals['password'] = vals.get('password')
        if vals.get('image'):
            user_vals['image_1920'] = vals.get('image')
        self.env['res.users'].search([('id', '=', self.user_id.id)]).sudo().write(user_vals)
        return super(Employee, self).write(vals)

    def do_resign_employee(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'gmleave.approve.resign.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_employee_id': self.id,
                'default_employee_name': self.name,
            }
        }


class EmployeeLeaveTypeLine(models.Model):
    _name = 'gmleave.employee.leavetype.line'
    employee_id = fields.Many2one('gmleave.employee', ondelete='cascade')
    leave_type_id = fields.Many2one('gmleave.leave_type', string='Leave Type')
    default_day = fields.Integer('Default Day', related='leave_type_id.default_day')
    leave_day = fields.Integer('Leave Day')


class EmployeeLeaveHistory(models.Model):
    _name = 'gmleave.employee_leave_history'
    _auto = False
    employee_id = fields.Many2one('gmleave.employee', ondelete='cascade')
    code = fields.Char('Code')
    name = fields.Char('Name')
    start_date = fields.Char('Start Date')
    end_date = fields.Char('End Date')
    duration = fields.Float('Duration')

    def init(self):
        sql = """
            SELECT EXISTS (
                SELECT FROM
                    pg_tables
                WHERE
                    schemaname = 'public' AND
                    tablename  = 'gmleave_leave'
                );
        """
        self._cr.execute(sql)
        result = self._cr.dictfetchone()
        if result['exists']:
            tools.drop_view_if_exists(self._cr, 'gmleave_employee_leave_history')
            self._cr.execute("""
                CREATE OR REPLACE VIEW gmleave_employee_leave_history AS (
                    select
                        row_number() OVER () as id,
                        lv.employee_id,
                        lv.code,
                        lt.name,
                        lv.start_date,
                        lv.end_date,
                        lv.duration
                    from gmleave_leave lv
                        left join gmleave_leave_type lt on lv.leave_type_id=lt.id
                    where lv.state='approve' and lv.year='{0}'
                    order by lv.start_date desc
                )""".format(datetime.now().year))
