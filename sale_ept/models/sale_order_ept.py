from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime


class SaleOrder(models.Model):
    _name = "sale.order.ept"
    _description = "Sale Order"

    order_no = fields.Char(string="Order No", help="Order No", required=True)
    partner_id = fields.Many2one(comodel_name='res.partner.ept', string="Customer", help="Customer")
    partner_invoice_id = fields.Many2one(comodel_name='res.partner.ept', string="Invoice Customer",
                                         help="Invoice Customer")
    partner_shipping_id = fields.Many2one(comodel_name='res.partner.ept', string="Shipping Customer",
                                          help="Shipping Customer")
    order_date = fields.Date(string="Sale Order Date", help="Sale Order Date", default=datetime.datetime.today())
    order_line = fields.One2many(comodel_name='sale.order.line.ept', inverse_name="order_no", string='Order Line',
                                 help="Order Line")
    salesperson = fields.Many2one(comodel_name='res.users', string="Salesperson", help=" Salesperson")
    state = fields.Selection(string="State", help="State's of order", default="draft",
                             selection=[('draft', 'draft'), ('confirmed', 'confirmed'),
                                        ('done', 'done'), ('cancelled', 'cancelled')])
    total_weight = fields.Float(string="Total Weight", compute="compute_total_weight_volume_nonstore",
                                store=False, default=0.0, help="Total Weight")
    total_volume = fields.Float(string="Total Volume", compute="compute_total_weight_volume_nonstore",
                                store=False, default=0.0, help="Total Volume")
    order_total = fields.Float(string="Order Total", compute="compute_order_total_store",
                               store=True, default=0.0, help="Order Total")
    lead_id = fields.Many2one(comodel_name='crm.lead.ept', string="Lead", help="Lead")

    warehouse_id = fields.Many2one(comodel_name='stock.warehouse.ept', string="Stock Warehouse", help="Stock Warehouse")
    picking_ids = fields.One2many(comodel_name='stock.picking.ept', inverse_name="sale_order_id", string='Pickings',
                                  help="Pickings", readonly=True)
    total_tax = fields.Float(string="Total Tax", compute="compute_total_tax", store=True, default=0.0, help="TotalTax")
    amount_untaxed = fields.Float(string="Total UnTax", compute="compute_total_untax", store=False, default=0.0,
                                  help="Total UnTax")
    total_amount = fields.Float(string="Total Amount", compute="compute_total_amount", store=True, default=0.0,
                                help="Total Amount")

    @api.depends('order_line')
    def compute_total_weight_volume_nonstore(self):
        for sale_order in self:
            obj_weight = 0
            obj_volume = 0
            for order_line in sale_order.order_line:
                obj_weight += order_line.product_id.weight
                obj_volume += order_line.product_id.volume
            sale_order.total_weight = obj_weight
            sale_order.total_volume = obj_volume

    @api.depends('order_line')
    def compute_order_total_store(self):
        for sale_order in self:
            obj_order = 0
            for order_line in sale_order.order_line:
                obj_order += order_line.subtotal_without_tax
            sale_order.order_total = obj_order

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        # self.partner_invoice_id = self.partner_id.child_ids.search([('address_type', '=', 'Invoice')], limit=1)
        # self.partner_shipping_id = self.partner_id.child_ids.search([('address_type', '=', 'Shipping')], limit=1)
        if self.partner_id.child_ids.filtered(lambda e: e.address_type == 'Invoice'):
            self.partner_invoice_id = self.partner_id.child_ids.filtered(lambda e: e.address_type == 'Invoice')[0]
        if self.partner_id.child_ids.filtered(lambda e: e.address_type == 'Shipping'):
            self.partner_shipping_id = self.partner_id.child_ids.filtered(lambda e: e.address_type == 'Shipping')[0]

    def action_set_sale_order_confirm(self):

        if not self.warehouse_id.stock_location_id.id:
            raise ValidationError('Stock Warehouse is not selected')

        customer_location = self.env['stock.location.ept'].search([('location_type', '=', 'Customer')], limit=1)
        if not customer_location:
            raise ValidationError('Customer location not created')

        warehouses = list(dict.fromkeys([self.order_line.warehouse_id]))
        delivery_order = []
        stock_moves = []
        if warehouses:
            for warehouse in warehouses[0].ids:
                for order_line in self.order_line:
                    if (order_line.warehouse_id.id == warehouse):
                        order_line.state = 'confirmed'
                        if (warehouse == self.warehouse_id.id):
                            stock_moves.append(self.make_stock_moves(order_line, customer_location))
                        else:
                            delivery_order.append(self.make_delivery_order(self.make_stock_moves(order_line, customer_location)))

        if len(self.order_line.filtered(lambda e: e.warehouse_id.id == 0).ids) != 0:
            for order_line in self.order_line.filtered(lambda e: e.warehouse_id.id == 0):
                order_line.state = 'confirmed'
                order_line.warehouse_id = self.warehouse_id.id
                stock_moves.append(self.make_stock_moves(order_line, customer_location))

            delivery_order.append(self.make_delivery_order(stock_moves))

        self.state = 'confirmed'
        self.env['stock.picking.ept'].create(delivery_order)

    def make_stock_moves(self, order_line, customer_location):
        return (0, 0, {'product_id': order_line.product_id.id, 'uom_id': order_line.uom_id.id,
                       'qty_to_deliver': order_line.quantity, 'sale_line_id': order_line.id,
                       'source_location_id': order_line.warehouse_id.stock_location_id.id,
                       'destination_location_id': customer_location.id})

    def make_delivery_order(self, stock_moves):
        return {'name': self.env['ir.sequence'].next_by_code('picking.out') or _('New'),
                'partner_id': self.partner_id.id, 'sale_order_id': self.id,
                'transaction_type': 'Out', 'move_ids': stock_moves}

    def action_set_delivery_order(self):
        if len(self.picking_ids.ids) != 0:
            if len(self.picking_ids.ids) > 1:
                action = self.env["ir.actions.actions"]._for_xml_id("sale_ept.action_delivery_order_ept")
            else:
                action = self.env["ir.actions.actions"]._for_xml_id("sale_ept.action_delivery_order_ept")
                action.update({'views': [[self.env.ref('sale_ept.view_stock_picking_ept_form').id, 'form']],
                               'res_id': self.picking_ids.id})
            return action

    def action_set_stock_move(self):
        if len(self.picking_ids.move_ids.ids) != 0:
            if len(self.picking_ids.move_ids.ids) > 1:
                action = self.env["ir.actions.actions"]._for_xml_id("sale_ept.action_stock_move_ept")
                action.update({'views': [[self.env.ref('sale_ept.view_stock_move_ept_tree').id, 'tree']],
                               'domain': [('id', 'in', self.picking_ids.move_ids.ids)]})
            else:
                action = self.env["ir.actions.actions"]._for_xml_id("sale_ept.action_stock_move_ept")
                action.update({'views': [[self.env.ref('sale_ept.view_stock_move_ept_form').id, 'form']],
                               'res_id': self.picking_ids.move_ids.id})
            return action

    @api.depends('order_line')
    def compute_total_tax(self):
        self.total_tax = 0
        if self.order_line:
            for order_line in self.order_line:
                self.total_tax += order_line.subtotal_with_tax

    @api.depends('order_line')
    def compute_total_untax(self):
        self.amount_untaxed = 0
        if self.order_line:
            for order_line in self.order_line:
                self.amount_untaxed += order_line.subtotal_without_tax

    @api.depends('order_line')
    def compute_total_amount(self):
        self.total_amount = 0
        if self.order_line:
            for order_line in self.order_line:
                self.total_amount += (order_line.subtotal_without_tax + order_line.subtotal_with_tax)
