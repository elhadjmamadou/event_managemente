from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
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

def home(request):
    return HttpResponse("Bienvenue dans mon site")

class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event/create_event.html'
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

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
    paginate_by = 12  # Nombre d'événements par page

    def get_queryset(self):
        queryset = Event.objects.filter(Q(is_public=True) | Q(organizer=self.request.user)) if self.request.user.is_authenticated else Event.objects.filter(is_public=True)
        
        # Filtres
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
                queryset = queryset.filter(start_date__date__range=[today.date(), today.date() + timezone.timedelta(days=7)])
            elif date_filter == 'month':
                queryset = queryset.filter(start_date__date__range=[today.date(), today.date() + timezone.timedelta(days=30)])
                
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        return queryset.order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['current_date'] = self.request.GET.get('date')
        context['current_location'] = self.request.GET.get('location')
        
        # Add user_tickets to context
        if self.request.user.is_authenticated:
            user_tickets = Ticket.objects.filter(user=self.request.user).values_list('event_id', flat=True)
            context['user_tickets'] = set(user_tickets)
        else:
            context['user_tickets'] = set()
            
        return context


def private_event_view(request, private_key):
    # Récupérer l'événement privé à partir de la clé privée
    event = get_object_or_404(Event, private_key=private_key, is_public=False)
    
    # Passer l'événement au template pour l'afficher
    return render(request, 'event/private_event_detail.html', {'event': event})


class EventDetailView(DetailView, LoginRequiredMixin):
    model = Event
    template_name = 'event/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        """
        Cette méthode s'assure que seules les événements publics sont affichés.
        """
        return Event.objects.filter(is_public=True)


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if not event.user_can_register(request.user):
        if event.is_expired():
            messages.error(request, "Cet événement est déjà terminé.")
        elif not event.has_available_spots():
            messages.error(request, "Il n'y a plus de places disponibles pour cet événement.")
        elif event.ticket_set.filter(user=request.user).exists():
            messages.error(request, "Vous êtes déjà inscrit à cet événement.")
        else:
            messages.error(request, "Vous ne pouvez pas vous inscrire à cet événement.")
        return redirect('event_detail', pk=event_id)

    # Créer le ticket
    ticket_type = 'paid' if event.price else 'free'
    ticket = Ticket.objects.create(
        user=request.user,
        event=event,
        ticket_type=ticket_type,
        is_paid=ticket_type == 'free'
    )
    
    # Send confirmation email
    subject = f"Confirmation d'inscription à {event.title}"
    html_message = render_to_string('event/registration_email.html', {
        'event': event,
        'user': request.user,
        'ticket': ticket
    })
    plain_message = strip_tags(html_message)
    email = EmailMessage(
        subject,
        html_message,
        to=[request.user.email]
    )
    email.content_subtype = "html"
    email.send()
    
    messages.success(request, "Vous êtes maintenant inscrit à cet événement ! Un email de confirmation vous a été envoyé.")
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