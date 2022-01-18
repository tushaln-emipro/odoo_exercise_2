from odoo import api, fields, models, _


class AccountTax(models.Model):
    _name = "account.tax.ept"
    _description = "Account Tax"

    name = fields.Char(string="Name", help="Name of Account Tax")
    tax_use = fields.Selection(string="Tax Use", help="Tax Use", default="None",
                               selection=[('None', 'None'), ('Sales', 'Sales'), ('Purchase', 'Purchase')])
    tax_value = fields.Float(string="Amount", help="Tax Value", default=0.0)
    tax_amount_type = fields.Selection(string="Tax Amount Type", help="Tax Amount Type", default="Percentage",
                                       selection=[('Percentage', 'Percentage'), ('Fixed', 'Fixed')])
