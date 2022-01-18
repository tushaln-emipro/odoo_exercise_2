from odoo import api, fields, models, _


class CRMLeadLine(models.Model):
    _name = "crm.lead.line.ept"
    _description = "CRM Lead Line"

    product_id = fields.Many2one(comodel_name='product.ept', string="Product", help="Product")
    description = fields.Char(string="Description", help="Product description")
    expected_sell_qty = fields.Float(string="Quantity", default=0.0, help="Quantity")
    uom_id = fields.Many2one(comodel_name='product.uom.ept', string="UOM", help="UOM")
    lead_id = fields.Many2one(comodel_name='crm.lead.ept', string="Lead", help="Lead")

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.description = self.product_id.name
        self.expected_sell_qty = 1
