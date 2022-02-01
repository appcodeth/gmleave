from odoo import models, fields, api


class Holiday(models.Model):
    _name = 'gmleave.holiday'
    _rec_name = 'name'
    year = fields.Char('Year', required=True)
    name = fields.Char('Name', required=True)
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
