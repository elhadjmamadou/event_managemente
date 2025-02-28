from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from event.forms import EventForm
from event.models import Category
from datetime import timedelta

class EventFormTest(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.category = Category.objects.create(name="Conférence")
        self.valid_data = {
            'title': 'Test Event',
            'description': 'Test Description',
            'location': 'Test Location',
            'start_date': timezone.now() + timedelta(days=1),
            'end_date': timezone.now() + timedelta(days=2),
            'capacity': 100,
            'price': 50.00,
            'category': self.category.id,
            'is_public': True
        }

    def test_valid_form(self):
        """Test avec des données valides"""
        form = EventForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_dates(self):
        """Test avec des dates invalides"""
        # Date de fin avant la date de début
        invalid_data = self.valid_data.copy()
        invalid_data['end_date'] = timezone.now()
        invalid_data['start_date'] = timezone.now() + timedelta(days=1)
        form = EventForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)

    def test_past_start_date(self):
        """Test avec une date de début dans le passé"""
        invalid_data = self.valid_data.copy()
        invalid_data['start_date'] = timezone.now() - timedelta(days=1)
        form = EventForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)

    def test_negative_capacity(self):
        """Test avec une capacité négative"""
        invalid_data = self.valid_data.copy()
        invalid_data['capacity'] = -1
        form = EventForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('capacity', form.errors)

    def test_negative_price(self):
        """Test avec un prix négatif"""
        invalid_data = self.valid_data.copy()
        invalid_data['price'] = -50.00
        form = EventForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_missing_required_fields(self):
        """Test avec des champs requis manquants"""
        required_fields = ['title', 'description', 'location', 'start_date', 'end_date', 'capacity']
        for field in required_fields:
            invalid_data = self.valid_data.copy()
            invalid_data.pop(field)
            form = EventForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_title_max_length(self):
        """Test avec un titre trop long"""
        invalid_data = self.valid_data.copy()
        invalid_data['title'] = 'A' * 201  # Dépasse la limite de 200 caractères
        form = EventForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_image_upload(self):
        """Test le téléchargement d'image"""
        # Créer un faux fichier image
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # Contenu vide pour le test
            content_type='image/jpeg'
        )
        
        # Ajouter l'image aux données valides
        data_with_image = self.valid_data.copy()
        files = {'image': image_file}
        
        form = EventForm(data=data_with_image, files=files)
        self.assertTrue(form.is_valid())

    def test_invalid_image_format(self):
        """Test avec un format d'image invalide"""
        # Créer un faux fichier non-image
        invalid_file = SimpleUploadedFile(
            name='test.txt',
            content=b'hello world',
            content_type='text/plain'
        )
        
        data_with_invalid_file = self.valid_data.copy()
        files = {'image': invalid_file}
        
        form = EventForm(data=data_with_invalid_file, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors) 