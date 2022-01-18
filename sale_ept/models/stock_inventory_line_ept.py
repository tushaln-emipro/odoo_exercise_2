from odoo import api, fields, models, _


class StockInventoryLine(models.Model):
    _name = "stock.inventory.line.ept"
    _description = "Stock Inventory Line"

    product_id = fields.Many2one(comodel_name='product.ept', string="Product", help="Product")
    available_qty = fields.Float(string="System Quantity", help="System Quantity", readonly=True, default=0.0)
    counted_product_qty = fields.Float(string="Counted Product Quantity", help="Counted Product Quantity", default=0.0)
    difference = fields.Float(string="Difference ", compute="compute_difference", store=False, default=0.0,
                              help="Difference")
    inventory_id = fields.Many2one(comodel_name='stock.inventory.ept', string="Inventory", help="Inventory")

    @api.depends('counted_product_qty', 'available_qty')
    def compute_difference(self):
        for line in self:
            line.difference = line.counted_product_qty - line.available_qty
