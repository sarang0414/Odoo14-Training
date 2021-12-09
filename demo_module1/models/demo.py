from odoo import api, fields, models
from odoo.exceptions import ValidationError , UserError

class DemoInherit(models.Model):
    _inherit = "sale.order"


    demo_name = fields.Char(string="Demo name")
    demo_description = fields.Char(string="Demo Description", readonly=True)

    @api.onchange("demo_name")
    def _onchange_demo_name(self):
        self.demo_description = self.demo_name

    @api.model
    def create(self, vals_list):
        return super().create(vals_list)

    def unlink(self):
        if self.partner_id.permanent_customer == True:
            raise ValidationError("Record Created by a Permanent Customer cannot be deleted")
        else:
            return super().unlink()


class PermanentUser(models.Model):
    _inherit = "res.partner"

    permanent_customer = fields.Boolean()


