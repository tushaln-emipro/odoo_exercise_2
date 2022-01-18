from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"

    @api.onchange('partner_id')
    def reset_history_unit_price(self):
        """
        This method for to be reset history_unit_price if changed the Customer.
        :return: not any return
        """
        if self.partner_id.id:
            self.order_line.history_unit_price = 0.0
