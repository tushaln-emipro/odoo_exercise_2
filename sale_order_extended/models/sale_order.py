from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    crm_lead_opportunity_id = fields.Many2one(comodel_name="crm.lead", string="CRM Lead Opportunity",
                                              help="CRM Lead Ref", readonly=True)
    is_all_picking_completed = fields.Boolean(string="Is all picking completed", help="Is all picking completed",
                                              store=False, compute="_find_computed", search="_search_is_computed")
    product_tmpl_ids = fields.Many2many("product.template", string="Product Template", help="Product Template")
    profit_value = fields.Float(string="Profit value", help="Profit value", store=False, default=0.0,
                                compute="compute_profit_value")
    profit_margin = fields.Float(string="Profit margin", help="Profit margin", store=False, default=0.0,
                                 compute="compute_profit_margin")

    def action_confirm(self):
        """
           This method is override for the shipping product add automatically to sale.order.line model
           :return: return res as per got by super
        """

        res = super(SaleOrder, self).action_confirm()

        # Add Shipping product if is available
        product_shipping_id = self.env.ref('sale_order_extended.product_shipping_extended').id
        if product_shipping_id and not self.order_line.filtered(lambda line: line.product_id.id == product_shipping_id):
            self.env['sale.order.line'].create({'order_id': self.id, 'product_id': product_shipping_id})
        return res

    def action_manage_deposits(self):
        """
        This method for the Manage Deposits. If there is any, then that deposit product should be added to the order line
        :return: not any return
        """
        deposit_products = self.order_line.filtered(lambda line: line.product_id.deposit_product_id.id > 1)
        if deposit_products:
            new_order_line = []
            if len(deposit_products) > 1:
                for deposits in deposit_products:
                    if not self.order_line.filtered(
                            lambda line: line.product_id.id == deposits.product_id.deposit_product_id.id):
                        new_order_line.append(self.make_dict_order_line(deposits))
            else:
                if not self.order_line.filtered(
                        lambda line: line.product_id.id == deposit_products.product_id.deposit_product_id.id):
                    new_order_line.append(self.make_dict_order_line(deposit_products))

            self.env['sale.order.line'].create(new_order_line)

    def make_dict_order_line(self, deposit_products):
        return {'order_id': self.id, 'product_id': deposit_products.product_id.deposit_product_id.id,
                'product_uom_qty': deposit_products.product_id.deposit_product_qty}

    def action_scan_all(self):
        """
        This method for scan all order lines and got products from them state not done or cancelled
        :return: return action
        """
        action = {
            'name': _('Sale Order Lines'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'sale.order.line',
            'domain': [('order_id', '!=', self.id), ('state', 'not in', ('done', 'cancel'))],
        }
        return action

    def action_perform_confirm(self):
        """
               This method for performing Confirm the sales order
               :return: not any return
        """
        if self.order_line.filtered(lambda line: line.warehouse_id.id == 0):
            for order_line in self.order_line:
                if not order_line.warehouse_id:
                    order_line.warehouse_id = self.warehouse_id.id

    def _find_computed(self):
        """
        This method is completed and all the pickings are validated then it should be marked as True
        :return: not any return
        """
        self.is_all_picking_completed = False
        res = self.get_sale_ids()
        order_ids = [r['sale_id'] for r in res]
        for order in self:
            if order.id in order_ids:
                order.is_all_picking_completed = True

    def _search_is_computed(self, operator, value):
        """
               This method search all pickings of state in done or cancel
               :return: return event_ids is all picking_ids of state is done
        """
        res = self.get_sale_ids()
        ids = []
        if res:
            ids = [r['sale_id'] for r in res]
        return [('id', 'in', ids)]

    def get_sale_ids(self):
        """
        This method for getting sale_ids of all orders are done or cancel
        :return: return result as per select statement
        """
        query = """SELECT B.sale_id FROM sale_order A 
                        JOIN stock_picking B ON B.sale_id = A.id 
                        WHERE B.state in ('done','cancel') 
                        AND NOT EXISTS (SELECT sale_id FROM stock_picking WHERE state IN ('draft','waiting','confirmed','assigned') AND sale_id = B.sale_id)                     
                        GROUP BY B.sale_id"""
        self._cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.onchange('partner_id')
    def reset_history_unit_price(self):
        """
        This method for to be reset history_unit_price if changed the Customer.
        :return: not any return
        """
        if self.partner_id.id:
            self.order_line.history_unit_price = 0.0

    @api.onchange('product_tmpl_ids')
    def product_tmpl_ids_onchange(self):
        """
         When onchange is fired add all the variants of that template into sale.order.line
         check if stock of those variants is available or not, skip the variants whose stock is not available and don’t
         add it to the sale.order.line Stock should be checked for warehouse set in the sale.order
        :return: not any return
        """

        if self.pricelist_id and self.partner_id and self.product_tmpl_ids:
            order_line = []
            pricelist = self.env['product.pricelist'].browse(self.pricelist_id.id)
            variants = self.env['product.product'].search([('product_tmpl_id', 'in', self.product_tmpl_ids.ids)])
            for variant in variants:
                qty_availabe = variant.with_context(location=self.warehouse_id.id)._product_available(variant)
                if qty_availabe.get(variant.id)['qty_available'] > 0:
                    res = pricelist.get_products_price(variant, [1.0], self.partner_id, False, False)
                    order_line.append((0, 0, {'product_id': variant.id, 'product_uom': variant.uom_id.id,
                                              'price_unit': res.get(variant.id)}))

            if order_line:
                self.order_line = [(5, 0, 0)]  # remove all order lines
                self.write({'order_line': order_line})

    @api.depends('order_line')
    def compute_profit_value(self):
        self.profit_value = 0
        for line in self.order_line:
            self.profit_value += (line.price_unit - line.product_id.standard_price)

    @api.depends('order_line')
    def compute_profit_margin(self):
        self.profit_margin = 0

    def action_merge_sales_orders(self):
        """
        This method for open wizard form of Marge Sales Orders
        :return: as action return as per set keys & values.
        """
        if self.filtered(lambda so: so.state != 'draft'):
            raise ValidationError('Only draft orders can be marge.')
        if len(set(self.partner_id.ids)) > 1:
            raise ValidationError('Partners must be same.')

        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.env.context.get('active_ids')
        ctx['active_model'] = 'sale.order'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'merge.sale.order',
            'name': 'Marge Sales Orders',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
            'views': [(self.env.ref('sale_order_extended.view_merge_sales_orders_form').id, "form")],
        }
