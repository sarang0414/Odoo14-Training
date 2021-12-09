from odoo import api, fields, models


class ComputerSale(models.Model):

    _inherit = "sale.order"

    layout = fields.Char(string='Layout')






