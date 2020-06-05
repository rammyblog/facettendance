from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from .validators import UnicodeUsernameValidator


class User(AbstractUser):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHERS = 'OTHERS'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHERS, 'Others'),
    ]
    username = models.CharField(max_length=40, unique=True)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'username'

    gender = models.CharField(choices=GENDER_CHOICES, max_length=6)
    dept = models.CharField(_("Your Department"), blank=True, max_length=255)
    phone_number = PhoneNumberField(blank=True, default='')
    address = models.CharField(max_length=500, default='')
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    # REQUIRED_FIELDS = ['email', 'username']

    def __init__(self, *args, **kwargs):
        validate_username = UnicodeUsernameValidator()
        super(User, self).__init__(*args, **kwargs)
        self._meta.get_field('username').validators = [validate_username]


class Lecturer(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    qualification = models.CharField(max_length=200)
    image = models.ImageField(upload_to='lecturers', null=True, blank=True)

    class Meta:
        verbose_name = "Lecturer"
        verbose_name_plural = "Lecturers"

    def __str__(self):
        return self.user.username

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def courses_registered(self):
        return self.course_set.all()


class Student(models.Model):
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
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to='students', null=True, blank=True)

    level = models.CharField(_('Your Level'), blank=True,
                             choices=LEVEL_CHOICE, max_length=4)

    def __str__(self):
        return self.user.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def courses_registered(self):
        return self.studentcourseregistration_set.filter(active=True)


# @receiver(post_save, sender=User)
# def create_or_update_lecturer_profile(sender, instance, created, **kwargs):
#     if created:
#         Lecturer.objects.create(user=instance)
#     instance.lecturer.save()
