from django.contrib import admin
from .models import (
    HRStaff, AttendanceLead, Employee, ExcelFile, AttendanceRecord,
    UploadConflict, Notification, GracePeriod, MonthlyReport,
    MonthlyReportEntry, YearlyTrendReport, TrendCategory, Leaves,
    LeaveUsage, InvitationCode
)

admin.site.register(HRStaff)
admin.site.register(AttendanceLead)
admin.site.register(Employee)
admin.site.register(ExcelFile)
admin.site.register(AttendanceRecord)
admin.site.register(UploadConflict)
admin.site.register(Notification)
admin.site.register(GracePeriod)
admin.site.register(MonthlyReport)
admin.site.register(MonthlyReportEntry)
admin.site.register(YearlyTrendReport)
admin.site.register(TrendCategory)
admin.site.register(Leaves)
admin.site.register(LeaveUsage)
admin.site.register(InvitationCode)