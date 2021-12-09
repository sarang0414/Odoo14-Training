from odoo import api, fields, models
from odoo.exceptions import ValidationError

class BlackPanthers(models.Model):
    _name = 'black.panthers'
    _description = 'Black Panthers Car manufacturing'

    
    name = fields.Char()
    company = fields.Char()