from odoo import api, fields, models, _


class UomCategory(models.Model):
    _name = "product.uom.category.ept"
    _description = "UOM Category"

    name = fields.Char(string="UOM", help="UOM Name")
    uom_ids = fields.One2many(comodel_name='product.uom.ept', inverse_name="uom_category_id", string='UOM', help="UOM")
