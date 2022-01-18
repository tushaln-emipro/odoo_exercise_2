from odoo import api, fields, models, _


class ProductStockUpdate(models.TransientModel):
    _name = "product.stock.update.ept"
    _description = "Stock Update"

    location_id = fields.Many2one(comodel_name='stock.location.ept', string='Location', help="Location")
    available_stock = fields.Float(string="Available Stock", default=0.0, help="Available Stock")
    counted_qty = fields.Float(string="Counted Quantity", default=0.0, help="Counted Quantity")
    difference_qty = fields.Float(string="Difference Quantity", compute="compute_difference_qty",
                                  store=False, default=0.0, help="Difference Quantity")

    @api.onchange('location_id')
    def onchange_location(self):
        if self.location_id.id:
            product_ids = self.env.context.get('active_ids')
            self.available_stock = self.env['product.ept'].with_context(location_id=self.location_id.id).browse(
                product_ids[0]).product_stock

    def action_update_stock(self):
        product_id = self.env.context.get('active_id')
        inventory_line = [(0, 0, {'product_id': product_id, 'available_qty': self.available_stock,
                                  'counted_product_qty': self.counted_qty, 'difference': self.difference_qty})]
        new_inventory = self.env['stock.inventory.ept'].create(
            {'name': 'Inventory' + str(product_id), 'location_id': self.location_id.id,
             'inventory_line_ids': inventory_line})
        new_inventory.action_set_validate()

    @api.depends('available_stock', 'counted_qty')
    def compute_difference_qty(self):
        for stock in self:
            stock.difference_qty = stock.counted_qty - stock.available_stock
