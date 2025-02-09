from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CustomUser  # Import CustomUser instead of User
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:signup')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('accounts:signup')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('accounts:signup')

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                role=role
            )
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('accounts:login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('accounts:signup')

    return render(request, 'accounts/signup.html')

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    return render(request, "accounts/templates/dashboard.html")

@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        messages.error(request, "Access Denied. Teachers only.")
        return redirect('home')

    # Generate calendar days for the current month
    today = datetime.now()
    calendar_days = [(today + timedelta(days=x)).day for x in range(14)]  # Next 2 weeks

    context = {
        'user': request.user,
        'calendar_days': calendar_days,
        'assignments': [
            {
                'title': 'Math Assignment: Algebra',
                'deadline': 'Feb 12, 2024',
                'status': 'Pending'
            },
            {
                'title': 'Physics Assignment: Mechanics',
                'deadline': 'Feb 14, 2024',
                'status': 'Pending'
            }
        ],
        'notifications': [
            {
                'type': 'New Message',
                'message': 'You have received a message from Jane Smith.',
                'link': '#'
            },
            {
                'type': 'New Assignment',
                'message': 'A new homework assignment is available for grading.',
                'link': '#'
            }
        ],
        'classes': [
            {
                'name': 'Class 10B - Algebra',
                'student_count': 25
            },
            {
                'name': 'Class 12A - Physics',
                'student_count': 30
            }
        ]
    }
    
    return render(request, 'accounts/teacher_dashboard.html', context)

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        messages.error(request, "Access Denied. Students only.")
        return redirect('home')

    context = {
        'user': request.user,
        'stats': {
            'average_score': 85,
            'completed_courses': 2,
            'total_courses': 4,
            'completed_assignments': 15
        },
        'enrolled_courses': [
            {
                'name': 'Introduction to Python',
                'instructor': 'Dr. Smith',
                'progress': 75
            },
            {
                'name': 'Advanced Mathematics',
                'instructor': 'Prof. Johnson',
                'progress': 45
            },
            {
                'name': 'Web Development Basics',
                'instructor': 'Ms. Davis',
                'progress': 30
            }
        ],
        'assignments': [
            {
                'title': 'Python Final Project',
                'course': 'Introduction to Python',
                'due_date': 'March 15, 2024',
                'status': 'pending'
            },
            {
                'title': 'Math Quiz 3',
                'course': 'Advanced Mathematics',
                'due_date': 'March 10, 2024',
                'status': 'pending'
            }
        ],
        'recent_activities': [
            {
                'type': 'Course Progress',
                'description': 'Completed Chapter 5 in Python Course',
                'time': '2 hours ago'
            },
            {
                'type': 'Assignment',
                'description': 'Submitted Math Quiz 2',
                'time': 'Yesterday'
            },
            {
                'type': 'Achievement',
                'description': 'Earned "Python Basics" Certificate',
                'time': '3 days ago'
            }
        ]
    }
    
    return render(request, 'accounts/student_dashboard.html', context)

@login_required
def student_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'teacher':
            return redirect('teacher_dashboard')
    return redirect('accounts:login')
