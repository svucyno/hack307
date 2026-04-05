models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, name, role, password=None):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, role='teacher', password=None):
        user = self.create_user(email, name, role, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.role})"


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    semester = models.IntegerField(choices=[(i, f'Semester {i}') for i in range(1, 9)])
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='subjects'
    )

    def __str__(self):
        return f"{self.code} - {self.name} (Sem {self.semester})"


class UploadedFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('ppt', 'PowerPoint'),
        ('doc', 'Word Document'),
        ('image', 'Image'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='files/')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='other')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject.code}"

    def get_file_icon(self):
        ext = self.file.name.split('.')[-1].lower()
        icons = {
            'pdf': '📄', 'ppt': '📊', 'pptx': '📊',
            'doc': '📝', 'docx': '📝',
            'png': '🖼️', 'jpg': '🖼️', 'jpeg': '🖼️', 'gif': '🖼️',
        }
        return icons.get(ext, '📁')


class Timetable(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
    ]
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries')
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.day} - {self.subject.name} ({self.start_time})"


class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ('upload', 'New Upload'),
        ('assignment', 'Assignment'),
        ('reminder', 'Reminder'),
        ('general', 'General'),
    ]
    title = models.CharField(max_length=200)
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title