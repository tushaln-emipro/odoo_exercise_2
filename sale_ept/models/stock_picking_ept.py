from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime


class StockPicking(models.Model):
    _name = "stock.picking.ept"
    _description = "Stock Picking"

    name = fields.Char(string="Name", help="Stock Picking Name")
    partner_id = fields.Many2one(comodel_name='res.partner.ept', string="Partner", help="Partner")
    state = fields.Selection(string="State", help="State of the Stock Picking", default='draft',
                             selection=[('draft', 'draft'), ('done', 'done'), ('cancelled', 'cancelled')])
    sale_order_id = fields.Many2one(comodel_name='sale.order.ept', string="Sale Order", help="Sale Order")
    purchase_order_id = fields.Many2one(comodel_name='purchase.order.ept', string="Purchase Order",
                                        help="Purchase Order")
    transaction_type = fields.Selection(string="Transaction Type", help="Transaction Type",
                                        selection=[('In', 'In'), ('Out', 'Out')])
    move_ids = fields.One2many(comodel_name='stock.move.ept', inverse_name="picking_id", string='Move', help="Move")
    transaction_date = fields.Date(string="Transaction Date", help="Transaction Date",
                                   default=datetime.datetime.today())
    back_order_id = fields.Many2one(comodel_name='stock.picking.ept', string='Back Order', help="Back Order")

    @api.model_create_multi
    def create(self, vals):
        if len(vals) == 1:
            if vals['transaction_type'] == 'In':
                vals['name'] = self.env['ir.sequence'].next_by_code('picking.in') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('picking.out') or _('New')
        new_record = super(StockPicking, self).create(vals)
        return new_record

    def action_set_done(self):

        if all(x.qty_delivered == 0 for x in self.move_ids):
            raise ValidationError('All Done Quantities Are Zero')

        new_moves = []
        for stock_move in self.move_ids:
            _temp_qty_to_deliver = 0
            if stock_move.qty_delivered == 0:
                _temp_qty_to_deliver = stock_move.qty_to_deliver
            if abs(stock_move.qty_to_deliver - stock_move.qty_delivered) < stock_move.qty_to_deliver:
                _temp_qty_to_deliver = abs(stock_move.qty_to_deliver - stock_move.qty_delivered)
                stock_move.qty_to_deliver = stock_move.qty_delivered
            if _temp_qty_to_deliver != 0:
                new_moves.append(
                    (0, 0, {'product_id': stock_move.product_id.id, 'uom_id': stock_move.product_id.uom_id.id,
                            'source_location_id': stock_move.source_location_id.id,
                            'destination_location_id': stock_move.destination_location_id.id,
                            'qty_to_deliver': _temp_qty_to_deliver, 'sale_line_id': stock_move.sale_line_id.id,
                            'purchase_line_id': stock_move.purchase_line_id.id, 'picking_id': self.id}))

            stock_move.state = 'done'

        self.state = 'done'
        # self.env['stock.move.ept'].search([('qty_delivered', '=', 0), ('picking_id', '=', self.id)]).unlink()
        # I have used filtered because not getting records of qty_delivered = 0
        self.move_ids.filtered(lambda e: e.qty_delivered == 0).unlink()
        self.env['stock.picking.ept'].create({'partner_id': self.partner_id.id, 'sale_order_id': self.sale_order_id.id,
                                              'purchase_order_id': self.purchase_order_id.id,
                                              'transaction_type': self.transaction_type, 'move_ids': new_moves,
                                              'back_order_id': self.id})

    def action_set_cancelled(self):
        self.state = 'cancelled'
        for stock_move in self.move_ids:
            stock_move.state = 'cancelled'
            stock_move.qty_delivered = stock_move.qty_to_deliver
