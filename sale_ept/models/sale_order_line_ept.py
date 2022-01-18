from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _name = "sale.order.line.ept"
    _description = "Order Line"

    order_no = fields.Many2one(comodel_name='sale.order.ept', string="Order No", help="Order No")
    product_id = fields.Many2one(comodel_name='product.ept', string="Product", help="Product")
    quantity = fields.Float(string="Quantity", default=0.0, help="Quantity")
    unit_price = fields.Float(string="Unit Price ", default=0.0, help="Unit Price ")
    state = fields.Selection(string="State", help="State's of order Line", default="draft",
                             selection=[('draft', 'draft'), ('confirmed', 'confirmed'), ('cancelled', 'cancelled')])
    uom_id = fields.Many2one(comodel_name='product.uom.ept', string="UOM", help="UOM")
    subtotal_without_tax = fields.Float(string="Subtotal Without TAX ", compute="compute_subtotal_without_tax",
                                        store=True, default=0.0, help="Subtotal Without TAX")
    stock_move_ids = fields.One2many(comodel_name='stock.move.ept', inverse_name="sale_line_id", string='Stock Move',
                                     help="Stock Move", readonly=True)
    delivered_qty = fields.Float(string="Delivered Quantity", compute="compute_delivered_qty",
                                 store=False, default=0.0, help="Delivered Quantity")
    cancelled_qty = fields.Float(string="Cancelled Quantity", compute="compute_cancelled_qty",
                                 store=False, default=0.0, help="Cancelled Quantity")
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse.ept', string="Stock Warehouse", help="Stock Warehouse")
    tax_ids = fields.Many2many('account.tax.ept', 'account_order_line_ref', 'order_line_id', 'account_id',
                               string="Account Taxs", help="Account Taxs")
    subtotal_with_tax = fields.Float(string="Subtotal With TAX ", compute="compute_subtotal_with_tax",
                                     store=True, default=0.0, help="Subtotal With TAX")

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.unit_price = self.product_id.sale_price
        self.quantity = 1

    @api.depends('unit_price', 'quantity')
    def compute_subtotal_without_tax(self):
        for line in self:
            line.subtotal_without_tax = line.unit_price * line.quantity

    @api.depends('quantity', 'unit_price', 'tax_ids', 'product_id')
    def compute_subtotal_with_tax(self):
        self.subtotal_with_tax = 0
        for order_line in self:
            if order_line.product_id.id:
                if order_line.product_id.tax_ids.tax_value:
                    if order_line.product_id.tax_ids.tax_amount_type == 'Percentage':
                        order_line.subtotal_with_tax = (
                                    order_line.unit_price * order_line.product_id.tax_ids.tax_value / 100)
                    else:
                        order_line.subtotal_with_tax = order_line.unit_price + order_line.product_id.tax_ids.tax_value

    def compute_delivered_qty(self):
        self.delivered_qty = 0
        for order_lines in self:
            order_lines.delivered_qty = sum(
                order_lines.stock_move_ids.filtered(lambda e: e.state == 'done').mapped('qty_delivered'))

    def compute_cancelled_qty(self):
        self.cancelled_qty = 0
        for order_lines in self:
            order_lines.cancelled_qty = sum(
                order_lines.stock_move_ids.filtered(lambda e: e.state == 'cancelled').mapped('qty_delivered'))
