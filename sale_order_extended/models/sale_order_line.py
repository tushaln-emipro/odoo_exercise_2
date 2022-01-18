from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    warehouse_ept_id = fields.Many2one(comodel_name='stock.warehouse', string="Stock Warehouse", help="Stock Warehouse")
    history_unit_price = fields.Float(string="History Unit Price", default=0.0, help="History Unit Price")

    def _prepare_procurement_values(self, group_id=False):
        """
        This method is override to be set new warehouse_id as per selected in Order Lines
        :param group_id:
        :return: updated values related to warehouse_id key if get new warehouse_id
        """
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.warehouse_ept_id.id:
            values["warehouse_id"] = self.warehouse_ept_id
        return values

    @api.onchange('product_id')
    def set_history_unit_price(self):
        """
        This method for to be set history_unit_price as per last confirm order's Price Unit of selected Customer.
        :return: not any return
        """
        if self.order_id.partner_id.id and self.product_id.id:
            # query = """SELECT sol.price_unit
            #         FROM sale_order so
            #         JOIN sale_order_line sol ON sol.order_id = so.id
            #         WHERE so.partner_id = """ + str(self.order_id.partner_id.id) + """
            #         AND so.state = 'sale' AND sol.product_id = """ + str(self.product_id.id) + """
            #         ORDER BY so.id DESC LIMIT 1;"""
            # self._cr.execute(query)
            # last_confirm_order = self.env.cr.dictfetchall()
            # if last_confirm_order:
            #     self.history_unit_price = last_confirm_order[0]['price_unit']

            _last_confirm_order = self.env['sale.order.line'].search(
                [('product_id', '=', self.product_id.id), ('state', '=', 'sale'),
                 ('order_id.partner_id.id', '=', self.order_id.partner_id.id)], order='id DESC', limit=1)

            if _last_confirm_order:
                self.history_unit_price = _last_confirm_order.price_unit
