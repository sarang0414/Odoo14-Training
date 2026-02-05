from collections import defaultdict
from odoo import api, fields, models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    loan_type = fields.Selection([
        ('loan_in', 'Loan In'),
        ('loan_out', 'Loan Out')
    ], string='Loan Type', related='move_id.loan_type', store=True, readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        # Retrieve the original create method
        
        # We need to split vals_list by loan_type to pass correct context
        vals_by_loan = defaultdict(list)
        for vals in vals_list:
            loan_type = vals.get('loan_type')
            vals_by_loan[loan_type].append(vals)
        
        # Result accumulator
        # To maintain order, we might need a more complex approach, but for creation usually returning the set is enough.
        # However, stock.move.line create return value is used.
        
        all_lines = self.env['stock.move.line']
        
        # We need to process groups. 
        # Note: calling super().create() with a subset of vals_list creates those records.
        for loan_type, vals_group in vals_by_loan.items():
            # Pass loan_type in context for stock.quant interactions
            context = dict(self.env.context)
            if loan_type:
                context['loan_type'] = loan_type
            
            lines = super(StockMoveLine, self.with_context(**context)).create(vals_group)
            all_lines += lines
            
        return all_lines

    def _action_done(self):
        # Group by loan_type to pass context
        loan_types = set(self.mapped('loan_type'))
        if not loan_types: 
             return super(StockMoveLine, self)._action_done()

        # If we have mixed loan types or single loan type (including None)
        # We process each group with its context
        
        # We must return True/None as per original implementation? Original returns nothing usually or check code.
        # _action_done usually returns None.
        
        for loan_type in loan_types:
            lines = self.filtered(lambda l: l.loan_type == loan_type)
            context = dict(self.env.context)
            if loan_type:
                context['loan_type'] = loan_type
            
            super(StockMoveLine, lines.with_context(**context))._action_done()
        
        return True
