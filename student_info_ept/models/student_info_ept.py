from odoo import api, fields, models, _


class Student(models.Model):
    _name = "student.ept"
    _description = "Student"

    name = fields.Char(string="Student Name", help="Student Name", required=True)
    student_class = fields.Char(string="Class", help="Student's class", required=True)
    birthdate = fields.Date(string="Student BirthDate", help="Student BirthDate", required=True)
    course_ids = fields.Many2many('course.ept', 'student_course_ref', 'student_id', 'course_id',
                                 string='Course',help="List of Courses`")
