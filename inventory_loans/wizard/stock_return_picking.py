from odoo import models

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_picking_default_values(self):
        vals = super(ReturnPicking, self)._prepare_picking_default_values()
        picking = self.picking_id
        if picking.loan_type == 'loan_in':
            vals['loan_type'] = 'loan_out'
        elif picking.loan_type == 'loan_out':
            vals['loan_type'] = 'loan_in'
        return vals
