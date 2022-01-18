from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime


class StockInventory(models.Model):
    _name = "stock.inventory.ept"
    _description = "Stock Inventory"

    name = fields.Char(string="Name", help="Stock Inventory Name", required=True)
    state = fields.Selection(string="State", help="State's of Stock Inventory", default="draft",
                             selection=[('draft', 'draft'), ('in-progress', 'in-progress'),
                                        ('done', 'done'), ('cancelled', 'cancelled')])
    location_id = fields.Many2one(comodel_name='stock.location.ept', string='Location', help="Location", required=True)
    inventory_date = fields.Date(string="Inventory Date", help="Inventory Date", default=datetime.datetime.today())
    inventory_line_ids = fields.One2many(comodel_name='stock.inventory.line.ept', inverse_name="inventory_id",
                                         string='Inventory Line', help="Inventory Line")
    stock_move_ids = fields.One2many(comodel_name='stock.move.ept', inverse_name="id", string='Moves', help="Moves")

    def action_set_start_inventory(self):
        inventory_line = []
        obj_products = self.env['product.ept'].search([]).with_context(location_id=self.location_id.id)
        for product in obj_products:
            inventory_line.append(
                {'product_id': product.id, 'available_qty': product.product_stock, 'inventory_id': self.id})

        if not self.env['stock.inventory.line.ept'].search([('inventory_id', '=', self.id)]):
            self.env['stock.inventory.line.ept'].create(inventory_line)
        else:
            self.env['stock.inventory.line.ept'].write(inventory_line)
        self.state = 'in-progress'

    def action_set_validate(self):
        adjustment_location = self.env['stock.location.ept'].search([('location_type', '=', 'Inventory Loss')], limit=1)
        if not adjustment_location:
            raise ValidationError('Adjustment Location not created')

        stock_moves = []
        for inventory_lines in self.inventory_line_ids:
            if inventory_lines.difference != 0:
                diff_qty = 0
                source_location_id = False
                destination_location_id = False
                if inventory_lines.difference > 0:
                    diff_qty = inventory_lines.difference
                    source_location_id = adjustment_location.id
                    destination_location_id = self.location_id.id
                else:
                    diff_qty = abs(inventory_lines.difference)
                    source_location_id = self.location_id.id
                    destination_location_id = adjustment_location.id

                stock_moves.append(
                    {'product_id': inventory_lines.product_id.id, 'uom_id': inventory_lines.product_id.uom_id.id,
                     'qty_delivered': diff_qty, 'qty_to_deliver': diff_qty, 'stock_inventory_id': self.id,
                     'state': 'done',
                     'source_location_id': source_location_id, 'destination_location_id': destination_location_id})

        if stock_moves:
            self.env['stock.move.ept'].create(stock_moves)
        self.state = 'done'

    def action_set_cancelled(self):
        self.state = 'cancelled'
