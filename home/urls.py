from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('mark-attendance/<int:subject_id>/', views.mark_attendance_view, name='mark_attendance'),
    path('save-attendance/', views.save_attendance_view, name='save_attendance'),
    
]
