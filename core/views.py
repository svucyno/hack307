import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User, Subject, UploadedFile, Timetable, Notification, Syllabus
from .forms import RegisterForm, SubjectForm, FileUploadForm, TimetableForm, SyllabusForm


# ──────────────────────────────────────────────
# HOME
# ──────────────────────────────────────────────
def home(request):
    if request.user.is_authenticated:
        if request.user.role == 'teacher':
            return redirect('upload')
        return redirect('dashboard')
    return redirect('login')


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        role     = request.POST.get('role', '')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.role == role:
                login(request, user)
                # Teacher goes straight to upload; student to dashboard
                return redirect('upload') if user.role == 'teacher' else redirect('dashboard')
            else:
                messages.error(request, f'This account is registered as a {user.role}, not {role}.')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'core/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ──────────────────────────────────────────────
# STUDENT DASHBOARD
# ──────────────────────────────────────────────
@login_required
def dashboard(request):
    # Teachers should never land here
    if request.user.role == 'teacher':
        return redirect('upload')

    recent_files   = UploadedFile.objects.select_related('subject', 'uploaded_by').order_by('-uploaded_at')[:6]
    total_subjects = Subject.objects.count()
    total_files    = UploadedFile.objects.count()
    unread_notifs  = Notification.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        'recent_files':   recent_files,
        'total_subjects': total_subjects,
        'total_files':    total_files,
        'unread_notifs':  unread_notifs,
        'semesters':      range(1, 9),
    }
    return render(request, 'core/dashboard.html', context)


# ──────────────────────────────────────────────
# SEMESTERS & SUBJECTS
# ──────────────────────────────────────────────
@login_required
def semesters_view(request):
    semester_data = []
    for i in range(1, 9):
        subjects = Subject.objects.filter(semester=i).select_related('teacher')
        semester_data.append({
            'number':        i,
            'subjects':      subjects,
            'subject_count': subjects.count(),
        })
    return render(request, 'core/semesters.html', {'semester_data': semester_data})


@login_required
def semester_detail(request, semester_num):
    if semester_num not in range(1, 9):
        return redirect('semesters')
    subjects = Subject.objects.filter(semester=semester_num).select_related('teacher')
    return render(request, 'core/subjects.html', {
        'semester_num': semester_num,
        'subjects':     subjects,
    })


