#from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    R_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=R_CHOICES, default='student')
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    highest_education = models.TextField(max_length=255, blank=True, null=True)

    class Meta:
        permissions = [
            ("can_manage_users", "Can manage users (Admin only)"),
            ("can_grade_students", "Can grade students (Teacher only)"),
            ("can_view_courses", "Can view courses (Student only)"),
        ]

    def __str__(self):
        return self.username