from odoo import api, fields, models, _


class EmployeeLeave(models.Model):
    _name = "employee.leave.ept"
    _description = "Employee Leave"

    employee_id = fields.Many2one(comodel_name='employee.ept', string='Employee', help="Employee")
    department_id = fields.Many2one(comodel_name='department.ept', related="employee_id.department_id",
                                    readonly=True,string='Department', help="Department")
    start_date = fields.Date(string="Start Date", help="Start Date")
    end_date = fields.Date(string="End Date", help="End Date")
    status = fields.Selection(
        selection=[('Draft', 'Draft'), ('Approved', 'Approved'), ('Refused', 'Refused'), ('Cancelled', 'Cancelled')],
        default="Draft", help="Product Type")
    description = fields.Char(string="Leave Description", help="Leave Description")
