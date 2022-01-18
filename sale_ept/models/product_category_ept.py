from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _name = "product.category.ept"
    _description = "Product Category"

    name = fields.Char(string="Category Name", help="Category Name", required=True)
    parent_id = fields.Many2one(comodel_name='product.category.ept', string='Parent Category', help="Parent Category")
