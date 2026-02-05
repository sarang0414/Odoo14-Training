from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    packing_size = fields.Float(string='Packing Size')
    pallet_no = fields.Float(string='Pallet Number')
    pallet_size = fields.Float(string='Pallet Size')
    
    @api.onchange('packing_size', 'pallet_no', 'pallet_size')
    def _onchange_packing_details(self):
        for record in self:
            if record.packing_size and record.pallet_no and record.pallet_size:
                record.quantity = record.packing_size * record.pallet_no * record.pallet_size

    def _synchronize_quant(self, quantity, location, action="available", in_date=False, **quants_value):
        if self.packing_size and self.pallet_size:
            denominator = (self.packing_size * self.pallet_size)
            if denominator:
                delta_pallet_no = quantity / denominator
                
                # Context passing for stock.quant usage
                self = self.with_context(
                    packing_size=self.packing_size,
                    pallet_size=self.pallet_size,
                    delta_pallet_no=delta_pallet_no
                )
        return super()._synchronize_quant(quantity, location, action=action, in_date=in_date, **quants_value)
