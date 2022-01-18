from odoo import api, fields, models, _


class Department(models.Model):
    _name = "department.ept"
    _description = "Department"

    name = fields.Char(string="Department Name", help="Department Name", required=True)
    department_manager_id = fields.Many2one(comodel_name='res.users', string="Department Manager",
                                            help='Department Manager')
    employee_ids = fields.One2many(comodel_name='employee.ept',inverse_name="id", string='Employee', help="Employee")
