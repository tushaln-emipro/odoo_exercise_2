from odoo import api, fields, models, _


class Employee(models.Model):
    _name = "employee.ept"
    _description = "Employee"

    name = fields.Char(string="Employee", requried=True, help="Name of Employee")
    department_id = fields.Many2one(comodel_name='department.ept', string='Department', requried=True,
                                    help="Department")
    shift_id = fields.Many2one(comodel_name='employee.department.shift.ept', string='Shift', requried=True,
                               help="Shift")
    job_position = fields.Char(string="Job Position", help="Job Position")
    salary = fields.Float(string="Salary", default=0.0, help="Salary")
    hiredate = fields.Date(string="Hire Date", help="Hire Date")
    gender = fields.Selection(selection=[('Male', 'Male'), ('Female', 'Female'), ('Transgender', 'Transgender')],
                              help="Employee Gender")
    job_type = fields.Selection(selection=[('Permanent', 'Permanent'), ('Ad Hoc', 'Ad Hoc')],
                                help="Employee Job Type")
    is_manager = fields.Boolean(string="Is Manager", help="Is Manager")
    manager_id = fields.Many2one(comodel_name='employee.ept', string='Manager', help="Manager")
    related_user = fields.Many2one(comodel_name='res.users', string='Related User', help="Related User")
    employee_ids = fields.One2many(comodel_name='employee.ept', inverse_name="manager_id", string='Employee',
                                   help="Employee")
    increment_percentage = fields.Float(string="Increment Percentage", default=0.0,
                                        groups="employee_ept.group_employee_mgmt_ept_manager",
                                        help="Increment Percentage")
