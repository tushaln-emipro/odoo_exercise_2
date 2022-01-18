from odoo import api, fields, models, _


class Partner(models.Model):
    _name = "res.partner.ept"
    _description = "Partner"

    name = fields.Char(string="Name", help="Partner's Name")
    street1 = fields.Char(string="Street 1", help="Partner's Street 1")
    street2 = fields.Char(string="Street 2", help="Partner's Street 2")
    country = fields.Many2one(comodel_name='res.country.ept', string="Country", help="Partner Country")
    state = fields.Many2one(comodel_name='res.state.ept', string="Country", help="Partner State")
    city = fields.Many2one(comodel_name='res.city.ept', string="Country", help="Partner City")
    zip_code = fields.Char(string="Zip Code", help="Partner's Zip Code")
    email = fields.Char(string="Email", help="Partner's Email")
    mobile = fields.Char(string="Mobile", help="Partner's Mobile")
    phone = fields.Char(string="Phone", help="Partner's Phone")
    photo = fields.Image(string="Photo", help="Partner's Photo")
    website = fields.Char(string="Website", help="Partner's Website")
    active = fields.Boolean(string="Active", help="Active")
    parent_id = fields.Many2one(comodel_name='res.partner.ept', string="Parent", help="Parent")
    child_ids = fields.One2many(comodel_name='res.partner.ept',inverse_name="parent_id", string='Child', help="Child")
    address_type = fields.Selection(string="Address Type", help="Address Type",
                                    selection=[('Invoice', 'Invoice'), ('Shipping', 'Shipping'),
                                               ('Contact', 'Contact')])
