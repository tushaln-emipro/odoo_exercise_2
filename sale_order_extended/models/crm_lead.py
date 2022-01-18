from odoo import api, fields, models, _


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = "crm.lead"

    def action_new_quotation(self):
        """
           This method is override for Add default 'crm_lead_opportunity_id' in And update default_tag_ids in context
           :return: action with Modified context
        """
        action = super(CrmLead, self).action_new_quotation()
        action['context']['default_crm_lead_opportunity_id'] = self.id
        action['context']['default_tag_ids'][0][2].append(self.env.ref('sale_order_extended.tag_crm_lead_extended').id)
        return action
