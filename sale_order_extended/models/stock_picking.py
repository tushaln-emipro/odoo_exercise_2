from odoo import api, fields, models, _


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def action_perform_validate(self):
        """
           This method for Validate the delivery orders
           :return: return res as per got by button_validate
        """
        res = self.button_validate()
        return res
