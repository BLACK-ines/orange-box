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

    path('reports/monthly/', views.generate_monthly_report, name='generate_monthly_report'),
    path('reports/monthly/<int:report_id>/', views.monthly_report_detail, name='monthly_report_detail'),
    path('reports/monthly/<int:report_id>/delete/', views.delete_monthly_report, name='delete_monthly_report'),
    path('reports/monthly/<int:report_id>/export/excel/', views.export_monthly_report_excel, name='export_monthly_report_excel'),
    path('reports/monthly/<int:report_id>/export/pdf/', views.export_monthly_report_pdf, name='export_monthly_report_pdf'),

    path('trend-categories/', views.trend_category_list, name='trend_category_list'),
    path('reports/yearly/', views.generate_yearly_report, name='generate_yearly_report'),
    path('reports/yearly/<int:report_id>/', views.yearly_report_detail, name='yearly_report_detail'),

    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('invite/', views.generate_invite, name='generate_invite'),
    path('signup/', views.signup, name='signup'),

    path('team/', views.team_list, name='team_list'),
    path('employees/invite-ajax/', views.generate_invite_ajax, name='generate_invite_ajax'),

    path('employees/search/', views.employee_search, name='employee_search'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/export/pdf/', views.export_employee_history_pdf, name='export_employee_history_pdf'),



   
]
