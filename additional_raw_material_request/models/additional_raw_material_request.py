from odoo import models, fields, api

class AdditionalRawMaterialRequest(models.Model):
    _name = 'additional.raw.material.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Additional Raw Material Request'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    mrp_production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, tracking=True, domain="[('state', 'in', ['draft', 'confirmed'])]")
    authorized_user_id = fields.Many2one('res.users', string='Authorized User', required=True, tracking=True)
    request_details = fields.Html(string='Request Details', default='A.<br/>B.<br/>C.<br/>D')
    line_ids = fields.One2many('additional.raw.material.request.line', 'request_id', string='Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('issued', 'Issued'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, copy=False, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('additional.raw.material.request') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_issue(self):
        for request in self:
            if request.mrp_production_id.state == 'done':
                raise models.ValidationError('Cannot issue additional raw materials for a completed Manufacturing Order.')
            moves_vals = []
            for line in request.line_ids:
                moves_vals.append({
                    'raw_material_production_id': request.mrp_production_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                    'location_id': request.mrp_production_id.location_src_id.id,
                    'location_dest_id': request.mrp_production_id.production_location_id.id,
                    'name': request.mrp_production_id.name,
                })
            if moves_vals:
                self.env['stock.move'].create(moves_vals)
            request.write({'state': 'issued'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

class AdditionalRawMaterialRequestLine(models.Model):
    _name = 'additional.raw.material.request.line'
    _description = 'Additional Raw Material Request Line'

    request_id = fields.Many2one('additional.raw.material.request', string='Request', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_code = fields.Char(related='product_id.default_code', string='Code', readonly=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
