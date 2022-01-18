from odoo import api, fields, models, _
import datetime


class PartnerLeadRel(models.Model):
    _name = "partner.lead.rel"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Partner Lead"

    name = fields.Char(string="Name", help="Name")
    from_date = fields.Date(string="From Date", help="From Date", default=datetime.datetime.today())
    to_date = fields.Date(string="To Date", help="To Date")
    partner_id = fields.Many2one(comodel_name='res.partner', string="Partner", help="Partner")
    partner_contact_ids = fields.Many2many("res.partner", string="Partner Contacts", compute="_compute_contact_ids",
                                           inverse="_inverse_contact_ids", help="Partner Contacts")
    salesperson_lead_count_ids = fields.One2many(comodel_name='salesperson.lead.count', inverse_name="lead_id",
                                                 string='Salesperson Lead Count', help="Salesperson Lead Count")

    lead_ids = fields.Many2many("crm.lead", string="Leads", help="Leads")
    total_revenue = fields.Float(string="Total Revenue",related='' , default=0.0, help="Total Revenue",
                                 compute='compute_total_revenue' )
    leads_count = fields.Integer("# Leads", compute='compute_leads_count')
    sale_order_count = fields.Integer("# Leads", compute='compute_sale_order_count')

    @api.model
    def create(self, vals):
        """
        This method is overridden for to be the set name by sequence
        :param vals: values of partner.lead.rel model
        :return: return new_record as per generated
        """
        vals['name'] = self.env['ir.sequence'].next_by_code('partner.lead.rel') or _('New')
        new_record = super(PartnerLeadRel, self).create(vals)
        return new_record

    @api.depends('partner_id')
    def _compute_contact_ids(self):
        """
        This method for getting Partner of which parent company is above selected partner_id
        :return: not any return
        """
        for partner in self:
            if partner.partner_id:
                    partner.partner_contact_ids = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id)])
            else:
                partner.partner_contact_ids = None

    def _inverse_contact_ids(self):
        """
        This method was created to make the editable field of partner_contact_ids
        :return:not any return
        """
        print(self.partner_contact_ids)

    def get_pipeline_details(self):
        """
        This method for creating line in salesperson_lead_count_ids by the fetch data of lead of
        those sales person associated with the leads of partner_id and partner_contact_ids
        :return:not any return
        """
        if self.partner_id:
            leads = self.get_leads()
            temp_lead_count = []
            if leads:
                for user_id in set(leads.user_id.ids):
                    temp_lead_count.append({'salesperson_id': user_id
                                               , 'total_pipelines': len(leads.filtered(lambda lead: lead.user_id.id == user_id and lead.type == 'opportunity'))
                                               , 'total_revenue': len(leads.filtered(lambda lead: lead.user_id.id == user_id and lead.won_status == 'won'))
                                               , 'total_quotations': len(leads.order_ids.filtered(lambda order: order.state == 'draft'))
                                               , 'total_sales_orders': len(leads.order_ids)
                                               , 'total_sales_orders_amounts': sum(leads.order_ids.filtered(lambda order:order).mapped('amount_total'))
                                               , 'lead_id': self.id
                                               , 'conversation_amount' : (self.total_revenue * sum(leads.order_ids.filtered(lambda order:order.state == 'sale').mapped('amount_total')) /100)
                                            })
                if temp_lead_count:
                    self.env['salesperson.lead.count'].create(temp_lead_count)

    def get_view_leads(self):
        """
        This method for display kanban and form view of pipeline/lead
        :return:action as per set domain
        """
        partner_ids = self.get_partner_ids()
        domain = [('type', '=', 'opportunity'),('partner_id', 'in', partner_ids)]
        if self.from_date:
            domain.append(('date_deadline', '>', self.from_date))
        if self.to_date:
            domain.append(('date_deadline', '<', self.to_date))

        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        action.update({
            'views' : [[self.env.ref('crm.crm_case_kanban_view_leads').id,'kanban'],[self.env.ref('crm.crm_lead_view_form').id,'form']]
            ,'domain':domain, 'context':{'default_type': 'opportunity'}
        })
        return action

    def compute_leads_count(self):
        """
        This method for to be set leads_count as per getting from crm.lead model as per partners selected.
        :return:not any return
        """
        self.leads_count = 0
        leads = self.get_leads()
        if leads:
            self.leads_count = len(leads.filtered(lambda lead: lead.type == 'opportunity'))

    def compute_sale_order_count(self):
        """
        This method for to be set sale_order_count as per getting from sale order model as per partners selected.
        :return:not any return
        """
        self.sale_order_count = 0
        leads = self.get_leads()
        if leads:
            orders = self.env['sale.order'].search([('opportunity_id', 'in', leads.ids)])
            if orders:
                self.sale_order_count = len(orders.filtered(lambda order: order))

    def compute_total_revenue(self):
        """
        This method for the to be set total revenue from the leads
        :return:not any return
        """
        self.total_revenue = 0.0
        leads = self.get_leads()
        if leads:
            self.total_revenue = sum(leads.filtered(lambda lead:lead).mapped('expected_revenue'))

    def get_paid_order(self):
        """
           This method for display View Paid Orders
           :return:action as per set domain
        """

        domain = []
        leads = self.get_leads()
        if leads:
            orders = self.env['sale.order'].search([('opportunity_id', 'in', leads.ids)])
            if orders:
                domain.append(('id','in',[r['id'] for r in orders.filtered(lambda order:order.picking_ids.state not in ('done','cancel')) ]))
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action.update({'domain':domain})
        return action

    def get_partner_ids(self):
        """
        This is for creating a list of partners ids as selected in Partner and Partner Contacts.
        :return: partner_ids as per getting from Partner and Partner Contacts.
        """
        partner_ids = []
        partner_ids.append(self.partner_id.id)
        if self.partner_contact_ids:
            for id in self.partner_contact_ids:
                partner_ids.append(id.id)
        return partner_ids

    def get_leads(self):
        """
        This method created common for getting all leads as per conditions
        :return: return leads as per searched
        """
        domain = [('partner_id', 'in', self.get_partner_ids())]
        if self.from_date:
            domain.append(('date_deadline', '>', self.from_date))
        if self.to_date:
            domain.append(('date_deadline', '<', self.to_date))

        leads = self.env['crm.lead'].search(domain)
        return leads
