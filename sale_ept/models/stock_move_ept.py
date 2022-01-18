from odoo import api, fields, models, _


class StockMove(models.Model):
    _name = "stock.move.ept"
    _description = "Stock Move"

    name = fields.Char(string="Name", help="Stock Move Name")
    product_id = fields.Many2one(comodel_name='product.ept', string="Product", help="Product")
    uom_id = fields.Many2one(comodel_name='product.uom.ept', string="UOM", help="UOM")
    source_location_id = fields.Many2one(comodel_name='stock.location.ept', string="Source Location",
                                         help="Source Location")
    destination_location_id = fields.Many2one(comodel_name='stock.location.ept', string="Destination Location",
                                              help="Destination Location")
    qty_to_deliver = fields.Float(string="Demand", readonly=True, help="Demand")
    qty_delivered = fields.Float(string="Done Quantities", help="Done Quantities")
    state = fields.Selection(string="State", help="State of the Stock Picking", default='draft',
                             selection=[('draft', 'draft'), ('done', 'done'), ('cancelled', 'cancelled')])
    sale_line_id = fields.Many2one(comodel_name='sale.order.line.ept', string="Order Line", help="Sale Order Line")
    purchase_line_id = fields.Many2one(comodel_name='purchase.order.line.ept', string="Purchase Line",
                                       help="Purchase Order Line")
    stock_inventory_id = fields.Many2one(comodel_name='stock.inventory.ept', string="Stock Inventory",
                                         help="Stock Inventory")
    picking_id = fields.Many2one(comodel_name='stock.picking.ept', string="Stock Picking", help="Stock Picking")

