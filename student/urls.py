from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/', views.student_list, name='student_list'),
    path('add-student/', views.add_students, name='add_student'),
    path('edit-student/<int:pk>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:pk>/', views.delete_student, name='delete_student'),

    path('course/', views.course_list, name='course_list'),
    path('add-course/', views.add_course, name='add_course'),
    path('edit-course/<int:pk>/', views.edit_course, name='edit_course'),
    path('delete-course/<int:pk>/', views.delete_course, name='delete_course'),

    path('instructor/', views.instructor_list, name='instructor_list'),
    path('add-instructor/', views.add_instructor, name='add_instructor'),
    path('edit-instructor/<int:pk>/', views.edit_instructor, name='edit_instructor'),
    path('delete-instructor/<int:pk>/', views.delete_instructor, name='delete_instructor'),
    
    path('register/', views.register, name='register'),
    path('login/', views.sign_in, name='signin'),
    path('signout/', views.sign_out, name='signout'),


]