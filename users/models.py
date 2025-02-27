from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('organisateur', 'Organisateur'),
        ('participant', 'Participant'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='participant')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.role})'

    @property
    def is_organisateur(self):
        return self.role == 'organisateur'

    @property
    def is_participant(self):
        return self.role == 'participant'
