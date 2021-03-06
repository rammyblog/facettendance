from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from accounts.decorator import student_required, teacher_required
from accounts.models import Lecturer, Student
from accounts.utils import face_rec_login
from .forms import AttendanceForm
from .models import Course, Attendance, StudentCourseRegistration


@login_required
def dashboard(request):
    # lecturer = Lecturer.objects.get(user=request.user)
    context = {}
    if request.user.lecturer:
        courses = Course.objects.filter(lecturer__user=request.user).count()
        attendances = Attendance.objects.filter(course__lecturer__user=request.user).count()
        students = StudentCourseRegistration.objects.filter(course__lecturer__user=request.user).count()
        context = {
            'courses': courses,
            'attendances': attendances,
            'students': students
        }
    return render(request, 'dashboard.html', context)


@login_required
def lecturer_dashboard(request):
    # lecturer = Lecturer.objects.get(user=request.user)
    context = {}
    if request.user.lecturer:
        courses = Course.objects.filter(lecturer__user=request.user).count()
        attendances = Attendance.objects.filter(course__lecturer=request.user).count()
        students = StudentCourseRegistration.objects.filter(course__lecturer=request.user).count()
        context = {
            'courses': courses,
            'attendances': attendances,
            'students': students
        }
    return render(request, 'dashboard.html', context)


@method_decorator([login_required, teacher_required], name='dispatch')
class CreateCourse(CreateView):
    model = Course
    fields = ['course_code', 'course_name']
    template_name = 'create_course.html'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        lecturer = get_object_or_404(Lecturer, user=self.request.user)
        self.object.lecturer = lecturer
        print(self.object.lecturer)
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            return reverse_lazy('course:course_list')


@method_decorator([login_required, teacher_required], name='dispatch')
class CourseList(ListView):
    model = Course
    template_name = 'course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        lecturer = get_object_or_404(Lecturer, user=self.request.user)
        return Course.objects.filter(lecturer=lecturer)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     courses = list(self.get_queryset().values_list('id', flat=True))
    #     context["sudents_registered"] =  StudentCourseRegistration.objects.filter(course_id__in=courses).filter(active=True)
    #     return context


