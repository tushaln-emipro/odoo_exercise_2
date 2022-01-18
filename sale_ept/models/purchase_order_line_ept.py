from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line.ept"
    _description = "Purchase Order Line"

    purchase_order_id = fields.Many2one(comodel_name='purchase.order.ept', string="Purchase Order",
                                        help="Purchase Order")
    product_id = fields.Many2one(comodel_name='product.ept', string="Product", help="Product")
    name = fields.Char(string="Description", help="‘Description")
    quantity = fields.Float(string="Quantity", default=0.0, help="Quantity")
    cost_price = fields.Float(string="Cost Price", default=0.0, help="Cost Price")
    state = fields.Selection(string="State", help="State of the Purchase Order Line", default='draft',
                             selection=[('draft', 'draft'), ('confirmed', 'confirmed'), ('done', 'done'),
                                        ('cancelled', 'cancelled')])
    uom_id = fields.Many2one(comodel_name='product.uom.ept', string="UOM", help="UOM")
    subtotal = fields.Float(string="Sub Total", compute="compute_subtotal", store=False, default=0.0, help="Subtotal")

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.name = self.product_id.sku
        self.cost_price = self.product_id.sale_price
        self.quantity = 1

    @api.depends('quantity', 'cost_price')
    def compute_subtotal(self):
        for line in self:
            line.subtotal = line.cost_price * line.quantity
