from odoo import api, fields, models
from odoo.osv import expression
from odoo.exceptions import ValidationError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    loan_type = fields.Selection([
        ('loan_in', 'Loan In'),
        ('loan_out', 'Loan Out')
    ], string='Loan Type', index=True)

    @api.model
    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        res = super(StockQuant, self)._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
        loan_type = self.env.context.get('loan_type')
        if loan_type:
            res = res.filtered(lambda q: q.loan_type == loan_type)
        elif self.env.context.get('force_no_loan_type'):
            res = res.filtered(lambda q: not q.loan_type)
        return res

    @api.model
    def _get_gather_domain(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        domain = super(StockQuant, self)._get_gather_domain(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
        
        loan_type = self.env.context.get('loan_type')
        if loan_type:
            domain = expression.AND([domain, [('loan_type', '=', loan_type)]])
        elif self.env.context.get('force_no_loan_type'):
            domain = expression.AND([domain, [('loan_type', '=', False)]])
            
        return domain

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity=False, reserved_quantity=False, lot_id=None, package_id=None, owner_id=None, in_date=None):
        ctx_loan_type = self.env.context.get('loan_type')
        
        # Case 1: Incoming (Increase Quantity) - Strict
        if quantity and quantity > 0:
            if not ctx_loan_type:
                # Force strict Owned if no loan type specified
                self = self.with_context(force_no_loan_type=True)
            return super(StockQuant, self)._update_available_quantity(product_id, location_id, quantity, reserved_quantity, lot_id, package_id, owner_id, in_date)

        # Case 2: Strict Context (e.g. Return Loan) - Strict
        if ctx_loan_type:
            return super(StockQuant, self)._update_available_quantity(product_id, location_id, quantity, reserved_quantity, lot_id, package_id, owner_id, in_date)
            
        # Case 3: Consumption/Reservation (Decrease/Reserve) with No Context - Mixing Allowed
        
        if not (quantity or reserved_quantity):
             raise ValidationError(('Quantity or Reserved Quantity should be set.'))
             
        self = self.sudo()
        
        # 1. Gather Preferred stock (Strict match to context)
        quants_preferred = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
        
        # 2. Gather Fallback stock (Owned stock) if context has loan_type
        # If context is empty, _gather already returns Mixed, so fallback is redundant.
        quants_fallback = self.env['stock.quant']
        if ctx_loan_type:
             quants_fallback = self.with_context(loan_type=False, force_no_loan_type=True)._gather(
                 product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True
             )
        
        # Combine: Preferred first, then Fallback
        quants = quants_preferred | quants_fallback
        
        if len(quants) <= 1 and not quants_fallback:
             return super(StockQuant, self)._update_available_quantity(product_id, location_id, quantity, reserved_quantity, lot_id, package_id, owner_id, in_date)
             
        # Multi-Quant Logic
        resulting_in_date = in_date or fields.Datetime.now()
        
        qty_to_process = quantity or 0
        rsv_to_process = reserved_quantity or 0
        
        for quant in quants:
            if qty_to_process == 0 and rsv_to_process == 0:
                break
                
            vals = {}
            updated = False
            
            # 1. Handle Quantity decrease
            if qty_to_process:
                if qty_to_process < 0:
                    available = quant.quantity
                    if available > 0:
                        to_take = min(available, abs(qty_to_process))
                        vals['quantity'] = quant.quantity - to_take
                        qty_to_process += to_take # Add because qty_to_process is negative
                        updated = True
                
                elif qty_to_process > 0:
                    # Should be handled by Case 1, but safe fallback
                    vals['quantity'] = quant.quantity + qty_to_process
                    qty_to_process = 0
                    updated = True

            # 2. Handle Reservation
            if rsv_to_process:
                if rsv_to_process > 0: # Reserving
                    available_to_reserve = quant.quantity - quant.reserved_quantity
                    if available_to_reserve > 0:
                        to_reserve = min(available_to_reserve, rsv_to_process)
                        vals['reserved_quantity'] = quant.reserved_quantity + to_reserve
                        rsv_to_process -= to_reserve
                        updated = True
                elif rsv_to_process < 0: # Unreserving
                    curr_reserved = quant.reserved_quantity
                    if curr_reserved > 0:
                        to_unreserve = min(curr_reserved, abs(rsv_to_process))
                        vals['reserved_quantity'] = quant.reserved_quantity - to_unreserve
                        rsv_to_process += to_unreserve
                        updated = True

            if updated:
                 quant.write(vals)

        # Apply remainder
        if qty_to_process or rsv_to_process:
             target_quant = quants[0]
             vals = {}
             if qty_to_process:
                 vals['quantity'] = target_quant.quantity + qty_to_process
             if rsv_to_process:
                 new_rsv = target_quant.reserved_quantity + rsv_to_process
                 vals['reserved_quantity'] = max(0, new_rsv)
             target_quant.write(vals)
             
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True, allow_negative=True), resulting_in_date

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'loan_type' not in vals and self.env.context.get('loan_type'):
                vals['loan_type'] = self.env.context.get('loan_type')
        return super(StockQuant, self).create(vals_list)
