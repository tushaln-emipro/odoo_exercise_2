from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MergeOrders(models.TransientModel):
    _name = "merge.sale.order"
    _description = "Merge Sales Orders"

    merge_options = fields.Selection(
        selection=[('1', 'Merge orders and create new order from selected orders and cancel all the orders')
            , ('2', 'Merge orders and create new order from selected orders and delete all the orders')
            , ('3', 'Merge orders into existing order and cancel remaining orders')
            , ('4', 'Merge orders into existing order and delete remaining orders')],
        string="Merge with options", help="Employee Gender")

    def selected_orders(self):
        return [('id', 'in', self.env.context.get('active_ids'))]

    selected_orders = fields.Many2one(comodel_name="sale.order", domain=selected_orders,
                                      string="Selected orders", help="Selected orders")

    @api.model
    def default_get(self, fields):
        """
        This method overrides checking some conditions before opening the Marge Sales Orders wizard form.
        :return: res return as per getting from the super.
        """
        res = super(MergeOrders, self).default_get(fields)
        sales_orders = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        if sales_orders.filtered(lambda so: so.state != 'draft'):
            raise ValidationError('Only draft orders can be marge.')
        if len(set(sales_orders.partner_id.ids)) > 1:
            raise ValidationError('Partners must be same.')
        return res

    def marge_order(self):
        """
        This method for the process of the Marge sale orders
        :return:not any return
        """
        if not self.merge_options:
            raise ValidationError('Please select option.')

        if self.merge_options in ('3', '4') and not self.selected_orders:
            raise ValidationError('Please select order.')

        order_ids = self.env.context.get('active_ids')
        self.create_write_sale_order(order_ids, self.merge_options)

    def create_write_sale_order(self, order_ids, option):
        """
        This method for Merge orders and creating new orders & orders into existing orders from selected orders
        and cancel/delete remaining orders as the selected option.
        :param order_ids: ids of SO from the selected in the tree view
        :param option: SO as selected from the M2O field
        :return: not any return   ...
        """
        orders = self.get_sales_orders(order_ids)
        _dict = dict()
        for line in orders.order_line:
            product_qty = line.product_uom_qty
            if _dict.get((line.product_id.id, line.price_unit, tuple(line.tax_id.ids)), False):
                product_qty += _dict.get((line.product_id.id, line.price_unit, tuple(line.tax_id.ids))).get(
                    'product_uom_qty')

            _dict.update({(line.product_id.id, line.price_unit, tuple(line.tax_id.ids)):
                              {'product_id': line.product_id.id, 'name': line.product_id.name,
                               'product_uom_qty': product_qty, 'product_uom': line.product_uom.id,
                               'price_unit': line.price_unit, 'tax_id': line.tax_id.ids}})

        order_line = [(0, 0, updated_dict[1]) for updated_dict in _dict.items()]
        if order_line:
            if option in ('1', '2'):
                sale_order_val = []
                for order in orders:
                    sale_order_val.append({'partner_id': order.partner_id.id, 'pricelist_id': order.pricelist_id.id,
                                           'company_id': order.company_id.id, 'order_line': order_line})
                    break
                self.env['sale.order'].create(sale_order_val)
            else:
                self.selected_orders.order_line = [(5, 0, 0)]
                self.selected_orders.write({'order_line': order_line})

        if option == '1':
            orders.action_cancel()
        if option == '2':
            orders.unlink()
        if option == '3':
            orders.filtered(lambda so: so.id != self.selected_orders.id).action_cancel()
        if option == '4':
            orders.filtered(lambda so: so.id != self.selected_orders.id).unlink()

    def get_sales_orders(self, order_ids):
        """
        This method for getting sales orders as per selected from the tree view
        :param order_ids: ids of SO from the selected in the tree view
        :return: searched SO as per matched ids in order_ids
        """
        return self.env['sale.order'].search([('id', 'in', order_ids)])
