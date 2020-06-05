from django.contrib import admin
from .models import Lecturer, Student, User

admin.site.register(Lecturer)
admin.site.register(User)

admin.site.register(Student)
