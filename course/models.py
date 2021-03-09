from django.db import models

from accounts.models import Lecturer, Student


class Course(models.Model):
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=400)
    course_code = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.course_code

    @property
    def full_course_name(self):
        return f"{self.course_code} ({self.course_name})"

    @property
    def total_students_for_course(self):
        cr = Course.objects.get(id=self.id)
        att_class = list(cr.studentcourseregistration_set.filter(active=True).values_list('student__user_id', flat=True))
        return Student.objects.filter(user_id__in=att_class)
        # return att_class

    @property
    def total_students(self):
        cr = Course.objects.get(id=self.id)
        att_class = cr.studentcourseregistration_set.filter(active=True).count()
        return att_class




class StudentCourseRegistration(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

    def __str__(self):
        return '%s : %s' % (self.student.user.username, self.course.course_code)


class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ManyToManyField(Student)
    # status = models.BooleanField(default=False)
    date_recorded = models.DateField(auto_now_add=True)

    # grade = models.FloatField(default=0)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    # @property
    # def attendance_status(self):
    #     if self.status:
    #         return 'Present'
    #     return 'Absent'

    def __str__(self):
        # status = 'Absent'
        # if self.status:
        #     status = 'Present'
        # return f"{self.student.user.first_name} was {status}"
        return f'Attendance for course {self.course.course_code} on {self.date_recorded}'

    @property
    def student_attendance(self):
        stud = Student.objects.get(id=self.student.id)
        cr = Course.objects.get(id=self.course.id)
        total_class = Attendance.objects.order_by('date_recorded').distinct('date_recorded')
        att_class = Attendance.objects.filter(course=cr, student__id=stud.id)
        if total_class == 0:
            attendance = 0
        else:
            attendance = round(len(att_class) / len(total_class) * 100, 2)
        return attendance

    @property
    def total_attended(self):
        stud = Student.objects.get(id=self.student.id)
        cr = Course.objects.get(id=self.course.id)
        att_class = Attendance.objects.filter(course=cr, student__id=stud.id).count()
        return att_class

    @property
    def total_absent(self):
        stud = Student.objects.get(id=self.student.id)
        cr = Course.objects.get(id=self.course.id)
        total_class = Attendance.objects.order_by('date_recorded').distinct('date_recorded')
        att_class = Attendance.objects.filter(course=cr, student=stud)
        absent = len(total_class) - len(att_class)
        return absent

    @property
    def total_present_per_class(self):
        # total_class = Attendance.objects.filter(date_recorded=self.date_recorded)
        # total_class = Attendance.objects.order_by('date_recorded').distinct('date_recorded')
        # total_present = self.student_set.count()
        # return total_present
        # print(Attendance.objects.get(id=self.id).student_set.count())

        return self.student.count()


    @property
    def total_student_absent_per_class(self):
        return self.course.total_students - self.total_present_per_class

