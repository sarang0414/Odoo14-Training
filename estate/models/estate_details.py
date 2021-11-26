from odoo import api, fields, models

class EstateDetails(models.Model):
    _name = "estate.details"
    _description = "Details Regarding the Estate"

    name = fields.Char(string="Estate Name" , required=True)
    place = fields.Char(string="Place")
    price = fields.Integer(string="Land Price")
    estate_category_id = fields.Many2one("estate.category")
    estate_tag_ids = fields.Many2many("estate.tag")
    estate_employee_ids = fields.One2many("estate.employee" , "estate_name_id" , string="Employees")
    details = fields.Text(string="Description")

class EstateCategory(models.Model): # For writing Many2one
    _name = "estate.category"

    name = fields.Char(string=" Land Category")
    area = fields.Selection([
        ('10_acre','10 acres'),
        ('20_acre','20 acres'),
        ('40_acre','40 acres'),
        ('100_acre', '100 acres')
    ])
    estate_state_id = fields.Many2one("estate.state")

class EstateState(models.Model):  # For writing Many2one
    _name = "estate.state"
    _rec_name = "state"

    state = fields.Char(string="State")

class EstateTag(models.Model):  # For writing Many2many
    _name = "estate.tag"
    _rec_name = "tags"

    tags = fields.Char(string="Tags")

class EstateEmployee(models.Model):  # For writing One2many
    _name = "estate.employee"

    estate_name_id = fields.Many2one("estate.details")
    employee_name = fields.Char(string="Employee Name")
    experience = fields.Integer(string="Experience in Years")