from odoo import api, fields, models, _


class salespersonLeadCount(models.Model):
    _name = "salesperson.lead.count"
    _description = "Salesperson Lead Count"

    lead_id = fields.Many2one(comodel_name='partner.lead.rel', string="Partner lead", help="Partner lead")
    salesperson_id = fields.Many2one(comodel_name='res.users', string="Salesperson", help=" Salesperson")
    total_pipelines = fields.Float(string="Pipelines", default=0.0, help="count number of pipeline of that salesperson")
    total_revenue = fields.Float(string="Total Revenue", default=0.0, help="Total Revenue")
    total_quotations = fields.Float(string="Quotations", default=0.0,
                                    help="total number of quotations created from this leads")
    total_sales_orders = fields.Float(string="Sales Orders", default=0.0,
                                      help="total number of sales orders created from this leads")
    total_sales_orders_amounts = fields.Float(string="Order amounts", default=0.0,
                                              help="sum of total order amounts of all this sales orders")
    conversation_amount = fields.Float(string="Conversation amount", default=0.0, help="percentage of conversation amount from expected revenue to sales order total amount. ")
