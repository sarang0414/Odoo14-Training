from random import randint

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EstateDetails(models.Model):
    _name = "estate.details"
    _description = "Details Regarding the Estate"

    name = fields.Char(string="Estate Name" , required=True)
    place = fields.Char(string="Place")
    price = fields.Integer(string="Land Price")
    offer_price = fields.Integer(string="Offer Price" , compute="_compute_offer" , inverse="_inverse_offer")
    estate_category_id = fields.Many2one("estate.category")
    estate_tag_ids = fields.Many2many("estate.tag")
    estate_employee_ids = fields.One2many("estate.employee" , "estate_name_id" , string="Employees")
    details = fields.Text(string="Description")
    owners = fields.Many2one("estate.owner") # For Verifying Record Rules
    estate_employee_count = fields.Integer(compute="_compute_estate_employee_count") # For employee count in stat buttons in estate.details

    def name_get(self):  # IT WILL GET EXECUTED AUTOMATICALLY.. USED WHEN WE WANT TO SET NAME & PLACE TO BE SHOWN IN MANY2ONE FIELDS
        res = []
        for rec in self:
            res.append((rec.id,'%s-%s'%(rec.name,rec.place)))
        return res

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100):
    #     if args is None:
    #         args = []
    #     domain = args + ['|',('name',operator,name),('place',operator,name)]
    #     return super(EstateDetails, self).search(domain,limit=limit).name_get()

    @api.model
    def create(self, vals_list):
        print("CONTEXT VALUES ARE..",self.env.context)
        return super().create(vals_list)

    @api.depends('estate_employee_ids')
    def _compute_estate_employee_count(self):
        for rec in self:
            employee_count = self.env['estate.employee'].search_count([('estate_name_id','=',rec.id)])
            rec.estate_employee_count = employee_count



    def action_estate_employee_count(self):
        print("Testttt")
        print(self.estate_employee_count)

    @api.depends("price")
    def _compute_offer(self):
        self.offer_price = self.price - 20000
        print("OFFER PRICE IS***************{}".format(self.offer_price))
        print("*-*-******-**-**--{}".format(self))

    def _inverse_offer(self):
        self.price = self.offer_price + 50000



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
    country = fields.Char()

    _sql_constraints = [
        ('estate_state_uniq', 'unique (state)', 'The State should be unique !')
    ]


class EstateTag(models.Model):  # For writing Many2many
    _name = "estate.tag"
    _rec_name = "tags"

    tags = fields.Char(string="Tags")
    color = fields.Integer()



class EstateEmployee(models.Model):  # For writing One2many
    _name = "estate.employee"

    estate_name_id = fields.Many2one("estate.details")
    employee_name = fields.Char(string="Employee Name")
    experience = fields.Integer(string="Experience in Years")



    @api.constrains('experience')
    def _check_experience(self):
        for record in self:
            if record.experience == 0:
                raise ValidationError("This Post is for experienced Employees , {} is not Eligible".format(record.employee_name))


