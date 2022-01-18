from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    history_unit_price = fields.Float(string="History Unit Price", default=0.0, help="History Unit Price")

    @api.onchange('product_id')
    def set_history_unit_price(self):
        """
        This method for to be set history_unit_price as per last confirm order's Price Unit of selected Customer.
        :return: not any return
        """
        if self.order_id.partner_id.id and self.product_id.id:
            # query = """SELECT sol.price_unit
            #             FROM purchase_order so
            #             JOIN purchase_order_line sol ON sol.order_id = so.id
            #             WHERE so.partner_id = """ + str(self.order_id.partner_id.id) + """
            #             AND so.state = 'purchase' AND sol.product_id = """ + str(self.product_id.id) + """
            #             ORDER BY so.id DESC LIMIT 1;"""
            # self._cr.execute(query)
            # last_confirm_order = self.env.cr.dictfetchall()
            # if last_confirm_order:
            #     self.history_unit_price = last_confirm_order[0]['price_unit']

            _last_confirm_order = self.env['purchase.order.line'].search(
                [('product_id', '=', self.product_id.id), ('state', '=', 'purchase'),
                 ('order_id.partner_id.id', '=', self.order_id.partner_id.id)], order='id DESC', limit=1)

            if _last_confirm_order:
                self.history_unit_price = _last_confirm_order.price_unit
