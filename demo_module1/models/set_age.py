from odoo import api, fields, models
from datetime import date


class SetAgeSaleOrder(models.Model):
    _inherit = "sale.order"
    set_age_sales = fields.Char(string="Age",store=True,compute="compute_ages",readonly=True)

    @api.depends("partner_id.set_age")
    def compute_ages(self):
        self.set_age_sales = self.partner_id.set_age


class SetAge(models.Model):
    _inherit = "res.partner"

    set_date_of_birth = fields.Date(string="Date of Birth")
    set_age = fields.Char(string="Age", compute="compute_set_age",readonly=True,store=True)

    @api.depends("set_date_of_birth")
    def compute_set_age(self):
        for rec in self:
            if rec.set_date_of_birth:
                date_today = date.today()
                print("...set_date_of_birth", rec.set_date_of_birth)   # True or False
                print("...date_today", date_today)
                total_days_obj = date_today - rec.set_date_of_birth
                total_days = total_days_obj.days
                avg_year = ((365 * 3) + 366) / 4  # 365.25
                avg_month = avg_year / 12  # 30.4375
                years = int(total_days / avg_year)  # 1.99 ==> 1
                rem_days_mon = total_days % avg_year  # 362.75
                months = int(rem_days_mon / avg_month)  # 11
                days = int(rem_days_mon % avg_month)  # 27.375 ==> 27
                print("TYPE OF...set_date_of_birth", type(rec.set_date_of_birth))
                print("TYPE OF...date_today", type(date_today))
                print("TYPE OF...total_days_obj", type(total_days_obj))
                rec.set_age = str("{} Years, {} Months, {} Days".format(years, months, days))
            else:
                pass
