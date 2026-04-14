from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Task, UserProfile
from django.contrib.auth.models import User
from .forms import TaskForm
from django.contrib import messages
import datetime

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        if name and email and phone:
            # Check if user exists with this email
            user = User.objects.filter(email=email).first()
            if not user:
                # Create user
                user = User.objects.create_user(username=email.split('@')[0] + str(User.objects.count()), email=email, password='default_password123', first_name=name)
                # Create profile
                UserProfile.objects.create(user=user, phone_number=phone)
            else:
                # Update phone if needed
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.phone_number = phone
                profile.save()
                user.first_name = name
                user.save()
            
            # Since we bypass standard auth, we need to explicitly set the backend
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please provide Name, Email, and Phone.')
            
    return render(request, 'App/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.method == 'POST':
        # Quick Add Task
        title = request.POST.get('title')
        keyword = request.POST.get('keyword', 'Store') # default if missing
        task_datetime = request.POST.get('datetime')
        if title and task_datetime:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(task_datetime)
            if dt:
                Task.objects.create(
                    user=request.user,
                    title=title,
                    keyword=keyword,
                    date=dt.date(),
                    time=dt.time()
                )
                messages.success(request, 'Task quickly added!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid date format.')

            
    tasks = Task.objects.filter(user=request.user).order_by('date', 'time')
    active_tasks = tasks.filter(is_completed=False)
    completed_tasks = tasks.filter(is_completed=True)
    return render(request, 'App/dashboard.html', {
        'tasks': tasks,
        'active_tasks': active_tasks,
        'completed_tasks': completed_tasks,
    })

@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task added successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'App/task_form.html', {'form': form, 'title': 'Add Task'})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'App/task_form.html', {'form': form, 'title': 'Edit Task'})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('dashboard')
    return render(request, 'App/task_confirm_delete.html', {'task': task})

@login_required
def task_details(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    # We will pass the task details and then fetch the places via JS dynamically
    # utilizing the user's location.
    return render(request, 'App/task_details.html', {'task': task})

@login_required
def mark_completed(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.is_completed = True
    task.save()
    messages.success(request, 'Task marked as completed!')
    return redirect('dashboard')
