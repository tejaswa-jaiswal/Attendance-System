from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .models import Teacher, Student, Subject, Attendance
from django.http import HttpResponse

# Create your views here.

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                
                # Check if user is a teacher or student and redirect accordingly
                try:
                    teacher = Teacher.objects.get(user=user)
                    return redirect('teacher_dashboard')
                except Teacher.DoesNotExist:
                    try:
                        student = Student.objects.get(user=user)
                        return redirect('student_dashboard')
                    except Student.DoesNotExist:
                        # User exists but is neither teacher nor student
                        messages.warning(request, 'Your account is not properly configured. Please contact administrator.')
                        return redirect('login')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'login.html')

def teacher_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        teacher = Teacher.objects.get(user=request.user)
        subjects = teacher.subjects.all()
        
        # Calculate teacher statistics
        total_students = 0
        total_attendance_marked = 0
        
        # Calculate statistics and create subject data with counts
        subjects_data = []
        classes_data = {}  # For JavaScript attendance modal
        students = Student.objects.filter(teacher=teacher)
        for subject in subjects:
            # For Option B: assume all teacher's students are enrolled in all subjects
            subject_students = students
            student_count = subject_students.count()
            total_students += student_count

            # Count attendance marked by this teacher for this subject
            total_attendance_marked += subject.attendance_records.filter(marked_by=teacher).count()

            # Prepare subject data
            subject_data = {
                'subject': subject,
                'student_count': student_count,
                'students': list(subject_students)
            }
            subjects_data.append(subject_data)

            # Prepare JS modal data
            classes_data[subject.code] = [
                {
                    'roll': i + 1,
                    'name': f"{student.user.get_full_name() or student.user.username}",
                    'student_id': student.roll_number
                }
                for i, student in enumerate(subject_students)
            ]

        
        # Get recent attendance records marked by this teacher
        recent_attendance = []
        for subject in subjects:
            recent_attendance.extend(
                subject.attendance_records.filter(marked_by=teacher).order_by('-date')[:5]
            )
        recent_attendance = sorted(recent_attendance, key=lambda x: x.date, reverse=True)[:10]
        for i in subjects_data:
            print(i)
        context = {
            'user': request.user,
            'teacher': teacher,
            'subjects': subjects,
            'subjects_data': subjects_data,
            'classes_data': classes_data,
            'user_type': 'teacher',
            'total_students': total_students,
            'total_attendance_marked': total_attendance_marked,
            'recent_attendance': recent_attendance,
        }
        return render(request, 'teacher_dashboard.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Access denied. Teacher profile not found.')
        return redirect('login')

def student_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        student = Student.objects.get(user=request.user)
        # Get attendance records for this student
        attendance_records = student.attendance_records.all()[:10]  # Last 10 records
        
        # Calculate attendance statistics
        all_records = student.attendance_records.all()
        total_classes = all_records.count()
        present_count = all_records.filter(status='Present').count()
        absent_count = all_records.filter(status='Absent').count()
        late_count = all_records.filter(status='Late').count()
        excused_count = all_records.filter(status='Excused').count()
        
        # Calculate overall attendance percentage
        if total_classes > 0:
            attendance_percentage = round((present_count / total_classes) * 100, 1)
        else:
            attendance_percentage = 0
        
        context = {
            'user': request.user,
            'student': student,
            'attendance_records': attendance_records,
            'user_type': 'student',
            'total_classes': total_classes,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'excused_count': excused_count,
            'attendance_percentage': attendance_percentage,
        }
        return render(request, 'student_dashboard.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Access denied. Student profile not found.')
        return redirect('login')

def dashboard_view(request):
    """Fallback dashboard - redirects to appropriate dashboard based on user type"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check user type and redirect
    try:
        Teacher.objects.get(user=request.user)
        return redirect('teacher_dashboard')
    except Teacher.DoesNotExist:
        try:
            Student.objects.get(user=request.user)
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Your account is not properly configured.')
            return redirect('login')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def mark_attendance_view(request,subject_id):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    
    teacher = Teacher.objects.get(user=request.user)
    subject = Subject.objects.get(id=subject_id)
    if subject in teacher.subjects.all():
        students = Student.objects.filter(teacher=teacher)
    else:
        students = Student.objects.none()  
    
    context = {
        'user': request.user,
        'teacher': teacher,
        'subject': subject,
        'user_type': 'teacher',
        'students': students,
        
    }
    return render(request, 'mark_attendance.html', context)
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from datetime import date


@csrf_protect
def save_attendance_view(request):
    
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        # Get teacher
        teacher = Teacher.objects.get(user=request.user)
        data = request.POST
        subject_id = data.get('subject_id')
        
        if not subject_id:
            return HttpResponse('Subject ID not provided', status=400)

        # Get subject
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Subject not found'})

        # Option B: get all students under this teacher
        students = Student.objects.filter(teacher=teacher)
        if not students.exists():
            return JsonResponse({'success': False, 'error': 'No students found for this teacher'})

        today = date.today()
        attendance_created = 0
        attendance_updated = 0

        for student in students:
            status_key = f"status_{student.roll_number}"
            if status_key not in data:
                continue

            status = data[status_key]

            # ✅ Save or update attendance record
            attendance_record, created = Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=today,
                defaults={'status': status, 'marked_by': teacher}
            )

            if created:
                attendance_created += 1
            else:
                attendance_updated += 1

        return JsonResponse({
            'success': True,
            'message': f'Attendance saved for {attendance_created + attendance_updated} students '
                       f'({attendance_created} new, {attendance_updated} updated)',
        })

    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Teacher profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
