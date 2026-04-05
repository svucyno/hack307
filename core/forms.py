from django import forms
from django.core.exceptions import ValidationError
from .models import User, Subject, UploadedFile, Timetable, Notification
import os


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'email', 'role', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'semester', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Subject name'}),
            'code': forms.TextInput(attrs={'placeholder': 'e.g. CS101'}),
        }


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['title', 'subject', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'File title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional description'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            allowed = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.gif']
            if ext not in allowed:
                raise ValidationError(f'File type not allowed. Allowed: {", ".join(allowed)}')
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('File size exceeds 10MB limit.')
        return file


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['day', 'subject', 'start_time', 'end_time', 'room']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'room': forms.TextInput(attrs={'placeholder': 'e.g. Room 101'}),
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'notif_type', 'recipient']
