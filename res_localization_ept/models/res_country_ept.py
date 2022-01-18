from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Country(models.Model):
    _name = "res.country.ept"
    _description = "Country"

    name = fields.Char(string="Country", help="Country Name")
    code = fields.Char(string="Short Code", help="Country Short Code")
    state_ids = fields.One2many(comodel_name='res.state.ept', inverse_name="country_id", string='State',
                                help="One2many of state")

    _sql_constraints = [('unique_code', 'unique(code)', 'The Country Code must be unique')]

    # _sql_constraints = [('unique_name', 'unique(name)', 'The Country name must be unique')]

    # @api.constrains('code')
    # def check_country_code(self):
    #     if self.search([('id', '!=', self.id), ('code', '=', self.code)]):
    #         raise ValidationError('Country Code Already Exist')

    # @api.model
    # def create(self, vals):
    #     vals.update({'code': vals['code'] + ' : emipro'})
    #     new_record = super(Country, self).create(vals)
    #     return  new_record
