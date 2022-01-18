from odoo import api, fields, models, _


class Course(models.Model):
    _name = "course.ept"
    _description = "Course"

    name = fields.Char(string="Course Name", help="Course Name", required=True)
    student_ids = fields.Many2many('student.ept', 'student_course_ref', 'course_id', 'student_id',
                                   string='Student',help="List of Students`")
