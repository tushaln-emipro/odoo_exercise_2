from odoo import api, fields, models, _


class ProductUom(models.Model):
    _name = "product.uom.ept"
    _description = "Product Uom"

    name = fields.Char(string="Unit of Measure", help="Product Unit of Measure", required=True)
    uom_category_id = fields.Many2one(comodel_name='product.uom.category.ept', string='Category',
                                      help="Uom Product Category")
