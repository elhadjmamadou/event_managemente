from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Event, Category, Ticket
from .forms import EventForm
from django.shortcuts import render,HttpResponse
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def home(request):
    return HttpResponse("Bienvenue dans mon site")

class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event/create_event.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        response = super().form_valid(form)
        
        # Si l'événement est privé, générer et afficher le lien privé
        if not form.instance.is_public:
            private_url = self.request.build_absolute_uri(
                reverse('private_event', kwargs={'private_key': form.instance.private_key})
            )
            messages.success(
                self.request,
                f'Événement privé créé avec succès ! Partagez ce lien avec vos invités : {private_url}'
            )
        else:
            messages.success(self.request, 'Événement public créé avec succès !')
            
        return response

    def test_func(self):
        return self.request.user.is_organisateur

    def handle_no_permission(self):
        return redirect('home')  

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    template_name = 'event/event_update.html'
    fields = ['title', 'description', 'image', 'location', 'start_date', 'end_date', 'price', 'capacity', 'category']
    success_url = reverse_lazy('home')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

    def handle_no_permission(self):
        return redirect('home')

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'event/event_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

    def handle_no_permission(self):
        return redirect('home')


class EventListView(ListView):
    model = Event
    template_name = 'event/event_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        # Base queryset : événements publics uniquement
        queryset = Event.objects.filter(is_public=True)
        
        # Si l'utilisateur est connecté, ajouter ses événements privés
        if self.request.user.is_authenticated:
            # Événements publics + événements privés où l'utilisateur est organisateur ou inscrit
            queryset = Event.objects.filter(
                Q(is_public=True) |
                Q(organizer=self.request.user) |
                Q(ticket__user=self.request.user)
            ).distinct()
        
        # Appliquer les filtres
        category = self.request.GET.get('category')
        date_filter = self.request.GET.get('date')
        location = self.request.GET.get('location')
        
        if category:
            queryset = queryset.filter(category__id=category)
            
        if date_filter:
            today = timezone.now()
            if date_filter == 'today':
                queryset = queryset.filter(start_date__date=today.date())
            elif date_filter == 'week':
                queryset = queryset.filter(
                    start_date__date__range=[today.date(), today.date() + timezone.timedelta(days=7)]
                )
            elif date_filter == 'month':
                queryset = queryset.filter(
                    start_date__date__range=[today.date(), today.date() + timezone.timedelta(days=30)]
                )
                
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        return queryset.order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['current_date'] = self.request.GET.get('date')
        context['current_location'] = self.request.GET.get('location')
        
        # Ajouter les tickets de l'utilisateur au contexte
        if self.request.user.is_authenticated:
            user_tickets = Ticket.objects.filter(user=self.request.user).values_list('event_id', flat=True)
            context['user_tickets'] = set(user_tickets)
        else:
            context['user_tickets'] = set()
            
        return context


@login_required
def private_event_view(request, private_key):
    # Récupérer l'événement privé à partir de la clé privée
    event = get_object_or_404(Event, private_key=private_key)
    
    # Vérifier si l'événement est vraiment privé
    if event.is_public:
        messages.error(request, "Cet événement est public et accessible via la liste des événements.")
        return redirect('event_detail', pk=event.id)
    
    # Vérifier si l'utilisateur est l'organisateur ou déjà inscrit
    is_organizer = event.organizer == request.user
    is_registered = event.ticket_set.filter(user=request.user).exists()
    
    # Récupérer la liste des participants si l'utilisateur est l'organisateur ou inscrit
    participants = None
    if is_organizer or is_registered:
        participants = event.ticket_set.filter(is_paid=True).select_related('user')
    
    context = {
        'event': event,
        'is_organizer': is_organizer,
        'is_registered': is_registered,
        'participants': participants,
    }
    
    return render(request, 'event/private_event_detail.html', context)


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'event/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        """
        Cette méthode s'assure que l'utilisateur a le droit de voir l'événement.
        """
        return Event.objects.filter(
            Q(is_public=True) | 
            Q(organizer=self.request.user) |
            Q(ticket__user=self.request.user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Vérifier si l'utilisateur est l'organisateur ou déjà inscrit
        context['is_organizer'] = event.organizer == self.request.user
        context['is_registered'] = event.ticket_set.filter(user=self.request.user).exists()
        
        # Ajouter la liste des participants
        if context['is_organizer'] or context['is_registered']:
            context['participants'] = event.ticket_set.filter(is_paid=True).select_related('user')
        
        # Générer le lien privé si nécessaire
        if not event.is_public and context['is_organizer']:
            context['private_url'] = self.request.build_absolute_uri(
                reverse('event_detail', kwargs={'pk': event.id})
            )
        
        return context


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Vérifier si l'utilisateur peut s'inscrire
    if not event.user_can_register(request.user):
        if request.user == event.organizer:
            messages.error(request, "Vous ne pouvez pas vous inscrire à votre propre événement.")
        elif event.is_expired():
            messages.error(request, "Cet événement est déjà terminé.")
        elif not event.has_available_spots():
            messages.error(request, "Il n'y a plus de places disponibles pour cet événement.")
        elif event.ticket_set.filter(user=request.user).exists():
            messages.error(request, "Vous êtes déjà inscrit à cet événement.")
        return redirect('event_detail', pk=event_id)

    # Créer le ticket
    ticket = Ticket.objects.create(
        user=request.user,
        event=event,
        ticket_type='free' if not event.price else 'paid',
        is_paid=True  # Tous les tickets sont marqués comme payés
    )
    
    # Envoyer l'email de confirmation
    subject = f"Confirmation d'inscription - {event.title}"
    html_message = render_to_string('event/registration_email.html', {
        'user': request.user,
        'event': event,
        'ticket': ticket
    })
    
    try:
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[request.user.email]
        )
        email.content_subtype = "html"
        email.send()
        messages.success(request, "Votre inscription est confirmée ! Un email de confirmation vous a été envoyé.")
    except Exception as e:
        messages.warning(request, "Inscription réussie, mais l'envoi de l'email de confirmation a échoué.")
    
    return redirect('event_detail', pk=event_id)

class OrganizerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'event/organizer_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Récupérer les événements de l'organisateur
        events = Event.objects.filter(organizer=user).annotate(
            total_tickets=Count('ticket'),
            total_revenue=Sum('ticket__event__price', filter=Q(ticket__is_paid=True))
        )
        
        # Statistiques globales
        total_events = events.count()
        total_registrations = events.aggregate(total=Sum('total_tickets'))['total'] or 0
        total_revenue = events.aggregate(total=Sum('total_revenue'))['total'] or 0
        
        context.update({
            'events': events,
            'total_events': total_events,
            'total_registrations': total_registrations,
            'total_revenue': total_revenue,
        })
        return context