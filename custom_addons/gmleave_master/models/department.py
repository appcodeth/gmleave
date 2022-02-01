from odoo import models, fields, api


class Department(models.Model):
    _name = 'gmleave.department'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)
    name_en = fields.Char('Name English')
