from odoo import fields, models
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    loan_type = fields.Selection([
        ('loan_in', 'Loan In'),
        ('loan_out', 'Loan Out')
    ], string='Loan Type', related='picking_id.loan_type',
    help="Loan Type propagated from Picking or set manually.")

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super(StockMove, self)._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        print("Prepare move line vals", vals)
        # Propagate loan_type from move OR from reserved_quant if available
        if self.loan_type:
            vals['loan_type'] = self.loan_type
        elif reserved_quant and reserved_quant.loan_type:
            vals['loan_type'] = reserved_quant.loan_type
        return vals

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self.loan_type:
            vals['loan_type'] = self.loan_type
        return vals
        
    def _prepare_procurement_values(self):
        vals = super(StockMove, self)._prepare_procurement_values()
        # If move has loan_type, propagate?
        # Usually procurement creates move, not vice versa.
        # But if we create a procurement from a move...
        return vals

    def _create_in_svl(self, forced_quantity=None):
        svl_vals_list = super(StockMove, self)._create_in_svl(forced_quantity=forced_quantity)
        for svl in svl_vals_list:
             if self.loan_type:
                 svl['loan_type'] = self.loan_type
        print("In svl vals list", svl_vals_list)
        return svl_vals_list

    def _create_out_svl(self, forced_quantity=None):
        svl_vals_list = super(StockMove, self)._create_out_svl(forced_quantity=forced_quantity)
        for svl in svl_vals_list:
             if self.loan_type:
                 svl['loan_type'] = self.loan_type
        print("Out svl vals list", svl_vals_list)
        return svl_vals_list
