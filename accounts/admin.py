from django.contrib import admin
from .models import Lecturer, Student, User
from django.contrib.auth.admin import UserAdmin

admin.site.register(Lecturer)
UserAdmin.list_display += ('is_student', 'is_teacher',)  # don't forget the commas
UserAdmin.list_filter += ('is_student', 'is_teacher',)
UserAdmin.fieldsets += (('Membership Status', {'fields': ('is_student', 'is_teacher',)}),)
admin.site.register(User, UserAdmin)

admin.site.register(Student)
