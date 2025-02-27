from django.db import models
from django.forms import ValidationError
from users.models import User 
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    is_public = models.BooleanField(default=True)  
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='events', blank=True)  
    private_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("la date de creation doit etre superieur a la data d'expiration")
        return super().clean()

    def get_registered_count(self):
        return self.ticket_set.count()

    def has_available_spots(self):
        return self.get_registered_count() < self.capacity

    def is_expired(self):
        return timezone.now() > self.end_date

    def user_can_register(self, user):
        if not user.is_authenticated:
            return False
        if user == self.organizer:
            return False
        if self.is_expired():
            return False
        if not self.has_available_spots():
            return False
        if self.ticket_set.filter(user=user).exists():
            return False
        return True
    
    def is_user_registered(self, user):
        return self.ticket_set.filter(user=user).exists()

class Ticket(models.Model):
    FREE = 'free'
    PAID = 'paid'
    TICKET_TYPES = [
        (FREE, 'Gratuit'),
        (PAID, 'Payant'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_type = models.CharField(max_length=4, choices=TICKET_TYPES, default=FREE)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user} - {self.event.title} - {self.ticket_type}"