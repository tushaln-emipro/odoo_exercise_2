from odoo import api, fields, models, _


class CRMTeam(models.Model):
    _name = "crm.team.ept"
    _description = "CRM Team"

    name = fields.Char(string="Team Name", help="Name of Team")
    team_leader = fields.Many2one(comodel_name='res.users', string="Team leader", help="Team leader")
