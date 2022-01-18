from odoo import models, fields, api, _


class Task(models.Model):
    _inherit = "project.tags"

    project_tag_ids = fields.Many2many("project.task", string="Project Tags", help="Project Tags")
    partner_ids = fields.Many2many("res.partner", string='Partners', help='Partners', compute="compute_partner",
                                   store=False)

    def compute_partner(self):
        self.partner_ids = None
        for tag in self:
            if tag.id in tag.project_tag_ids.tag_ids.ids:
                tag.partner_ids = tag.project_tag_ids.partner_id.ids
