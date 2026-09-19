from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from datetime import time



class HRStaffManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class HRStaff(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = HRStaffManager()

    def __str__(self):
        return self.full_name


class AttendanceLead(HRStaff):
    """Inherits everything from HRStaff automatically."""

    class Meta:
        verbose_name = "Attendance Lead"
        verbose_name_plural = "Attendance Leads"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    sex = models.CharField(max_length=10, blank=True)
    birthday = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_uploads/')
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    uploaded_by = models.ForeignKey(HRStaff, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.file)


class AttendanceRecord(models.Model):
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    total_hours = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=50)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    source_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE)
    gap_resolved = models.BooleanField(default=True)

    def matches(self, check_in, check_out, status):
        return self.check_in == check_in and self.check_out == check_out and self.status == status

    def __str__(self):
        return f"{self.employee.name} - {self.date}"





class UploadConflict(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()

    old_check_in = models.TimeField(null=True, blank=True)
    old_check_out = models.TimeField(null=True, blank=True)
    old_status = models.CharField(max_length=50, blank=True)

    new_check_in = models.TimeField(null=True, blank=True)
    new_check_out = models.TimeField(null=True, blank=True)
    new_status = models.CharField(max_length=50, blank=True)

    old_record = models.ForeignKey(AttendanceRecord, on_delete=models.SET_NULL, null=True, blank=True)
    new_source_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE)

    status = models.CharField(max_length=50, default='open')
    resolution = models.CharField(max_length=50, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(AttendanceLead, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Conflict: {self.employee.name} - {self.date}"


class Notification(models.Model):
    type = models.CharField(max_length=50)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='unread')
    recipient = models.ForeignKey(HRStaff, on_delete=models.CASCADE)
    related_record = models.ForeignKey(AttendanceRecord, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.type} - {self.date}"

    
class GracePeriod(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, unique=True)
    minutes = models.IntegerField(default=0)
    start_time = models.TimeField(default=time(8, 0))
    end_time = models.TimeField(default=time(17, 0))
    updated_date = models.DateTimeField(auto_now=True)
    set_by = models.ForeignKey(AttendanceLead, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.department.name} - {self.minutes} min"
    

class MonthlyReport(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(HRStaff, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('department', 'month', 'year')

    def __str__(self):
        return f"{self.department.name} - {self.month}/{self.year}"


class MonthlyReportEntry(models.Model):
    total_working_hours = models.FloatField(default=0)
    total_lateness = models.FloatField(default=0)
    total_late_minutes = models.IntegerField(default=0)
    total_absence = models.IntegerField(default=0)
    total_working_days = models.IntegerField(default=0)
    attendance_percentage = models.FloatField(default=0)
    service_hours = models.FloatField(default=0)
    mission_hours = models.FloatField(default=0)
    total_hours_with_leave = models.FloatField(default=0)
    is_exception = models.BooleanField(default=False)
    report = models.ForeignKey(MonthlyReport, on_delete=models.CASCADE, related_name='entries')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee.name} - {self.report}"


class TrendCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name






class Leaves(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    max_hours_allowed = models.FloatField()
    limit_per_period = models.IntegerField()
    period_type = models.CharField(max_length=10, choices=[('month', 'Per Month'), ('year', 'Per Year')], default='year')
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.name



class YearlyTrendReport(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField()
    output_type = models.CharField(max_length=20, choices=[('table', 'Table'), ('chart', 'Chart')])
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(AttendanceLead, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Leaves, blank=True)
    display_number = models.IntegerField(default=1)
    

    def __str__(self):
        suffix = f" ({self.display_number})" if self.display_number > 1 else ""
        return f"{self.department.name} - {self.year} - {self.output_type}{suffix}"



class LeaveUsage(models.Model):
    date = models.DateField()
    hours_used = models.FloatField()
    leave_type = models.ForeignKey(Leaves, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type.name} - {self.date}"


class InvitationCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    generated_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=50, default='active')
    generated_by = models.ForeignKey(AttendanceLead, on_delete=models.CASCADE)

    def __str__(self):
        return self.code


    