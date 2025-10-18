from django.db import models
from django.contrib.auth.models import User

# ------------------------
# USER PROFILE EXTENSIONS
# ------------------------
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

    
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    employee_id = models.AutoField(primary_key=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    subjects = models.ManyToManyField(Subject, related_name="teachers", blank=True)


    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(primary_key=True, max_length=20)
    course = models.CharField(max_length=100)
    year = models.IntegerField()
    branch = models.CharField(max_length=100,blank=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    def __str__(self):
        return f"{self.name} ({self.roll_number})"


# ------------------------
# SUBJECT & ATTENDANCE
# ------------------------



class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused'),
    ]
    ATTENDENCE_TYPE_CHOICES = [
        ('One' , 'Single Session'),
        ('Two' , 'Double Session'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="attendance_records")

    type = models.CharField(max_length=3, choices=ATTENDENCE_TYPE_CHOICES, default='One')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="marked_attendance")

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.date} ({self.status})"


# ------------------------
# OPTIONAL: AGGREGATE VIEW
# ------------------------

class AttendanceSummary(models.Model):
    """Optional: store summarized attendance data for performance"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_classes = models.IntegerField(default=0)
    attended_classes = models.IntegerField(default=0)

    @property
    def attendance_percentage(self):
        if self.total_classes == 0:
            return 0
        return round((self.attended_classes / self.total_classes) * 100, 2)

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.attendance_percentage}%"
