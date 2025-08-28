from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User


def index(request):
    return render(request, 'core/base.html')


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')


@login_required
def student_list(request):
    """
    Displays a list of all students with search and metadata filtering.
    """
    students = Student.objects.all()
    query = request.GET.get('q')
    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).distinct()

    return render(request, 'student_app/list_students.html', {'students': students, 'query': query})


@login_required
def add_students(request):
    """
    Handles adding a new student.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        if Student.objects.filter(email=email).exists():
            messages.error(request, "A student with this email already exists.")
            return render(request, "student_app/add_student.html", {'form_data': request.POST})

        student = Student(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=email,
            dob=request.POST.get('dob')
        )
        
        try:
            student.full_clean()
            student.save()

            metadata_str = request.POST.get('metadata', '')
            if metadata_str:
                pairs = [pair.strip() for pair in metadata_str.split(',')]
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        meta, created = Metadata.objects.get_or_create(key=key, value=value)
                        student.metadata.add(meta)
            
            messages.success(request, f"Student {student.first_name} added successfully.")
            return redirect("student_list")
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return render(request, 'student_app/add_student.html', {'form_data': request.POST})
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return render(request, 'student_app/add_student.html', {'form_data': request.POST})
    
    return render(request, 'student_app/add_student.html')


@login_required
def edit_student(request, pk):
    """
    Handles editing an existing student.
    """
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if Student.objects.exclude(pk=pk).filter(email=new_email).exists():
            messages.error(request, 'A student with this email already exists.')
            return render(request, 'student_app/edit_student.html', {'student': student})
        
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.email = new_email
        student.dob = request.POST.get('dob')
        
        try:
            student.full_clean()
            student.save()
            messages.success(request, 'Student information has been updated successfully!')
            return redirect('student_list')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return render(request, 'student_app/edit_student.html', {'student': student})
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
            return render(request, 'student_app/edit_student.html', {'student': student})
    
    return render(request, 'student_app/edit_student.html', {'student': student})


@login_required
def delete_student(request, pk):
    """
    Deletes a student.
    """
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student has been deleted successfully.')
    return redirect('student_list')


# --- Instructor Views ---

@login_required
def instructor_list(request):
    """
    Displays a list of all instructors with search functionality.
    """
    instructors = Instructor.objects.all().prefetch_related('courses', 'metadata')
    query = request.GET.get('q')

    if query:
        instructors = instructors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(courses__name__icontains=query)
        ).distinct()

    return render(request, 'instructor_app/list_instructor.html', {'instructors': instructors, 'query': query})


@login_required
def add_instructor(request):
    """
    Handles adding a new instructor.
    """
    courses = Course.objects.all()
    if request.method == 'POST':
        email = request.POST.get('email')
        if Instructor.objects.filter(email=email).exists():
            messages.error(request, "An instructor with this email already exists.")
            return render(request, 'instructor_app/add_instructor.html', {'form_data': request.POST, 'courses': courses})

        instructor = Instructor(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=email
        )
        
        try:
            instructor.full_clean()
            instructor.save()

            courses_list = request.POST.getlist('courses')
            metadata_str = request.POST.get('metadata', '')
            instructor.courses.set(courses_list)
            
            if metadata_str:
                pairs = [pair.strip() for pair in metadata_str.split(',')]
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        meta, created = Metadata.objects.get_or_create(key=key, value=value)
                        instructor.metadata.add(meta)
            
            messages.success(request, f"Instructor {instructor.first_name} added successfully.")
            return redirect('instructor_list')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return render(request, 'instructor_app/add_instructor.html', {'form_data': request.POST, 'courses': courses})
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return render(request, 'instructor_app/add_instructor.html', {'form_data': request.POST, 'courses': courses})
    
    return render(request, 'instructor_app/add_instructor.html', {'courses': courses})


@login_required
def edit_instructor(request, pk):
    """
    Handles editing an existing instructor.
    """
    instructor = get_object_or_404(Instructor, pk=pk)
    courses = Course.objects.all()
    
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if Instructor.objects.exclude(pk=pk).filter(email=new_email).exists():
            messages.error(request, "An instructor with this email already exists.")
            return render(request, 'instructor_app/edit_instructor.html', {'instructor': instructor, 'courses': courses})

        instructor.first_name = request.POST.get('first_name')
        instructor.last_name = request.POST.get('last_name')
        instructor.email = new_email

        try:
            instructor.full_clean()
            instructor.save()
            
            courses_list = request.POST.getlist('courses')
            instructor.courses.set(courses_list)
            
            metadata_str = request.POST.get('metadata', '')
            instructor.metadata.clear()
            if metadata_str:
                pairs = [pair.strip() for pair in metadata_str.split(',')]
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        meta, created = Metadata.objects.get_or_create(key=key, value=value)
                        instructor.metadata.add(meta)

            messages.success(request, 'Instructor information has been updated successfully!')
            return redirect('instructor_list')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return render(request, 'instructor_app/edit_instructor.html', {'instructor': instructor, 'courses': courses})
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
            return render(request, 'instructor_app/edit_instructor.html', {'instructor': instructor, 'courses': courses})
    
    return render(request, 'instructor_app/edit_instructor.html', {'instructor': instructor, 'courses': courses})


@login_required
def delete_instructor(request, pk):
    """
    Deletes an instructor.
    """
    instructor = get_object_or_404(Instructor, pk=pk)
    if request.method == 'POST':
        instructor.delete()
        messages.success(request, f"Instructor {instructor.first_name} {instructor.last_name} has been deleted successfully.")
    return redirect('instructor_list')


# --- Course Views ---

@login_required
def course_list(request):
    """
    Displays a list of all courses with search functionality.
    """
    courses = Course.objects.all()
    query = request.GET.get('q')

    if query:
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(course_code__icontains=query)
        ).distinct()

    return render(request, "course_app/list_course.html", {"courses": courses, 'query': query})


@login_required
def add_course(request):
    if request.method == 'POST':
        course = Course(
            name=request.POST.get('name'),
            course_code=request.POST.get('course_code'),
            description=request.POST.get('description')
        )
        try:
            course.full_clean()
            course.save()

            metadata_str = request.POST.get('metadata', '')
            if metadata_str:
                pairs = [pair.strip() for pair in metadata_str.split(',')]
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        meta, created = Metadata.objects.get_or_create(key=key, value=value)
                        course.metadata.add(meta)
            messages.success(request, f"Course '{course.name}' has been added successfully.")
            return redirect('course_list')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            context = {'form_data': request.POST}
            return render(request, 'course_app/add_course.html', context)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            context = {'form_data': request.POST}
            return render(request, 'course_app/add_course.html', context)
    
    return render(request, 'course_app/add_course.html')


@login_required
def edit_course(request, pk):
    """
    Handles editing an existing Course.
    """
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        new_course_code = request.POST.get('course_code')
        if Course.objects.exclude(pk=pk).filter(course_code=new_course_code).exists():
            messages.error(request, "A course with this code already exists.")
            return render(request, 'course_app/edit_course.html', {'course': course})
            
        course.name = request.POST.get('name')
        course.course_code = new_course_code
        course.description = request.POST.get('description')
        
        try:
            course.full_clean()
            course.save()
            metadata_str = request.POST.get('metadata', '')
            course.metadata.clear()
            if metadata_str:
                pairs = [pair.strip() for pair in metadata_str.split(',')]
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        meta, created = Metadata.objects.get_or_create(key=key, value=value)
                        course.metadata.add(meta)
            messages.success(request, 'Course information has been updated successfully!')
            return redirect('course_list')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return render(request, 'course_app/edit_course.html', {'course': course})
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
            return render(request, 'course_app/edit_course.html', {'course': course})
            
    return render(request, 'course_app/edit_course.html', {'course': course})


@login_required
def delete_course(request, pk):
    """
    Handles deleting a Course.
    """
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, f"Course '{course.name}' has been deleted successfully.")
    return redirect('course_list')



# --- User Authentication Views ---

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')

        if password != confirm_password:
            messages.error(request, 'Password and confirm password do not match.')
            return redirect('register')

        try:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('index')
        except Exception:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return redirect('register')
    
    return render(request, 'user/register.html')

def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Log in successful.')
            next_url = request.GET.get('next')
            return redirect(next_url or 'dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'user/login.html')
            
    return render(request, 'user/login.html')

def sign_out(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('signin')
    
@login_required
def user_info(request):
    return render(request, 'user/user_info.html', {'info': request.user})

@login_required
def reset_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('oldpassword')
        new_password = request.POST.get('newpassword')

        user = authenticate(username=request.user.username, password=old_password)

        if user is not None:
            user.set_password(new_password)
            user.save()
            logout(request)
            messages.success(request, 'Password has been reset. Please log in again.')
            return redirect('signin')
        else:
            messages.error(request, 'Invalid old password.')
            return redirect('reset_password')
    
    return render(request, 'user/reset_password.html')