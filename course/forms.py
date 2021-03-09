from django import forms

from accounts.models import Student
from course.models import Attendance


class AttendanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        print(kwargs)
        if 'initial' in kwargs:
            self.fields['student'].queryset = kwargs['instance'].course.total_students_for_course

    class Meta:
        model = Attendance
        fields = ['student']
