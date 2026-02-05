from odoo import fields, models

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    loan_type = fields.Selection([
        ('loan_in', 'Loan In'),
        ('loan_out', 'Loan Out')
    ], string='Loan Type')
    
    # We need to populate this.
    # Usually valuation layer is created from stock.move._create_in_svl / _create_out_svl
    # These methods create dicts. 
    # We should override stock.move methods to add loan_type to the dict.

# Back to stock.move to implement valuation layer propagation