class EstateOwner(models.Model):
    _name = "estate.owner"
    _rec_name = "owner_name"

    owner_name = fields.Char(string="Owner Name")
    owner_gender = fields.Selection([
        ('male','Male'),
        ('female', 'Female'),
        ('others', 'Others')
    ])
    estate_data = fields.Many2one("estate.details")
    description = fields.Text(string="Description")
    status = fields.Char()
    state = fields.Selection([
        ('registered','Registered'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ],default='registered')
    user_id = fields.Many2one("res.users")  # For Record Rules
    owner_age = fields.Integer()



    @api.onchange("estate_data")
    def _onchange_estate_data(self):
        self.description = self.estate_data.details


    def action_owner_status_cancel(self):
        self.status = "Cancelled"
        return True

    def action_owner_status_renew(self):
        self.status = "Approved"
        return True

    def action_owner_status_pending(self):
        self.status = "Pending"

    @api.constrains('owner_name')
    def _check_owner_name(self):
        for record in self:
            owners = self.env['estate.owner'].search([('owner_name', '=', record.owner_name),('id', '!=', record.id)])
            print("************************")
            print(owners)
            if owners:
                raise ValidationError('Name already Exists')


class EstateManagers(models.Model):
    _name = "estate.managers"

    manager_name = fields.Char()
    manager_join_date = fields.Date()
    manager_age = fields.Integer()
    manager_resign_date = fields.Date()
    manager_salary = fields.Integer()
    manager_gender = fields.Selection([
        ('male','Male'),
        ('female','Female'),
    ])
    estate_name_manager = fields.Many2one("estate.details", string="Estate Name")
    manager_description = fields.Char(related="estate_name_manager.place", string="Estate Location")
    manager_age_group = fields.Selection([
        ('minor','Minor'),
        ('major','Major')
    ], compute="_compute_age_group")
    manager_base_salary = fields.Integer(compute="_compute_base_salary", readonly=True)


    _sql_constraints = [
        ('manager_name_unique','unique(manager_name)','The Manager Name should be unique'),
        ('manager_dates_check','check(manager_join_date<manager_resign_date)','Join Date Cannot be greater than Resign Date'),
        ('manager_age_notnull','CHECK(manager_age IS NOT NULL)','The age should not be null value')
    ]

    @api.model
    def default_get(self, fields_list):    # IT WILL EXECUTED WHEN WE OPEN THE RECORD (WE CAN SET DEFAULT VALUES TO FIELDS IF NECESSARY)
        print("Hellooooo")
        res = super(EstateManagers, self).default_get(fields_list)
        res['manager_name'] = "Demo Name"
        res["manager_description"] = "Demo Description"
        return res

    @api.returns('self', lambda value: value.id)  # Still works if api.returns is not Given
    def copy(self, default=None):
        default = dict(default or {})
        print("Default...",default)   # {}
        default["manager_name"]="Copy of "+self.manager_name
        # default.update(
        #     manager_name=_("%s (copy)") % (self.manager_name or ''),
        #     manager_age = _("%d") % (45))
        rslt = super().copy(default)
        print("Default..",default)
        print("Final Return..",rslt)
        return rslt

    @api.depends_context('manager_age')
    def _compute_base_salary(self):
        for rec in self:
            if rec.manager_age > 25:
                rec.manager_base_salary = 85000
            else:
                rec.manager_base_salary = 35000

    @api.depends('manager_age')
    def _compute_age_group(self):
        for rec in self:
            if rec.manager_age > 18:
                rec.manager_age_group = "major"
            else:
                rec.manager_age_group = "minor"

    # @api.model
    # def create(self, vals_list):
    #     print("SELF*******",self)
    #     print("VALS LIST BEFORE ***********",vals_list)
    #     print("USER ENV ..",self.env)
    #     print("USER ENV USER..",self.env.user)
    #     print("USER ENV COMPANY..",self.env.company)
    #     print("USER ENV CONTEXT..",self.env.context)
    #     print("USER ENV LANG..",self.env.lang)
    #     print("USER ENV SUPERUSER ?..",self.env.su)
    #     rslt = super().create(vals_list)
    #     print("SELF*******", rslt)
    #     return rslt

    @api.model_create_multi  # [{},{},{},...]
    def create(self, vals_list):
        for values in vals_list:
            values["manager_age"] = 25

        rslt = super(EstateManagers, self).create(vals_list)
        print("RESULT..",rslt)
        print("VALS LIST..",vals_list)
        return rslt

    def action_create_records(self):    # TO IMPLEMENT MODEL_CREATE_MULTI
        manager_list = [{"manager_name": "aalG5GfddflddGg", "manager_age": 12}, {"manager_name": "aaH7lffddHkdHh", "manager_age": 42}]
        manager_rec = self.env["estate.managers"].create(manager_list)
        print("Manger record List is ", manager_rec)
        self._cr.commit()

    def action_tutorial_orm_methods(self):
        #*************SEARCH******************
        managers = self.env["estate.managers"].search([])
        print("All Managers : -- > ",managers)
        male_managers = self.env["estate.managers"].search([('manager_gender','=','male')])
        print("Male Managers : -- > ",male_managers)
        male_managers_age = self.env["estate.managers"].search([('manager_gender', '=', 'male'),
                                                                ('manager_age','>=',30)])
        print("Male Managers Age greater than 30 : -- > ", male_managers_age)
        # *************SEARCH_COUNT******************
        managers_count = self.env["estate.managers"].search_count([])
        print("All Managers Count : -- > ", managers_count)
        # *************ref******************
        record = self.env.ref("estate.estate_managers_form_view")
        print("Record with ref : -- > ", record)
        # *************Browse******************
        browsed_rec = self.env["estate.managers"].browse(16)
        print("Browsed record : -- > ", browsed_rec)






class TestModel(models.Model):
    _name = "test.model"
    _description = "Test Model"

    name = fields.Char()
    age = fields.Integer()


class Transport(models.Model):
    _inherit = "estate.details"

    vehicles = fields.Char()

class SaleDetails(models.Model):
    _inherit = "sale.order"

    description = fields.Char(string="Sale Description")

class Quotations(models.Model):
    _name = "estate.quotation"
    _inherit = "estate.details"

    estate_quotations = fields.Char(string="Estate Quotations")

class DeligationDemo(models.Model):
    _name = "deligation.demo"

    _inherits = {
        'estate.state':'state_id',
        'estate.tag':'tag_id'
    }

    deligation_names = fields.Char(string="Deligation name")

    state_id = fields.Many2one("estate.state")
    tag_id = fields.Many2one("estate.tag")


