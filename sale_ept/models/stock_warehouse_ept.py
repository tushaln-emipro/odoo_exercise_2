from odoo import api, fields, models, _


class Warehouse(models.Model):
    _name = "stock.warehouse.ept"
    _description = "Warehouse"

    name = fields.Char(string="Name", help="Warehouse Name", required=True)
    code = fields.Char(string="Code", help="Warehouse Code", required=True)
    address_id = fields.Many2one(comodel_name='res.partner.ept', string="Address", help="Partner Address")
    stock_location_id = fields.Many2one(comodel_name='stock.location.ept', string="Stock Location",
                                        help="Stock Location")
    view_location_id = fields.Many2one(comodel_name='stock.location.ept', string="View Location",
                                       help="View Location")

    @api.model
    def create(self, vals):
        new_view_location = self.env['stock.location.ept'].create(
            {'name': 'View Location | ' + vals['code'], 'location_type': 'View'})
        new_stock_location = self.env['stock.location.ept'].create(
            {'name': 'Stock Location | ' + vals['code'], 'location_type': 'View', 'parent_id': new_view_location.id})
        vals['stock_location_id'] = new_stock_location.id
        vals['view_location_id'] = new_view_location.id
        new_record = super(Warehouse, self).create(vals)
        return new_record
