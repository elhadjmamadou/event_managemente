from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from event.models import Event, Category, Ticket
from datetime import timedelta
import uuid

User = get_user_model()

class EventModelTest(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.category = Category.objects.create(name="Conférence")
        self.organizer = User.objects.create_user(
            username='organisateur',
            email='organisateur@test.com',
            password='testpass123',
            is_organisateur=True
        )
        self.participant = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            password='testpass123'
        )

    def test_event_creation(self):
        """Test la création d'un événement avec des données valides"""
        event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            location="Test Location",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            capacity=100,
            price=50.00,
            category=self.category,
            organizer=self.organizer,
            is_public=True
        )
        self.assertEqual(event.title, "Test Event")
        self.assertEqual(event.capacity, 100)
        self.assertTrue(isinstance(event.private_key, uuid.UUID))

    def test_event_dates_validation(self):
        """Test la validation des dates de l'événement"""
        # Test avec date de fin avant date de début
        with self.assertRaises(ValidationError):
            event = Event(
                title="Test Event",
                description="Test Description",
                location="Test Location",
                start_date=timezone.now() + timedelta(days=2),
                end_date=timezone.now() + timedelta(days=1),
                capacity=100,
                category=self.category,
                organizer=self.organizer
            )
            event.full_clean()

    def test_event_capacity_validation(self):
        """Test la validation de la capacité de l'événement"""
        with self.assertRaises(ValidationError):
            event = Event(
                title="Test Event",
                description="Test Description",
                location="Test Location",
                start_date=timezone.now() + timedelta(days=1),
                end_date=timezone.now() + timedelta(days=2),
                capacity=-1,
                category=self.category,
                organizer=self.organizer
            )
            event.full_clean()

    def test_event_methods(self):
        """Test les méthodes de l'événement"""
        event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            location="Test Location",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            capacity=2,
            category=self.category,
            organizer=self.organizer
        )

        # Test has_available_spots
        self.assertTrue(event.has_available_spots())
        Ticket.objects.create(user=self.participant, event=event)
        self.assertTrue(event.has_available_spots())
        Ticket.objects.create(user=self.participant, event=event)
        self.assertFalse(event.has_available_spots())

        # Test is_expired
        self.assertFalse(event.is_expired())
        event.end_date = timezone.now() - timedelta(days=1)
        event.save()
        self.assertTrue(event.is_expired())

class TicketModelTest(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.category = Category.objects.create(name="Conférence")
        self.organizer = User.objects.create_user(
            username='organisateur',
            email='organisateur@test.com',
            password='testpass123'
        )
        self.participant = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            password='testpass123'
        )
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            location="Test Location",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            capacity=100,
            price=50.00,
            category=self.category,
            organizer=self.organizer
        )

    def test_ticket_creation(self):
        """Test la création d'un ticket"""
        ticket = Ticket.objects.create(
            user=self.participant,
            event=self.event,
            ticket_type='paid',
            is_paid=True
        )
        self.assertTrue(isinstance(ticket.id, int))
        self.assertEqual(ticket.user, self.participant)
        self.assertEqual(ticket.event, self.event)
        self.assertEqual(ticket.ticket_type, 'paid')
        self.assertTrue(ticket.is_paid)

    def test_ticket_unique_constraint(self):
        """Test qu'un utilisateur ne peut pas avoir plusieurs tickets pour le même événement"""
        Ticket.objects.create(
            user=self.participant,
            event=self.event,
            ticket_type='paid',
            is_paid=True
        )
        with self.assertRaises(Exception):
            Ticket.objects.create(
                user=self.participant,
                event=self.event,
                ticket_type='paid',
                is_paid=True
            )

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        """Test la création d'une catégorie"""
        category = Category.objects.create(name="Test Category")
        self.assertEqual(str(category), "Test Category")
        self.assertEqual(category.name, "Test Category") 