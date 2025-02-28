from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from event.models import Event, Category, Ticket
from datetime import timedelta
from django.core import mail

User = get_user_model()

class EventViewsTest(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        self.category = Category.objects.create(name="Conférence")
        
        # Créer un organisateur
        self.organizer = User.objects.create_user(
            username='organisateur',
            email='organisateur@test.com',
            password='testpass123',
            is_organisateur=True
        )
        
        # Créer un participant
        self.participant = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            password='testpass123'
        )
        
        # Créer un événement public
        self.public_event = Event.objects.create(
            title="Événement Public",
            description="Description test",
            location="Location test",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            capacity=100,
            price=50.00,
            category=self.category,
            organizer=self.organizer,
            is_public=True
        )
        
        # Créer un événement privé
        self.private_event = Event.objects.create(
            title="Événement Privé",
            description="Description test",
            location="Location test",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            capacity=100,
            price=50.00,
            category=self.category,
            organizer=self.organizer,
            is_public=False
        )

    def test_event_list_view_public(self):
        """Test la vue de liste des événements pour les utilisateurs non connectés"""
        response = self.client.get(reverse('list_event'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Événement Public")
        self.assertNotContains(response, "Événement Privé")

    def test_event_list_view_authenticated(self):
        """Test la vue de liste des événements pour les utilisateurs connectés"""
        self.client.login(username='participant', password='testpass123')
        response = self.client.get(reverse('list_event'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Événement Public")

    def test_event_detail_view_public(self):
        """Test la vue détaillée d'un événement public"""
        self.client.login(username='participant', password='testpass123')
        response = self.client.get(
            reverse('event_detail', kwargs={'private_key': self.public_event.private_key})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.public_event.title)

    def test_event_detail_view_private_unauthorized(self):
        """Test l'accès non autorisé à un événement privé"""
        self.client.login(username='participant', password='testpass123')
        response = self.client.get(
            reverse('event_detail', kwargs={'private_key': self.private_event.private_key})
        )
        self.assertEqual(response.status_code, 403)

    def test_event_creation_view(self):
        """Test la création d'un événement"""
        self.client.login(username='organisateur', password='testpass123')
        event_data = {
            'title': 'Nouvel Événement',
            'description': 'Description test',
            'location': 'Location test',
            'start_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'capacity': 100,
            'price': 50.00,
            'category': self.category.id,
            'is_public': True
        }
        response = self.client.post(reverse('create_event'), event_data)
        self.assertEqual(response.status_code, 302)  # Redirection après création
        self.assertTrue(Event.objects.filter(title='Nouvel Événement').exists())

    def test_event_registration(self):
        """Test l'inscription à un événement"""
        self.client.login(username='participant', password='testpass123')
        response = self.client.post(
            reverse('register_for_event', kwargs={'private_key': self.public_event.private_key})
        )
        self.assertEqual(response.status_code, 302)  # Redirection après inscription
        
        # Vérifier la création du ticket
        self.assertTrue(
            Ticket.objects.filter(user=self.participant, event=self.public_event).exists()
        )
        
        # Vérifier l'envoi de l'email
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.public_event.title, mail.outbox[0].subject)

    def test_organizer_dashboard_access(self):
        """Test l'accès au tableau de bord de l'organisateur"""
        # Test accès non autorisé
        response = self.client.get(reverse('organizer_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        
        # Test accès participant
        self.client.login(username='participant', password='testpass123')
        response = self.client.get(reverse('organizer_dashboard'))
        self.assertEqual(response.status_code, 403)  # Accès refusé
        
        # Test accès organisateur
        self.client.login(username='organisateur', password='testpass123')
        response = self.client.get(reverse('organizer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tableau de bord")

    def test_event_update_view(self):
        """Test la modification d'un événement"""
        self.client.login(username='organisateur', password='testpass123')
        event_data = {
            'title': 'Événement Modifié',
            'description': 'Nouvelle description',
            'location': 'Nouveau lieu',
            'start_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'capacity': 150,
            'price': 75.00,
            'category': self.category.id,
            'is_public': True
        }
        response = self.client.post(
            reverse('update_event', kwargs={'private_key': self.public_event.private_key}),
            event_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Vérifier les modifications
        updated_event = Event.objects.get(pk=self.public_event.pk)
        self.assertEqual(updated_event.title, 'Événement Modifié')
        self.assertEqual(updated_event.capacity, 150)

    def test_event_delete_view(self):
        """Test la suppression d'un événement"""
        self.client.login(username='organisateur', password='testpass123')
        response = self.client.post(
            reverse('delete_event', kwargs={'private_key': self.public_event.private_key})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(pk=self.public_event.pk).exists()) 