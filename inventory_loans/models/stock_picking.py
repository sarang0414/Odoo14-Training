from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    loan_type = fields.Selection([
        ('loan_in', 'Loan In'),
        ('loan_out', 'Loan Out')
    ], string='Loan Type', help="Indicates if this transfer is a Loan In or Loan Out.")

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.picking_type_id and self.picking_type_id.default_loan_type:
            self.loan_type = self.picking_type_id.default_loan_type
