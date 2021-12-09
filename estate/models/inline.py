from odoo import api, fields, models

class InlineModel(models.Model):
    _name = "inline.model"
    _description = "Test Model"

    name = fields.Char()
    line_ids = fields.One2many("inline.model.line", "names")


class InlineModelLine(models.Model):
    _name = "inline.model.line"
    _description = "Test Model Line"

    names = fields.Many2one("inline.model")
    field_1 = fields.Char()
    field_2 = fields.Char()
    field_3 = fields.Char()