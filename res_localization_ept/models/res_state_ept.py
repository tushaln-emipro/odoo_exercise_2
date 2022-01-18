from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class State(models.Model):
    _name = "res.state.ept"
    _description = "State"

    name = fields.Char(string="State", help="State Name")
    code = fields.Char(string="Short Code", help="State Short Code")
    country_id = fields.Many2one(comodel_name='res.country.ept', string="Country", help='Many2one of Country')
    city_ids = fields.One2many(comodel_name="res.city.ept", inverse_name="state_id", string="City",
                               help="One2many of City")

    @api.constrains('code')
    def check_state_code(self):
        if self.search([('id', '!=', self.id), ('code', '=', self.code)]):
            raise ValidationError('State Code Already Exist')

    # def set_country_details(self):
    #     # new_country = self.env['res.country.ept'].create({'name': 'USA', 'code': 'USA'})
    #     # new_country = self.env['res.country.ept'].create([{'name': 'US1', 'code': 'US1'},{'name': 'UK', 'code': 'UK'}])
    #     # new_state = self.env['res.state.ept'].create({'name': 'US', 'code': 'US', 'country_id': new_country.id})
    #
    #     # countries = self.env['res.country.ept'].search([('code','=','1 : emipro')])
    #     # is_wirte = countries.write({'code':'1'})
    #
    #     # is_wirte = self.country_id.write({'code': '2'})
    #
    #     new_state = self.env['res.state.ept'].create({'name': '001', 'code': '001'})
    #     new_record = new_state.copy()
    #     print(new_record)
    #
    # # args = ['|',['name','ilike',args[0][2]],['code','ilike',args[0][2]]]
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     new_args = []
    #     if args:
    #         if args[0][0] == 'name':
    #             new_args = ['|', ('name', 'ilike', args[0][2]), ('code', 'ilike', args[0][2])]
    #     else:
    #         new_args = args
    #
    #     return super(State, self).search(new_args, offset=offset, limit=limit, order=order, count=count)
    #
    # def copy(self, defalut=None):
    #     defalut = {'name': self.name + '- Copy'}
    #     return super(State, self).copy(defalut)
