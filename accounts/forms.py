from django import forms
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .validators import UnicodeUsernameValidator
from .models import Student, Lecturer
from django.contrib.auth import get_user_model
User = get_user_model()

LEVEL_ONE = '100'
LEVEL_TWO = '200'
LEVEL_THREE = '300'
LEVEL_FOUR = '400'
LEVEL_FIVE = '500'
LEVEL_SIX = '600'

LEVEL_CHOICE = [
    (LEVEL_ONE, '100L'),
    (LEVEL_TWO, '200L'),
    (LEVEL_THREE, '300L'),
    (LEVEL_FOUR, '400L'),
    (LEVEL_FIVE, '500L'),
    (LEVEL_SIX, '600L'),

]
MALE = 'MALE'
FEMALE = 'FEMALE'
OTHERS = 'OTHERS'
GENDER_CHOICES = [
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    (OTHERS, 'Others'),
]


class UserRegistrationForm(UserCreationForm):

    validate_username = UnicodeUsernameValidator()

    error_message = UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}), max_length=50, validators=[validate_username], help_text='Enter Your Matric no/Staff ID')
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}), max_length=32, help_text='First name')
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}), max_length=32, help_text='Last name')
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email'}), max_length=64, help_text='Enter a valid email address')
    # password1 = forms.CharField(widget=forms.PasswordInput(
    #     attrs={'class': 'form-control', 'placeholder': 'Password'}))
    # password2 = forms.CharField(widget=forms.PasswordInput(
    #     attrs={'class': 'form-control', 'placeholder': 'Password Again'}))

    address = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Address'}), max_length=50, help_text='Address', required=True)
    phone_number = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone Number'}), max_length=32, help_text='Phone number', required=True)
    dept = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Department'}), max_length=32, help_text='Your Department', required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('email', 'first_name', 'last_name', 'gender',
             'address', 'phone_number', 'dept')

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


class StudentSignUpForm(UserRegistrationForm):
    level = forms.ChoiceField(required=True, choices=LEVEL_CHOICE)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('level',)

    @transaction.atomic
    def save(self):
        data = self.cleaned_data

        phone_number = data['phone_number']
        address = data['address']
        level = data['level']
        gender = data['gender']
        dept = data['dept']
        password = data['password1']
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']

        user = super().save(commit=False)
        user.is_student = True
        user.address = address
        user.phone_number = phone_number
        user.dept = dept
        user.gender = gender
        user.email =email
        user.first_name=first_name
        user.last_name=last_name
        user.set_password(password)
        user.save()
        student = Student.objects.create(
            user=user, level=level)
        print(student)
        # student.interests.add(*self.cleaned_data.get('interests'))
        return user


class LecturerSignUpForm(UserRegistrationForm):
    qualification = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Your Qualification'}), max_length=32, help_text='Your Qualification')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('qualification',)

    # def clean_matric_no(self):
    #     matric_no = self.cleaned_data['matric_no']

    #     try:
    #         Student.objects.get(matric_no)
    #     except Student.DoesNotExist:
    #         return matric_no

    #     raise ValidationError('Matric Number already taken')

    @transaction.atomic
    def save(self):
        data = self.cleaned_data
        phone_number = data['phone_number']
        address = data['address']
        qualification = data['qualification']
        gender = data['gender']
        dept = data['dept']
        password = data['password1']
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        user = super().save(commit=False)
        user.is_teacher = True
        user.address = address
        user.phone_number = phone_number
        user.dept = dept
        user.gender = gender
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.save()
        Lecturer.objects.create(
            user=user,  qualification=qualification)
        # student.interests.add(*self.cleaned_data.get('interests'))
        return user


# class StudentLoginForm(forms.Form):
#     matric_no = forms.CharField(
#         max_length=50, required=True, help_text='Enter Your matric No')

#     def clean_matric_no(self):
#         matric_no = self.cleaned_data['matric_no']

#         try:
#             Student.objects.get(matric_no=matric_no)
#         except Student.DoesNotExist:
#             raise ValidationError('Incorrect Matric No')

#         return matric_no


# class LectuerUpdateForm(forms.ModelForm):
#     email = forms.CharField(max_length=50, required=True,
#                             help_text='Enter Email')

#     class Meta:
#         model = Lecturer
#         fields = ['gender', 'qualification', 'image',
#                   'dept', 'school', 'phone_number', 'address']
