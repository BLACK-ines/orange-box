from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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
    pass




class Employee(models.Model):
    name = models.CharField(max_length=150)
    sex = models.CharField(max_length=10)
    birthday = models.DateField()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_uploads/')
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    uploaded_by = models.ForeignKey(HRStaff, on_delete=models.CASCADE)

    def __str__(self):
        return self.file_name




class AttendanceRecord(models.Model):
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    total_hours = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=50)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    source_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class UploadConflict(models.Model):
    employee_name = models.CharField(max_length=150)
    date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=50, default='open')
    resolved_date = models.DateTimeField(null=True, blank=True)
    source_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE)
    resolved_by = models.ForeignKey(AttendanceLead, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Conflict: {self.employee_name} - {self.date}"


class Notification(models.Model):
    type = models.CharField(max_length=50)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='unread')
    recipient = models.ForeignKey(HRStaff, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.type} - {self.date}"


class GracePeriod(models.Model):
    department = models.CharField(max_length=100)
    minutes = models.IntegerField()
    updated_date = models.DateTimeField(auto_now=True)
    set_by = models.ForeignKey(AttendanceLead, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.department} - {self.minutes} min"


class MonthlyReport(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(HRStaff, on_delete=models.CASCADE)

    def __str__(self):
        return f"Monthly Report {self.month}/{self.year}"


class MonthlyReportEntry(models.Model):
    total_working_hours = models.FloatField(default=0)
    total_lateness = models.FloatField(default=0)
    total_absence = models.IntegerField(default=0)
    total_working_days = models.IntegerField(default=0)
    attendance_percentage = models.FloatField(default=0)
    report = models.ForeignKey(MonthlyReport, on_delete=models.CASCADE, related_name='entries')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee.name} - {self.report}"


class TrendCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class YearlyTrendReport(models.Model):
    year = models.IntegerField()
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(AttendanceLead, on_delete=models.CASCADE)
    categories = models.ManyToManyField(TrendCategory, blank=True)

    def __str__(self):
        return f"Yearly Trend Report {self.year}"


class Leaves(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    max_hours_allowed = models.FloatField()
    limit_per_period = models.IntegerField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.name


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




    