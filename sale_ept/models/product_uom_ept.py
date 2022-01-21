from odoo import api, fields, models, _


class ProductUom(models.Model):
    _name = "product.uom.ept"
    _description = "Product Uom"
    _check_company_auto = True

    name = fields.Char(string="Unit of Measure", help="Product Unit of Measure", required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    uom_category_id = fields.Many2one(comodel_name='product.uom.category.ept', string='Category', check_company=True,
                                      help="Uom Product Category")
