from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class City(models.Model):
    _name = "res.city.ept"
    _description = "City"

    name = fields.Char(string="City", help="City Name")
    code = fields.Char(string="Short Code", help="City Short Code")
    state_id = fields.Many2one(comodel_name="res.state.ept",string="State")

    @api.constrains('code')
    def check_city_code(self):
        if self.search([('id', '!=', self.id), ('code', '=', self.code)]):
            raise ValidationError('City Code Already Exist')