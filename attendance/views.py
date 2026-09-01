from datetime import datetime
from .models import Employee, AttendanceRecord, ExcelFile, UploadConflict, Leaves, LeaveUsage, GracePeriod
import openpyxl
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Employee, AttendanceRecord, ExcelFile, UploadConflict
from .models import Employee, AttendanceRecord, ExcelFile


@login_required
def dashboard(request):
    return render(request, 'attendance/dashboard.html')


@login_required
def upload_excel(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('excel_file')

        if uploaded_file:
            # save the uploaded file + create the ExcelFile record
            excel_record = ExcelFile.objects.create(
                file=uploaded_file,
                status='pending',
                uploaded_by=request.user
            )

            # open the saved file and read its data
            workbook = openpyxl.load_workbook(excel_record.file.path)
            sheet = workbook.active

            row_count = 0
            created_count = 0

            # go through every row (skipping the header row)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_count += 1
                name, date, check_in, check_out = row

                try:
                    employee = Employee.objects.get(name=name)

                    # convert text date/times into real Python date/time objects
                    date_obj = datetime.strptime(str(date), '%Y-%m-%d').date()
                    check_in_obj = datetime.strptime(str(check_in), '%H:%M').time()
                    check_out_obj = datetime.strptime(str(check_out), '%H:%M').time()

                    # calculate total hours worked
                    duration = datetime.combine(date_obj, check_out_obj) - datetime.combine(date_obj, check_in_obj)
                    total_hours = duration.total_seconds() / 3600

                    AttendanceRecord.objects.create(
                        employee=employee,
                        source_file=excel_record,
                        date=date_obj,
                        check_in=check_in_obj,
                        check_out=check_out_obj,
                        total_hours=total_hours,
                        status='ok'
                    )
                    created_count += 1
                    print(f"CREATED: {name} - {date_obj} - {total_hours}h")

                except Employee.DoesNotExist:
                    UploadConflict.objects.create(
                        employee_name=name,
                        date=datetime.strptime(str(date), '%Y-%m-%d').date(),
                        description=f"No matching employee found for '{name}'",
                        status='open',
                        source_file=excel_record
                        )
                    print(f"CONFLICT CREATED: '{name}' not found")



            # one single summary message, shown after the loop finishes
            messages.success(
                request,
                f"'{uploaded_file.name}' uploaded — {created_count}/{row_count} records created!"
            )
            return redirect('upload_excel')

    return render(request, 'attendance/upload.html')




@login_required
def conflict_list(request):
    conflicts = UploadConflict.objects.filter(status='open')
    return render(request, 'attendance/conflicts.html', {'conflicts': conflicts})


@login_required
def resolve_conflict(request, conflict_id):
    conflict = UploadConflict.objects.get(id=conflict_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            conflict.status = 'accepted'
        elif action == 'reject':
            conflict.status = 'rejected'

        conflict.resolved_date = datetime.now()
        conflict.save()

        messages.success(request, f"Conflict for '{conflict.employee_name}' marked as {conflict.status}.")
        return redirect('conflict_list')

    return render(request, 'attendance/resolve_conflict.html', {'conflict': conflict})



# ---------- LEAVES ----------

@login_required
def leave_list(request):
    leaves = Leaves.objects.all()
    return render(request, 'attendance/leave_list.html', {'leaves': leaves})


@login_required
def add_leave(request):
    if request.method == 'POST':
        Leaves.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            category=request.POST.get('category'),
            max_hours_allowed=request.POST.get('max_hours_allowed'),
            limit_per_period=request.POST.get('limit_per_period'),
            is_paid=request.POST.get('is_paid') == 'on'
        )
        messages.success(request, "Leave type created.")
        return redirect('leave_list')

    return render(request, 'attendance/add_leave.html')


# ---------- LEAVE USAGE ----------

@login_required
def log_leave_usage(request):
    if request.method == 'POST':
        employee = Employee.objects.get(id=request.POST.get('employee'))
        leave_type = Leaves.objects.get(id=request.POST.get('leave_type'))

        LeaveUsage.objects.create(
            employee=employee,
            leave_type=leave_type,
            date=request.POST.get('date'),
            hours_used=request.POST.get('hours_used')
        )
        messages.success(request, f"Leave logged for {employee.name}.")
        return redirect('log_leave_usage')

    employees = Employee.objects.all()
    leaves = Leaves.objects.all()
    usages = LeaveUsage.objects.all().order_by('-date')
    return render(request, 'attendance/log_leave_usage.html', {
        'employees': employees,
        'leaves': leaves,
        'usages': usages
    })


# ---------- GRACE PERIOD ----------

@login_required
def grace_period_list(request):
    periods = GracePeriod.objects.all()

    if request.method == 'POST':
        GracePeriod.objects.create(
            department=request.POST.get('department'),
            minutes=request.POST.get('minutes'),
            set_by=request.user if hasattr(request.user, 'attendancelead') else None
        )
        messages.success(request, "Grace period set.")
        return redirect('grace_period_list')

    return render(request, 'attendance/grace_period_list.html', {'periods': periods})