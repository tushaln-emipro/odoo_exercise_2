from odoo import api, fields, models, _


class SaleOrderReport(models.Models):
    _name = "sale.order.report"
    _description = "Sales by Salesperson"

    user_id = fields.Many2one(comodel_name='res.users', string='Salesperson', help="Salesperson", required=True)
    from_date = fields.Date(string="From Date", help="From Date", required=True)
    to_date = fields.Date(string="To Date", help="To Date", required=True)

    name = fields.Char(string="Name", help="Name")

    def generate_report_salesperson(self):
        print(self.user_id)
        data = {'from_date': self.from_date, 'to_date': self.to_date}
        return self.env.ref('sale_order_extended.report_sales').report_action(None, data=data)
