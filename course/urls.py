from django.urls import path
from .views import (dashboard, CreateCourse, CourseList, StudentsPerCourseList, student_course_registration, all_students_per_lecturer,
                    take_attendance, attendance_per_course,attendance_per_course_breakdown, AttendanceUpdate, 
                    calculate_percentage_of_attendance)

app_name = 'course'

urlpatterns = [
    path('dashboard/', dashboard, name='user_dashboard'),
    path('create-course/', CreateCourse.as_view(), name='create_course'),
    path('courses-list', CourseList.as_view(), name='course_list'),
    path('course/students/<int:pk>', StudentsPerCourseList.as_view(), name='courses_per_students'),

    path('student/<int:pk>/registration/',
         student_course_registration, name='student_registration'),
    path('all/student/',
         all_students_per_lecturer, name='all_student_per_lecturer'),

    path('attendance-update/<int:pk>/',
         AttendanceUpdate.as_view(), name='attendance_update'),
    path('take-attendance/<int:course_id>',
         take_attendance, name='take_attendance'),
    path('view-attendance/<int:course_id>',
         attendance_per_course, name='view_attendance'),
    path('view-attendance/marks/<int:course_id>',
         calculate_percentage_of_attendance, name='view_attendance_marks'),
    path('view-attendance-breakdown/<slug:attendance_date>', attendance_per_course_breakdown,
         name='view_attendance_breakdown')


]
