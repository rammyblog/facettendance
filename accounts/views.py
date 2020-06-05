from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from .forms import UserRegistrationForm, LecturerSignUpForm, StudentSignUpForm
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic import DetailView
from .mixins import ViewPermissionMixin
from django.contrib.auth import authenticate, login, logout
from .models import Lecturer, Student
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from .utils import convert64toImage, face_rec_login, encoded_face
from django.contrib import messages


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        matric_no = user.username
        user.save()
        login(self.request, user)
        student = Student.objects.get(matric_no=matric_no)
        return redirect(reverse('accounts:image_register', args=[student.id]))


class LecturerSignUpView(CreateView):
    model = User
    form_class = LecturerSignUpForm
    template_name = 'register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Lecturer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        # matric_no = user.cleaned_data['user']
        # user.save()
        login(self.request, user)
        # student = Student.objects.get(matric_no=matric_no)
        return redirect(reverse('course:user_dashboard'))


# def user_registration(request):
#     if request.method == 'POST':
#         user_form = UserRegistrationForm(request.POST)
#         if user_form.is_valid():
#             user_form.save(commit=False)
#             username = user_form.cleaned_data['username']
#             password = user_form.cleaned_data['password1']
#             email = user_form.cleaned_data['email']

#             user = user_form.save()
#             Lecturer.objects.update_or_create(
#                 user=user,
#                 defaults={
#                     "gender": user_form.cleaned_data['gender'],
#                     "qualification": user_form.cleaned_data['qualification'],

#                 }
#             )
#             user = authenticate(request, username=username, password=password)
#             login(request, user)

#             return redirect('course:user_dashboard')
#     else:
#         user_form = UserRegistrationForm()

#     context = {
#         'form': user_form
#     }

#     return render(request, 'register.html', context)


def user_login(request):
    if request.user.is_student:
        student = Student.objects.get(user=request.user)
        print(student.pk)
        if student.image:
            return redirect(reverse('accounts:student_image_login', args=[student.pk]))
        else:
            return redirect(reverse('accounts:image_register', args=[student.pk]))
    else:
        return redirect(reverse('course:user_dashboard'))


def student_image_login(request, pk):
    student = get_object_or_404(Student, pk=pk)
    images_array, first_names, matric_nos = [student.image.path], [
        student.first_name], [student.matric_no]
    authenticated = face_rec_login(
        images_array, first_names, matric_nos, student_login=True)

    if authenticated:
        request.session['student'] = student.pk
        return redirect(reverse('accounts:student_detail', args=[pk]))

    else:
        messages.error(request, 'Login failed')
        return redirect('accounts:student_login')


# class CreateStudent(CreateView):
#     model = Student
#     fields = ['first_name', 'last_name',
#               'matric_no', 'dept', 'school', 'level']
#     template_name = 'add_student.html'

#     def get_success_url(self):
#         if not self.success_url:
#             return reverse_lazy('accounts:image_register', args=[self.object.id])


class StudentDetail(ViewPermissionMixin, DetailView):
    model = Student
    template_name = 'profile.html'
    context_object_name = 'profile_detail'

    def dispatch(self, request, *args, **kwargs):
        try:
            if int(kwargs['pk']) != request.session['student'] or not request.user.is_authenticated:
                messages.warning(
                    request, 'You do not have access to view this page')
                return redirect('accounts:student_login')
        except KeyError:
            return redirect('accounts:student_login')

        return super(StudentDetail, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student_profile"] = True
        # context['courses_registered'] = self.studentcourseregistration_set.filter(active=True)
        return context


class LecturerDetail(ViewPermissionMixin, DetailView):
    model = Lecturer
    template_name = 'lecturer-profile.html'
    context_object_name = 'profile_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lecturer_profile"] = True
        # context['courses_registered'] = self.studentcourseregistration_set.filter(active=True)
        return context


class UpdateLecturer(UpdateView):
    model = Lecturer
    fields = ['gender', 'qualification', 'image',
              'dept', 'school', 'phone_number', 'address']
    template_name = 'update_lecturer.html'

    context_object_name = 'lecturer'

    def get_context_data(self, **kwargs):

        context = super(UpdateLecturer, self).get_context_data(**kwargs)
        context['update'] = True

        return context

    def get_success_url(self):
        if not self.success_url:
            return reverse_lazy('accounts:lecturer_detail', args=[self.object.id])


class UpdateUser(UpdateView):
    model = User
    fields = ['email']
    template_name = 'update_lecturer.html'

    context_object_name = 'lecturer'

    def get_context_data(self, **kwargs):

        context = super(UpdateUser, self).get_context_data(**kwargs)
        context['update'] = True

        return context

    def get_success_url(self):
        if not self.success_url:
            return reverse_lazy('accounts:lecturer_detail', args=[self.object.id])


class UpdateStudent(UpdateView):
    model = Student
    fields = ['first_name', 'last_name',
              'matric_no', 'dept', 'school', 'level']
    template_name = 'add_student.html'

    context_object_name = 'student'

    def get_context_data(self, **kwargs):

        context = super(UpdateStudent, self).get_context_data(**kwargs)
        context['update'] = True

        return context

    def get_success_url(self):
        if not self.success_url:
            return reverse_lazy('accounts:image_register', args=[self.object.id])


def image_registration(request, pk):
    if request.method == 'POST':
        image = request.POST['autentication_image']
        user = get_object_or_404(Student, pk=pk)
        user_image = convert64toImage(image, user.user.first_name)
        temppath = default_storage.save('temp.png', content=user_image)
        temp_filepath = default_storage.path(temppath)
        face_accepted = encoded_face(temp_filepath)
        if face_accepted:
            user.image = user_image
            user.save()
            default_storage.delete(temppath)
            return redirect('course:user_dashboard')
        else:
            default_storage.delete(temppath)
            messages.warning(request, 'Face Not decteted.')

        default_storage.delete(temppath)
    return render(request, 'auth_image.html')
