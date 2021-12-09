from odoo import api, fields, models

class SaleOrderStock(models.Model):
    _inherit = "sale.order"

    sale_demo_data = fields.Char(string="Sales Demo Data")

class StockPickSaleDemo(models.Model):
    _inherit = "stock.picking"

    #sale_order_demo_id = fields.Many2one("sale.order")
    stock_demo_data = fields.Char(string="Sales Demo Data", readonly=True, compute="compute_sale_stock_demo")

    def compute_sale_stock_demo(self):
        for rec in self:
            rec.stock_demo_data = rec.sale_id.sale_demo_data
