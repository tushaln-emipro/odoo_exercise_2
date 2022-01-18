from odoo import api, fields, models, _


class Department(models.Model):
    _name = "employee.department.shift.ept"
    _description = "Shift"

    name = fields.Char(
        selection="[('Morning','Morning'),('Afternoon','Afternoon'),('Evening','Evening'),('Night','Night')]",
        string="Shift", help="Shift")
    employee_ids = fields.One2many(comodel_name='employee.ept', inverse_name="id", string='Employee', help="Employee")
    # _rec_name = shift
