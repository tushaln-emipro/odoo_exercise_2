from odoo import api, fields, models, _


class StockLocation(models.Model):
    _name = "stock.location.ept"
    _description = "Stock Location"

    name = fields.Char(string="Name", help="Stock Location Name", required=True)
    parent_id = fields.Many2one(comodel_name='stock.location.ept', string="Parent", help="Parent Of Stock Location")
    location_type = fields.Selection(string="Location Type", help="Location Type",
                                     selection=[('Vendor', 'Vendor'), ('Customer', 'Customer'),
                                                ('Internal', 'Internal'), ('Inventory Loss', 'Inventory Loss'),
                                                ('Production', 'Production'), ('Transit', 'Transit'), ('View', 'View')])
    is_scrap_location = fields.Boolean(string="Is Scrap Location", help="Is Scrap Location")

