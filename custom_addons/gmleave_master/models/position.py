from odoo import models, fields, api


class Position(models.Model):
    _name = 'gmleave.position'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)
    name_en = fields.Char('Name English')
