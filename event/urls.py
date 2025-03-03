from django.urls import path
from . import views

urlpatterns = [
    path('', views.EventListView.as_view(), name='list_event'),
    path('events/create/', views.EventCreateView.as_view(), name='create_event'),
    path('events/<uuid:private_key>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:id>/update/', views.EventUpdateView.as_view(), name='update_event'),
    path('events/<int:id>/delete/', views.EventDeleteView.as_view(), name='delete_event'),
    path('events/<uuid:private_key>/register/', views.register_for_event, name='register_for_event'),
    path('events/private/<uuid:private_key>/', views.private_event_view, name='private_event'),
    path('dashboard/', views.OrganizerDashboardView.as_view(), name='organizer_dashboard'),
]