@method_decorator([login_required, teacher_required], name='dispatch')
class StudentProfile(DetailView):
    model = Student
    template_name = 'student-profile.html'
    context_object_name = 'student'

    def get_queryset(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        return Student.objects.filter(pk=pk)


@method_decorator([login_required, teacher_required], name='dispatch')
class StudentsPerCourseList(ListView):
    model = StudentCourseRegistration
    template_name = 'all-students.html'
    context_object_name = 'students'

    def get_queryset(self, *args, **kwargs):
        course_pk = self.kwargs.get('pk')
        return StudentCourseRegistration.objects.filter(course_id=course_pk).filter(active=True)


@login_required
@teacher_required
def all_students_per_lecturer(request):
    lecturer = get_object_or_404(Lecturer, user=request.user)
    courses = list(Course.objects.filter(
        lecturer=lecturer).values_list('id', flat=True))
    students = StudentCourseRegistration.objects.filter(
        course_id__in=courses).filter(active=True)
    context = {
        'students': students,
    }
    return render(request, 'all-students.html', context)


def student_course_registration_processing(course_array, student, status):
    for course in course_array:
        StudentCourseRegistration.objects.update_or_create(
            student=student,
            course=course,
            defaults={'active': status}
        )


@login_required
@student_required
def student_course_registration(request, pk):
    student = Student.objects.get(pk=pk)
    courses = Course.objects.all()
    courses_registered = list(student.studentcourseregistration_set.filter(
        active=True).values_list('course', flat=True))

    if request.method == 'POST':
        try:
            print(request.POST.getlist('selected_courses'))
            selected_courses = [
                int(i) for i in request.POST.getlist('selected_courses')]
        except MultiValueDictKeyError:
            return redirect(reverse('accounts:student_detail', args=[pk]))
        old_courses = list(set(courses_registered) - set(selected_courses))
        print(selected_courses)
        adding_selected_courses = student_course_registration_processing(
            selected_courses, student, True)
        if old_courses:
            removing_old_courses = student_course_registration_processing(
                old_courses, student, False)
        messages.success(request, 'Courses added successfully')
        return redirect(reverse('accounts:student_detail', args=[pk]))
    context = {
        'student': student,
        'courses': courses,
        'courses_registered': courses_registered
    }

    return render(request, 'student_register_courses.html', context)


# def student_course_registration_processing(request):
#     student = Student.objects.get(id=id)
#     courses = Course.objects.all()
#     courses_registered = list(student.studentcourseregistration_set.all().values_list('course', flat=True))
#     context = {
#         'student':student,
#         'courses':courses,
#         'courses_registered': courses_registered
#     }

#     return render(request, 'student_register_courses.html', context)


@login_required
@teacher_required
def take_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student_registered_for_course = course.studentcourseregistration_set.filter(
        active=True).values_list('student')
    students = Student.objects.filter(
        pk__in=student_registered_for_course).filter(image__isnull=False)
    first_names = list(students.values_list('user__first_name', flat=True))
    matric_nos = list(students.values_list('user__username', flat=True))
    images_array = []
    for student in students:
        images_array.append(student.image.path)
    recgonized_faces_matric_no = face_rec_login(
        images_array, first_names, matric_nos)
    attendance, _ = Attendance.objects.get_or_create(
        course=course,
        date_recorded=datetime.today(),
        # defaults={'status': True}
    )
    for matric_no in matric_nos:
        student = get_object_or_404(Student, user__username=matric_no)
        if matric_no in recgonized_faces_matric_no:
            attendance.student.add(student)
            attendance.save()
        # else:
        #     Attendance.objects.get_or_create(
        #         course=course,
        #         student=student,
        #         defaults={'status': False}
        #     )

    return redirect(reverse('course:view_attendance', args=(course.id,)))


def attendance_per_course(request, course_id):
    # attendance_list = Attendance.objects.filter(course=course_id).order_by(
    #     'date_recorded').distinct('date_recorded')
    # attendance_present = attendance_list.filter(status=True)
    attendance_list = Attendance.objects.filter(course=course_id).order_by(
        'date_recorded')
    context = {
        'attendance_list': attendance_list,
    }
    return render(request, 'view_attendance_by_course.html', context)


# What the fuck is going on here
def student_attendance_per_course(request, course_id):
    attendance_list = Attendance.objects.filter(course=course_id).order_by(
        'date_recorded').distinct('date_recorded')
    lecturer = get_object_or_404(Lecturer, user=request.user)
    courses = get_object_or_404(Course, pk=course_id)
    students = StudentCourseRegistration.objects.filter(
        course=courses).filter(active=True)

    context = {
        'attendance_list': attendance_list,
        'students': students,
    }
    return render(request, 's', context)


def attendance_per_course_breakdown(request, course_id, attendance_date):
    print(attendance_date)
    attendance_list = Attendance.objects.filter(course_id=course_id,
                                                date_recorded__exact=attendance_date)
    students_present = list(attendance_list.values_list('student__user__username', flat=True))
    context = {
        'attendance_list': attendance_list,
        'students_present': students_present
        # 'attendance_present': len(attendance_present),
        # 'attendance_absent': len(attendance_list) - len(attendance_present)
    }
    return render(request, 'view_attendance_by_breakdown_course.html', context)


@method_decorator([login_required, teacher_required], name='dispatch')
class AttendanceUpdate(UpdateView):
    model = Attendance
    # fields = ['student']
    template_name = 'attendance_edit.html'
    form_class = AttendanceForm

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            return reverse_lazy('course:view_attendance_breakdown',
                                kwargs={'attendance_date': self.object.date_recorded})


def calculate_percentage_of_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # Gives everyone registered
    total_registered_students = StudentCourseRegistration.objects.filter(course_id=course_id, active=True)
    total_attendance_list = Attendance.objects.filter(course=course_id).count()
    all_attendance = list(
        Attendance.objects.filter(course=course_id).order_by('date_recorded').values_list(
            'student', flat=True))

    # Slow and should be left out of views, but I am too lazy and IDGAF for now
    # This is meant to iterate over every student that registered for the course then iterate over every attendance
    # taken, since I only got the student value list, it gives me the id of each student, so if that id(attendance)
    # If that id matches the student, it means the student attended the class.
    print(all_attendance)

    students_obj = {}
    # total_class_attended = 0
    for single_student in total_registered_students:
        # for attendance in all_attendance:
        #     print(attendance, single_student.student.user_id)
        #     if attendance == single_student.student.user_id:
        #         total_class_attended += 1
        total_class_attended = all_attendance.count(single_student.student.user_id)
        total_class_missed = total_attendance_list - total_class_attended
        attendance_percent = round(total_class_attended / total_attendance_list * 100, 2)
        students_obj[single_student.student] = [total_class_attended, total_class_missed, attendance_percent]
        total_class_attended = 0
    print(students_obj)
    return render(request, 'attendance_check.html', context={
        # 'total_attendance_list': total_attendance_list,
        'all_attendance': all_attendance,
        'course': course,
        'students_obj': students_obj
    })
