import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import random


class CRMLead(models.Model):
    _name = "crm.lead.ept"
    _description = "CRM Lead"

    partner_id = fields.Many2one(comodel_name='res.partner.ept', string="Partner", help="Partner")
    order_ids = fields.One2many(comodel_name='sale.order.ept', inverse_name="id", string="Orders", help="Orders")
    team_id = fields.Many2one(comodel_name='crm.team.ept', string="Team", help="CRM Team")
    user_id = fields.Many2one(comodel_name='res.users', string="User", help="User")
    lead_line_ids = fields.One2many(comodel_name='crm.lead.line.ept', inverse_name="lead_id", string="Lead Lines",
                                    help="Lead Lines")
    state = fields.Selection(string="State", help="State's of Lead", default="New",
                             selection=[('New', 'New'), ('Qualified', 'Qualified'), ('Proposition', 'Proposition'),
                                        ('Won', 'Won'), ('Lost', 'Lost')])
    won_date = fields.Date(string="Won Date", help="Won Date", readonly=True)
    lost_reason = fields.Char(string="Lost reason", help="Lost reason")
    next_followup_date = fields.Date(string="Next Follow Date", help="Next Follow Date")

    partner_name = fields.Char(string="Partner Name", help="Name of Partner")
    partner_email = fields.Char(string="Partner Email", help="Email of Partner")
    partner_country_id = fields.Many2one(comodel_name='res.country.ept', string="Country", help="Country of Partner")
    partner_state_id = fields.Many2one(comodel_name='res.state.ept', string="State", help="State of Partner")
    partner_city_id = fields.Many2one(comodel_name='res.city.ept', string="City", help="City of Partner")
    partner_phone_no = fields.Char(string="Phone No", help="Phone No of Partner")

    def generate_customer(self):
        if not self.partner_name:
            raise ValidationError('Partner Name Required')
        else:
            new_partner = self.env['res.partner.ept'].create(
                {'name': self.partner_name, 'email': self.partner_email, 'active': True,
                 'country': self.partner_country_id, 'state': self.partner_state_id, 'city': self.partner_city_id,
                 'phone': self.partner_phone_no})
            self.partner_id = new_partner.id

    def action_set_qualified(self):
        self.validation_partner_product()
        self.state = 'Qualified'

    def action_set_proposition(self):
        self.validation_partner_product()
        self.state = 'Proposition'

    def action_set_won(self):
        self.validation_partner_product()
        self.state = 'Won'
        self.won_date = datetime.datetime.today()

    def action_set_lost(self):
        self.validation_partner_product()
        self.state = 'Lost'

    def action_generate_sales_quotation(self):
        self.validation_partner_product()

        partner_invoice_id = self.partner_id
        partner_shipping_id = self.partner_id
        if self.partner_id.child_ids.filtered(lambda e: e.address_type == 'Invoice'):
            partner_invoice_id = self.partner_id.child_ids.filtered(lambda e: e.address_type == 'Invoice')[0]
        if self.partner_id.child_ids.filtered(lambda e: e.address_type == 'Shipping'):
            partner_shipping_id = self.partner_id.child_ids.filtered(lambda e: e.address_type == 'Shipping')[0]
        order_no = random.randint(100, 500)

        new_sale_order = self.env['sale.order.ept'].create(
            {'order_no': order_no, 'partner_id': self.partner_id.id, 'partner_invoice_id': partner_invoice_id.id,
             'partner_shipping_id': partner_shipping_id.id, 'salesperson': self.user_id.id})
        if new_sale_order:
            for lead_line in self.lead_line_ids:
                self.env['sale.order.line.ept'].create(
                    {'order_no': new_sale_order.id, 'product_id': lead_line.product_id.id,
                     'quantity': lead_line.expected_sell_qty, 'unit_price': lead_line.product_id.sale_price
                        , 'uom_id': lead_line.uom_id.id})

    def validation_partner_product(self):
        if not self.partner_id:
            raise ValidationError('Please Select Partner')
        if len(self.lead_line_ids) == 0:
            raise ValidationError('Please Add Product')
