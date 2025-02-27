from django.urls import path
from .views import (EventCreateView, EventUpdateView, EventDeleteView, private_event_view,
                    EventDetailView, EventListView, register_for_event, OrganizerDashboardView)

urlpatterns = [
    path('create/', EventCreateView.as_view(), name='create_event'),
    path('list/', EventListView.as_view(), name='list_event'),
    path('<int:pk>/detail/', EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/update/', EventUpdateView.as_view(), name='update_event'),
    path('<int:pk>/delete/', EventDeleteView.as_view(), name='delete_event'),
    path('<int:event_id>/register/', register_for_event, name='register_event'),
    path('private/<uuid:private_key>/', private_event_view, name='private_event'),
    path('dashboard/', OrganizerDashboardView.as_view(), name='organizer_dashboard'),
]
