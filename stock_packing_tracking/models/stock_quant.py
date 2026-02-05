from odoo import models, fields, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    packing_size = fields.Float(string='Packing Size')
    pallet_no = fields.Float(string='Pallet Number')
    pallet_size = fields.Float(string='Pallet Size')
    
    @api.model
    def _get_gather_domain(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        domain = super()._get_gather_domain(product_id, location_id, lot_id, package_id, owner_id, strict)
        if self.env.context.get('packing_size'):
             domain.append(('packing_size', '=', self.env.context['packing_size']))
        if self.env.context.get('pallet_size'):
             domain.append(('pallet_size', '=', self.env.context['pallet_size']))
        return domain

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
             if 'packing_size' not in vals and self.env.context.get('packing_size'):
                  vals['packing_size'] = self.env.context['packing_size']
             if 'pallet_size' not in vals and self.env.context.get('pallet_size'):
                  vals['pallet_size'] = self.env.context['pallet_size']
             if 'pallet_no' not in vals and self.env.context.get('delta_pallet_no'):
                  vals['pallet_no'] = self.env.context['delta_pallet_no']
        return super().create(vals_list)

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity=False, reserved_quantity=False, lot_id=None, package_id=None, owner_id=None, in_date=None):
        res = super()._update_available_quantity(product_id, location_id, quantity, reserved_quantity, lot_id, package_id, owner_id, in_date)
        
        # After update, check for partial pallets if we are tracking them
        # We need to find the quant that was just updated/created.
        # Since super doesn't return the quant, we interpret the context or strict search.
        # But _update_available_quantity is often called with quantity change.
        
        # NOTE: This hook might be too generic. Let's try to handle it in write/create if possible, 
        # or use the context to know we are in a "pallet move".
        # However, typically moves are done via _action_done -> _update_available_quantity.
        
        return res

    def write(self, vals):
        # Update pallet_no based on delta passed from stock.move.line activity
        if self.env.context.get('delta_pallet_no') and len(self) == 1 and 'quantity' in vals:
             current_pallet = self.pallet_no
             delta = self.env.context.get('delta_pallet_no')
             new_pallet_no = current_pallet + delta
             vals['pallet_no'] = new_pallet_no
             
        res = super().write(vals)
        
        # Check for partial pallets logic
        for quant in self:
            if quant.packing_size and quant.pallet_size and quant.quantity > 0:
                total_capacity_per_pallet = quant.packing_size * quant.pallet_size
                if total_capacity_per_pallet > 0:
                     # Check if we have exact multiples
                     remainder = quant.quantity % total_capacity_per_pallet
                     
                     # Floating point comparison safety
                     if abs(remainder) > 0.001: 
                         # We have a partial pallet.
                         # Logic: Split the partial amount into a new quant or update existing if it's < 1 pallet.
                         
                         full_pallets = int(quant.quantity // total_capacity_per_pallet)
                         
                         if full_pallets > 0:
                             # We have some full pallets and one partial.
                             # Split!
                             # Original quant becomes the full pallets
                             # New quant becomes the partial
                             
                             # 1. Update original (this record) to full pallets
                             # We must avoid infinite recursion since we are in write()
                             # Using SQL or context to bypass?
                             # Or just check if values are already consistent.
                             
                             new_qty_full = full_pallets * total_capacity_per_pallet
                             if abs(quant.quantity - new_qty_full) > 0.001:
                                 # This is the split point
                                 remainder_qty = quant.quantity - new_qty_full
                                 remainder_bags = remainder_qty / quant.packing_size
                                 
                                 # Update this quant to be full pallets
                                 # We use sudo() and context to avoid re-triggering if needed, though simple write is fine if guarded.
                                 super(StockQuant, quant).write({
                                     'quantity': new_qty_full,
                                     'pallet_no': full_pallets
                                 })
                                 
                                 # Create new quant for the partial
                                 self.create({
                                     'product_id': quant.product_id.id,
                                     'location_id': quant.location_id.id,
                                     'lot_id': quant.lot_id.id,
                                     'package_id': quant.package_id.id,
                                     'owner_id': quant.owner_id.id,
                                     'packing_size': quant.packing_size,
                                     'pallet_size': remainder_bags, # The size of this specific "pallet" (it's a partial pallet)
                                     'pallet_no': 1, # It counts as 1 (partial) pallet
                                     'quantity': remainder_qty,
                                     'in_date': quant.in_date,
                                 })
                         else:
                             # We have less than 1 full pallet (0 full pallets)
                             # Just update the pallet_size to reflect it's now a smaller partial pallet
                             remainder_bags = quant.quantity / quant.packing_size
                             if abs(quant.pallet_size - remainder_bags) > 0.001:
                                 super(StockQuant, quant).write({
                                     'pallet_size': remainder_bags,
                                     'pallet_no': 1
                                 })

        return res