@login_required
def subject_files(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    files   = UploadedFile.objects.filter(subject=subject).select_related('uploaded_by').order_by('-uploaded_at')
    return render(request, 'core/subject_files.html', {'subject': subject, 'files': files})


# ──────────────────────────────────────────────
# UPLOAD  (teacher = admin for files)
# ──────────────────────────────────────────────
@login_required
def upload_view(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can access this page.')
        return redirect('dashboard')

    subjects = Subject.objects.all().order_by('semester', 'name')

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.uploaded_by = request.user

            ext = os.path.splitext(uploaded_file.file.name)[1].lower()
            type_map = {
                '.pdf': 'pdf', '.ppt': 'ppt', '.pptx': 'ppt',
                '.doc': 'doc', '.docx': 'doc',
                '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.gif': 'image',
            }
            uploaded_file.file_type = type_map.get(ext, 'other')
            uploaded_file.save()

            # Notify all students
            for student in User.objects.filter(role='student'):
                Notification.objects.create(
                    title=f'New file in {uploaded_file.subject.name}',
                    message=(
                        f'{request.user.name} uploaded "{uploaded_file.title}" '
                        f'for {uploaded_file.subject.name} (Sem {uploaded_file.subject.semester})'
                    ),
                    notif_type='upload',
                    recipient=student,
                )

            messages.success(request, f'"{uploaded_file.title}" uploaded successfully!')
            return redirect('upload')
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    else:
        form = FileUploadForm()

    my_uploads = UploadedFile.objects.filter(
        uploaded_by=request.user
    ).select_related('subject').order_by('-uploaded_at')[:10]

    return render(request, 'core/upload.html', {
        'form':       form,
        'subjects':   subjects,
        'my_uploads': my_uploads,
    })


@login_required
def delete_file(request, file_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    file_obj = get_object_or_404(UploadedFile, id=file_id, uploaded_by=request.user)
    if request.method == 'POST':
        file_obj.file.delete(save=False)
        file_obj.delete()
        messages.success(request, 'File deleted successfully.')
    return redirect('upload')


# ──────────────────────────────────────────────
# TIMETABLE  (teacher = admin for timetable)
# ──────────────────────────────────────────────
@login_required
def timetable_view(request):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    if request.method == 'POST' and request.user.role == 'teacher':
        form = TimetableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry added!')
            return redirect('timetable')
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)

    entries = Timetable.objects.select_related('subject', 'subject__teacher').order_by('day', 'start_time')

    timetable_by_day = {day: [] for day in days}
    for entry in entries:
        if entry.day in timetable_by_day:
            timetable_by_day[entry.day].append(entry)

    has_entries  = entries.exists()
    all_subjects = Subject.objects.all().order_by('semester', 'name')

    return render(request, 'core/timetable.html', {
        'timetable_by_day': timetable_by_day,
        'days':             days,
        'has_entries':      has_entries,
        'all_subjects':     all_subjects,
    })


@login_required
def delete_timetable(request, entry_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('timetable')
    entry = get_object_or_404(Timetable, id=entry_id)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Entry removed.')
    return redirect('timetable')


# ──────────────────────────────────────────────
# NOTIFICATIONS
# ──────────────────────────────────────────────
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifications})


# ──────────────────────────────────────────────
# MANAGE SUBJECTS  (teacher = admin for subjects)
# ──────────────────────────────────────────────
@login_required
def manage_subjects(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    subjects = Subject.objects.select_related('teacher').order_by('semester', 'name')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Subject added successfully!')
                return redirect('manage_subjects')
            else:
                for errors in form.errors.values():
                    for error in errors:
                        messages.error(request, error)

        elif action == 'delete':
            subject = get_object_or_404(Subject, id=request.POST.get('subject_id'))
            name = subject.name
            subject.delete()
            messages.success(request, f'Subject "{name}" deleted.')
            return redirect('manage_subjects')

    # Pass teachers list for the subject form dropdown
    teachers = User.objects.filter(role='teacher')
    return render(request, 'core/manage_subjects.html', {
        'subjects': subjects,
        'form':     SubjectForm(),
        'teachers': teachers,
    })


# ──────────────────────────────────────────────
# API
# ──────────────────────────────────────────────
@login_required
def api_unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})
# ──────────────────────────────────────────────
# SYLLABUS
# ──────────────────────────────────────────────
@login_required
def syllabus_view(request):
    semester_data = []
    for i in range(1, 9):
        subjects = Subject.objects.filter(semester=i).prefetch_related('syllabus_units')
        semester_data.append({
            'number':   i,
            'subjects': subjects,
        })
    return render(request, 'core/syllabus.html', {'semester_data': semester_data})


@login_required
def syllabus_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    units   = Syllabus.objects.filter(subject=subject).order_by('unit_number')
    return render(request, 'core/syllabus_detail.html', {
        'subject': subject,
        'units':   units,
    })


@login_required
def manage_syllabus(request):
    if request.user.role != 'teacher':
        return redirect('syllabus')

    subjects = Subject.objects.all().order_by('semester', 'name')
    units    = Syllabus.objects.select_related('subject').order_by('subject__semester', 'unit_number')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            form = SyllabusForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Syllabus unit added successfully!')
                return redirect('manage_syllabus')
            else:
                for errors in form.errors.values():
                    for error in errors:
                        messages.error(request, error)

        elif action == 'delete':
            unit = get_object_or_404(Syllabus, id=request.POST.get('unit_id'))
            unit.delete()
            messages.success(request, 'Unit deleted.')
            return redirect('manage_syllabus')

    return render(request, 'core/manage_syllabus.html', {
        'subjects': subjects,
        'units':    units,
        'form':     SyllabusForm(),
    })