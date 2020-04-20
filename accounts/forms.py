from django import forms
from .models import Student, Lecturer
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'matric_no',
                  'dept', 'school', 'level',)

    def clean_matric_no(self):
        matric_no = self.cleaned_data['matric_no']

        try:
            Student.objects.get(matric_no)
        except Student.DoesNotExist:
            return matric_no

        raise ValidationError('Matric Number already taken')


class StudentLoginForm(forms.Form):
    matric_no = forms.CharField(
        max_length=50, required=True, help_text='Enter Your matric No')

    def clean_matric_no(self):
        matric_no = self.cleaned_data['matric_no']

        try:
            Student.objects.get(matric_no=matric_no)
        except Student.DoesNotExist:
            raise ValidationError('Incorrect Matric No')

        return matric_no


# class LectuerUpdateForm(forms.ModelForm):
#     email = forms.CharField(max_length=50, required=True,
#                             help_text='Enter Email')

#     class Meta:
#         model = Lecturer
#         fields = ['gender', 'qualification', 'image',
#                   'dept', 'school', 'phone_number', 'address']


class UserRegistrationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHERS = 'OTHERS'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHERS, 'Others'),
    ]
    email = forms.EmailField(max_length=300)
    first_name = forms.CharField(
        max_length=30, required=True, help_text='Enter your First Name')
    last_name = forms.CharField(
        max_length=30, required=True, help_text='Enter your Last name')
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    qualification = forms.CharField(
        max_length=30, help_text='Enter your Qualifications')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('email', 'first_name', 'last_name', 'gender', 'qualification')

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise ValidationError('Email already taken')
