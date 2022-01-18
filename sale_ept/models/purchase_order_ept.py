from odoo import api, fields, models, _
import datetime
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _name = "purchase.order.ept"
    _description = "Purchase Order"

    warehouse_id = fields.Many2one(comodel_name='stock.warehouse.ept', string="Stock Warehouse", help="Stock Warehouse")
    partner_id = fields.Many2one(comodel_name='res.partner.ept', string="Partner", help="Partner")
    order_date = fields.Date(string="Order Date", help="Order Date", default=datetime.datetime.today())
    name = fields.Char(string="Name", help="Name", required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('purchase.order'))
    state = fields.Selection(string="State", help="State of the Purchase Order", default='Draft',
                             selection=[('Draft', 'Draft'), ('Confirm', 'Confirm'), ('Done', 'Done'),
                                        ('Cancelled', 'Cancelled')])
    purchase_order_line_ids = fields.One2many(comodel_name='purchase.order.line.ept', inverse_name="purchase_order_id",
                                              string='Purchase Order Line', help="Purchase Order Line")
    amount_total = fields.Float(string="Total Weight", compute="compute_total_weight_volume_nonstore",
                                store=False, default=0.0, help="Total Weight")

    @api.depends('purchase_order_line_ids')
    def compute_total_weight_volume_nonstore(self):
        for purchase_order in self:
            subtotal = 0
            for order_line in purchase_order.purchase_order_line_ids:
                subtotal += order_line.subtotal
            purchase_order.amount_total = subtotal

    def action_set_confirm(self):

        if not self.warehouse_id.stock_location_id.id:
            raise ValidationError('Destination location not created')

        vendor_location = self.env['stock.location.ept'].search([('location_type', '=', 'Vendor')], limit=1)
        if not vendor_location:
            raise ValidationError('Vendor location not created')

        self.state = 'Confirm'
        new_incoming_shipment = self.env['stock.picking.ept'].create(
            {'name': self.env['ir.sequence'].next_by_code('picking.in') or _('New'),
             'partner_id': self.partner_id.id, 'purchase_order_id': self.id,
             'transaction_type': 'In'})

        for purchase_order in self:
            for order_line in purchase_order.purchase_order_line_ids:
                self.env['stock.move.ept'].create(
                    {'product_id': order_line.product_id.id, 'uom_id': order_line.uom_id.id,
                     'qty_to_deliver': order_line.quantity,
                     # 'qty_delivered': order_line.quantity,
                     'purchase_line_id': self.id,
                     'source_location_id': vendor_location.id,
                     'picking_id': new_incoming_shipment.id,
                     'destination_location_id': self.warehouse_id.stock_location_id.id})
