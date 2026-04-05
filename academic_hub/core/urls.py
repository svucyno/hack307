from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Student routes
    path('dashboard/', views.dashboard, name='dashboard'),
    path('semesters/', views.semesters_view, name='semesters'),
    path('semester/<int:semester_num>/', views.semester_detail, name='semester_detail'),
    path('subject/<int:subject_id>/files/', views.subject_files, name='subject_files'),

    # Teacher routes
    path('upload/', views.upload_view, name='upload'),
    path('upload/delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('subjects/manage/', views.manage_subjects, name='manage_subjects'),

    # Shared routes
    path('timetable/', views.timetable_view, name='timetable'),
    path('timetable/delete/<int:entry_id>/', views.delete_timetable, name='delete_timetable'),
    path('notifications/', views.notifications_view, name='notifications'),

    # API
    path('api/notifications/count/', views.api_unread_count, name='api_unread_count'),
]
