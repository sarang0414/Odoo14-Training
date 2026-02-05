from odoo import fields, models

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    default_loan_type = fields.Selection([
        ('loan_in', 'Loan In'),
        ('loan_out', 'Loan Out')
    ], string='Default Loan Type', help="If set, this loan type will be automatically assigned to pickings of this type.")
