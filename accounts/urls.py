from django.urls import path
from .views import (StudentSignUpView, LecturerSignUpView, UpdateStudent,
                    user_login, student_image_login, image_registration,
                    StudentDetail, LecturerDetail, UpdateLecturer, UpdateUser)
from django.contrib.auth import views

app_name = 'accounts'

urlpatterns = [
    path('lecturer/register/', LecturerSignUpView.as_view(),
         name='lecturer_register'),
    path('add-student/', StudentSignUpView.as_view(), name='add_student'),
    path('user/login/', user_login, name='user_login_redirect'),
    path('student/image/login/<int:pk>/',
         student_image_login, name='student_image_login'),
    path('update-student/<int:pk>/',
         UpdateStudent.as_view(), name='update_student'),
    path('student/details/<int:pk>/',
         StudentDetail.as_view(), name='student_detail'),
    path('lecturer/details/<int:pk>/',
         LecturerDetail.as_view(), name='lecturer_detail'),
    path('update-lecturer/<int:pk>/',
         UpdateLecturer.as_view(), name='update_lecturer'),
    path('update-user/<int:pk>/',
         UpdateUser.as_view(), name='update_user'),
    path('image-registration/<int:pk>',
         image_registration, name='image_register'),
    path('reset', views.PasswordResetView.as_view(
        template_name='password_reset_form.html', email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt'),
        name='password_reset'
    ),

    path('reset/done', views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),

    path('account/reset/complete/',
         views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'),
         name='password_reset_complete'),

    path('settings/password/', views.PasswordChangeView.as_view(template_name='password_change.html'),
         name='password_change'),

    path('settings/password/done/', views.PasswordChangeDoneView.as_view(
        template_name='password_change_done.html'),
        name='password_change_done'
    ),

    path('login/', views.LoginView.as_view(template_name='login.html'), name='login'),

]
