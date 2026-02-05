from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    additional_raw_material_request_count = fields.Integer(compute='_compute_additional_raw_material_request_count', string='Additional Raw Material Requests')

    def _compute_additional_raw_material_request_count(self):
        for production in self:
            production.additional_raw_material_request_count = self.env['additional.raw.material.request'].search_count([('mrp_production_id', '=', production.id)])

    def action_view_additional_raw_material_requests(self):
        self.ensure_one()
        return {
            'name': 'Additional Raw Material Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'additional.raw.material.request',
            'view_mode': 'list,form',
            'domain': [('mrp_production_id', '=', self.id)],
            'context': {'default_mrp_production_id': self.id},
        }
