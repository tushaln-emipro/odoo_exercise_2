from odoo import api, fields, models, _


class Products(models.Model):
    _inherit = "product.product"

    deposit_product_id = fields.Many2one(comodel_name='product.product', string="Deposit Product",
                                         help="Deposit Product")
    deposit_product_qty = fields.Integer(string="Deposit Product Quantity", help="Deposit Product Quantity")
