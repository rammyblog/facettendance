from django.contrib import admin
from .models import Course, Attendance,StudentCourseRegistration

admin.site.register(Course)
admin.site.register(Attendance)
admin.site.register(StudentCourseRegistration)
