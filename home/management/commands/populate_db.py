from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random
from home.models import Teacher, Student, Subject, Attendance


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Attendance.objects.all().delete()
            Subject.objects.all().delete()
            Student.objects.all().delete()
            Teacher.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating sample data...')

        # Create Teachers
        teachers_data = [
            {
                'username': 'dr_smith',
                'first_name': 'Dr. Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@university.edu',
                'employee_id': 'EMP001',
                'department': 'Computer Science'
            },
            {
                'username': 'prof_johnson',
                'first_name': 'Prof. Michael',
                'last_name': 'Johnson',
                'email': 'michael.johnson@university.edu',
                'employee_id': 'EMP002',
                'department': 'Mathematics'
            },
            {
                'username': 'dr_williams',
                'first_name': 'Dr. Sarah',
                'last_name': 'Williams',
                'email': 'sarah.williams@university.edu',
                'employee_id': 'EMP003',
                'department': 'Physics'
            }
        ]

        teachers = []
        for teacher_data in teachers_data:
            user = User.objects.create_user(
                username=teacher_data['username'],
                first_name=teacher_data['first_name'],
                last_name=teacher_data['last_name'],
                email=teacher_data['email'],
                password='teacher123'
            )
            teacher = Teacher.objects.create(
                user=user,
                employee_id=teacher_data['employee_id'],
                department=teacher_data['department']
            )
            teachers.append(teacher)
            self.stdout.write(f'Created teacher: {teacher}')

        # Create Students
        students_data = [
            {'username': 'alice_student', 'first_name': 'Alice', 'last_name': 'Brown', 'roll_number': 'STU001', 'course': 'Computer Science', 'year': 3, 'branch': 'CS'},
            {'username': 'bob_student', 'first_name': 'Bob', 'last_name': 'Davis', 'roll_number': 'STU002', 'course': 'Computer Science', 'year': 3, 'branch': 'CS'},
            {'username': 'charlie_student', 'first_name': 'Charlie', 'last_name': 'Wilson', 'roll_number': 'STU003', 'course': 'Computer Science', 'year': 3, 'branch': 'CS'},
            {'username': 'diana_student', 'first_name': 'Diana', 'last_name': 'Miller', 'roll_number': 'STU004', 'course': 'Mathematics', 'year': 2, 'branch': 'MATH'},
            {'username': 'eve_student', 'first_name': 'Eve', 'last_name': 'Garcia', 'roll_number': 'STU005', 'course': 'Mathematics', 'year': 2, 'branch': 'MATH'},
            {'username': 'frank_student', 'first_name': 'Frank', 'last_name': 'Martinez', 'roll_number': 'STU006', 'course': 'Physics', 'year': 4, 'branch': 'PHY'},
            {'username': 'grace_student', 'first_name': 'Grace', 'last_name': 'Anderson', 'roll_number': 'STU007', 'course': 'Physics', 'year': 4, 'branch': 'PHY'},
            {'username': 'henry_student', 'first_name': 'Henry', 'last_name': 'Taylor', 'roll_number': 'STU008', 'course': 'Computer Science', 'year': 1, 'branch': 'CS'},
            {'username': 'ivy_student', 'first_name': 'Ivy', 'last_name': 'Thomas', 'roll_number': 'STU009', 'course': 'Mathematics', 'year': 1, 'branch': 'MATH'},
            {'username': 'jack_student', 'first_name': 'Jack', 'last_name': 'Jackson', 'roll_number': 'STU010', 'course': 'Physics', 'year': 3, 'branch': 'PHY'},
        ]

        students = []
        for student_data in students_data:
            user = User.objects.create_user(
                username=student_data['username'],
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                password='student123'
            )
            student = Student.objects.create(
                user=user,
                roll_number=student_data['roll_number'],
                course=student_data['course'],
                year=student_data['year'],
                branch=student_data['branch']
            )
            students.append(student)
            self.stdout.write(f'Created student: {student}')

        # Create Subjects
        subjects_data = [
            {'name': 'Data Structures and Algorithms', 'code': 'CS301', 'teacher': teachers[0]},
            {'name': 'Web Development', 'code': 'CS302', 'teacher': teachers[0]},
            {'name': 'Database Systems', 'code': 'CS303', 'teacher': teachers[0]},
            {'name': 'Calculus III', 'code': 'MATH301', 'teacher': teachers[1]},
            {'name': 'Linear Algebra', 'code': 'MATH302', 'teacher': teachers[1]},
            {'name': 'Quantum Mechanics', 'code': 'PHY401', 'teacher': teachers[2]},
            {'name': 'Thermodynamics', 'code': 'PHY302', 'teacher': teachers[2]},
        ]

        subjects = []
        for subject_data in subjects_data:
            subject = Subject.objects.create(
                name=subject_data['name'],
                code=subject_data['code'],
                teacher=subject_data['teacher']
            )
            subjects.append(subject)
            self.stdout.write(f'Created subject: {subject}')

        # Create Attendance Records
        self.stdout.write('Creating attendance records...')
        
        # Get the last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # Create attendance for each subject
        for subject in subjects:
            # Get students for this subject (simulate enrollment)
            if 'CS' in subject.code:
                subject_students = [s for s in students if s.course == 'Computer Science']
            elif 'MATH' in subject.code:
                subject_students = [s for s in students if s.course == 'Mathematics']
            elif 'PHY' in subject.code:
                subject_students = [s for s in students if s.course == 'Physics']
            else:
                subject_students = students[:5]  # Default to first 5 students
            
            # Create attendance for the last 30 days (3-4 classes per week)
            current_date = start_date
            while current_date <= end_date:
                # Skip weekends
                if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    # Randomly decide if there was a class (80% chance)
                    if random.random() < 0.8:
                        for student in subject_students:
                            # Randomly assign attendance status
                            status_choices = ['Present', 'Present', 'Present', 'Present', 'Absent', 'Late', 'Excused']
                            status = random.choice(status_choices)
                            
                            Attendance.objects.create(
                                student=student,
                                subject=subject,
                                date=current_date,
                                status=status,
                                marked_by=subject.teacher
                            )
                current_date += timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database with:\n'
                f'- {len(teachers)} teachers\n'
                f'- {len(students)} students\n'
                f'- {len(subjects)} subjects\n'
                f'- {Attendance.objects.count()} attendance records'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                '\nTest login credentials:\n'
                'Teachers:\n'
                '- dr_smith / teacher123\n'
                '- prof_johnson / teacher123\n'
                '- dr_williams / teacher123\n\n'
                'Students:\n'
                '- alice_student / student123\n'
                '- bob_student / student123\n'
                '- charlie_student / student123\n'
                '- (and 7 more students with same password)'
            )
        )
