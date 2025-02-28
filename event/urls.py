from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.EventListView.as_view(), name='list_event'),
    path('events/create/', views.EventCreateView.as_view(), name='create_event'),
    path('events/<uuid:private_key>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<uuid:private_key>/update/', views.EventUpdateView.as_view(), name='update_event'),
    path('events/<uuid:private_key>/delete/', views.EventDeleteView.as_view(), name='delete_event'),
    path('events/<uuid:private_key>/register/', views.register_for_event, name='register_for_event'),
    path('dashboard/', views.OrganizerDashboardView.as_view(), name='organizer_dashboard'),
]
