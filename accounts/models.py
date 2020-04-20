from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Lecturer(models.Model):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHERS = 'OTHERS'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHERS, 'Others'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6)
    qualification = models.CharField(max_length=200)
    image = models.ImageField(upload_to='lecturers', null=True, blank=True)
    dept = models.CharField(_("Your Department"), blank=True, max_length=255)
    school = models.CharField(_("Name of school"), blank=True, max_length=255)
    phone_number = PhoneNumberField(blank=True, default='')
    address = models.CharField(max_length=500, default='')

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
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    matric_no = models.CharField(unique=True, max_length=200)
    image = models.ImageField(upload_to='students', null=True, blank=True)
    dept = models.CharField(_("Your Department"), blank=True, max_length=255)
    school = models.CharField(_("Name of school"), blank=True, max_length=255)
    level = models.CharField(_('Your Level'), blank=True,
                             choices=LEVEL_CHOICE, max_length=4)
    phone_number = PhoneNumberField(blank=True, default='')
    address = models.CharField(max_length=500, default='')
    email = models.EmailField(max_length=254, default='')

    def __str__(self):
        return self.first_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def courses_registered(self):
        return self.studentcourseregistration_set.filter(active=True)


@receiver(post_save, sender=User)
def create_or_update_lecturer_profile(sender, instance, created, **kwargs):
    if created:
        Lecturer.objects.create(user=instance)
    instance.lecturer.save()
