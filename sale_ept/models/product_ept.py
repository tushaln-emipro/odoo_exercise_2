from odoo import api, fields, models, _


class Product(models.Model):
    _name = "product.ept"
    _description = "Product"

    name = fields.Char(string="Name", help="Product's Name", required=True)
    sku = fields.Char(string="SKU", help="Product's SKU", required=True)
    weight = fields.Float(string="Weight", default=0.0, help="Product's Weight")
    length = fields.Float(string="Length", default=0.0, help="Product's Length")
    volume = fields.Float(string="Volume", default=0.0, help="Product's Volume")
    width = fields.Float(string="Width", default=0.0, help="Product's Width")
    barcode = fields.Char(string="Barcode", help="Product's Barcode")
    product_type = fields.Selection(string="Product Type",
                                    selection=[('Storable', 'Storable'), ('Consumable', 'Consumable'),
                                               ('Service', 'Service')], help="Product's Type")
    sale_price = fields.Float(string="Sale Price", default=1.00, help="Product's Sale Price")
    cost_price = fields.Float(string="Cost Price", default=1.00, help="Product's Cost Price")
    category_id = fields.Many2one(comodel_name='product.category.ept', string='Category', help="Category")
    uom_id = fields.Many2one(comodel_name='product.uom.ept', string='UOM', help="UOM")
    description = fields.Char(string="Description", help="Product's Description")
    product_stock = fields.Float(string="Product Stock", compute="compute_product_stock_nonstore",
                                 store=False, default=0.0, help="Stock Product")
    tax_ids = fields.Many2many('account.tax.ept', 'account_product_ref', 'product_id', 'account_id',
                               string='Customer Taxes', help="Customer Taxes")

    def compute_product_stock_nonstore(self):
        self.product_stock = 0
        location_id = self._context.get('location_id')
        stock_moves = self.env['stock.move.ept'].search([('state', '=', 'done')])
        if location_id:
            for products in self:
                total_stock = 0
                total_stock += sum(
                    stock_moves.filtered(lambda e: e.destination_location_id.id == location_id and
                                                   e.product_id.id == products.id).mapped('qty_delivered'))
                total_stock -= sum(
                    stock_moves.filtered(lambda e: e.source_location_id.id == location_id and
                                                   e.product_id.id == products.id).mapped('qty_delivered'))
                products.product_stock = total_stock
        else:
            warehouses = self.env['stock.warehouse.ept'].search([])
            for products in self:
                total_stock = 0
                for warehouse in warehouses:
                    total_stock += sum(
                        stock_moves.filtered(lambda e: e.destination_location_id.id == warehouse.stock_location_id.id
                                                       and e.product_id.id == products.id).mapped('qty_delivered'))
                    total_stock -= sum(
                        stock_moves.filtered(lambda e: e.source_location_id.id == warehouse.stock_location_id.id
                                                       and e.product_id.id == products.id).mapped('qty_delivered'))
                products.product_stock = total_stock

    def action_set_stock_update(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale_ept.action_stock_update_link")
        return action

    # def get_stock_moves_destination_location(self, product_id, location_id):
    #     return self.env['stock.move.ept'].search(
    #         [('destination_location_id.id', '=', location_id), ('product_id', '=', product_id), ('state', '=', 'done')])
    #
    # def get_stock_moves_source_location(self, product_id, location_id):
    #     return self.env['stock.move.ept'].search(
    #         [('source_location_id.id', '=', location_id), ('product_id', '=', product_id), ('state', '=', 'done')])

    # for stock_move in self.get_stock_moves_destination_location(products.id, location_id):
    #     total_stock += stock_move.qty_delivered
    # for stock_move in self.get_stock_moves_source_location(products.id, location_id):
    #     total_stock -= stock_move.qty_delivered
