from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='attendance/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('conflicts/', views.conflict_list, name='conflict_list'),
    path('conflicts/<int:conflict_id>/resolve/', views.resolve_conflict, name='resolve_conflict'),

path('leaves/', views.leave_list, name='leave_list'),
path('leaves/add/', views.add_leave, name='add_leave'),
path('leave-usage/', views.log_leave_usage, name='log_leave_usage'),
path('grace-periods/', views.grace_period_list, name='grace_period_list'),


]
