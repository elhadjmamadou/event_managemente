from django.urls import path

from .views import (
    EventCategoryListView,
    EventCategoryCreateView,
    EventCategoryUpdateView,
    EventCategoryDeleteView,
    EventCreateView,
    EventListView,
    EventUpdateView,
    EventDetailView,
    EventDeleteView,
    AddEventMemberCreateView,
    JoinEventListView,
    RemoveEventMemberDeleteView,
    EventUserWishListView,
    AddEventUserWishListCreateView,
    RemoveEventUserWishDeleteView,
    UpdateEventStatusView,
    CompleteEventList,
    AbsenseUserList,
    CompleteEventUserList,
    CreateUserMark,
    UserMarkList,
    search_event_category,
    search_event,
    create_event,
)



from django.urls import path, include
from rest_framework import routers
from .views_api import (
    EventCategoryViewSet, JobCategoryViewSet, EventViewSet,
    EventImageViewSet, EventAgendaViewSet, EventJobCategoryLinkingViewSet,
    EventMemberViewSet, EventUserWishListViewSet, UserCoinViewSet,
    UserViewSet
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'event-categories', EventCategoryViewSet)
router.register(r'job-categories', JobCategoryViewSet)
router.register(r'events', EventViewSet)
router.register(r'event-images', EventImageViewSet)
router.register(r'event-agendas', EventAgendaViewSet)
router.register(r'event-job-categories', EventJobCategoryLinkingViewSet)
router.register(r'event-members', EventMemberViewSet)
router.register(r'event-wishlists', EventUserWishListViewSet)
router.register(r'user-coins', UserCoinViewSet)



urlpatterns = [
    path('category-list/', EventCategoryListView.as_view(), name='event-category-list'),
    path('create-category/', EventCategoryCreateView.as_view(), name='create-event-category'),
    path('category/<int:pk>/edit/', EventCategoryUpdateView.as_view(), name='edit-event-category'),
    path('category/<int:pk>/delete/', EventCategoryDeleteView.as_view(), name='delete-event-category'),
    path('event-create/', EventCreateView.as_view(), name='event-create'),
    path('event-list/', EventListView.as_view(), name='event-list'),
    path('event/<int:pk>/edit/', EventUpdateView.as_view(), name='event-edit'),
    path('detail/<int:pk>', EventDetailView.as_view(), name='event-detail'),
    path('delete/<int:pk>', EventDeleteView.as_view(), name='event-delete'),
    path('add-event-member/', AddEventMemberCreateView.as_view(), name='add-event-member'),
    path('join-event-list/', JoinEventListView.as_view(), name='join-event-list'),
    path('event-member/<int:pk>/remove/', RemoveEventMemberDeleteView.as_view(), name='remove-event-member'),
    path('event-wish-list/', EventUserWishListView.as_view(), name='event-wish-list'),
    path('add-event-wish-user/', AddEventUserWishListCreateView.as_view(), name='add-event-wish-user'),
    path('event-user-wish/<int:pk>/remove/', RemoveEventUserWishDeleteView.as_view(), name='remove-event-user-wish'),
    path('update-status/<int:pk>/event/', UpdateEventStatusView.as_view(), name='update-event-status'),
    path('complete-event/', CompleteEventList.as_view(), name='complete-event'),
    path('absense-user/', AbsenseUserList.as_view(), name='absense-user'),
    path('complete-event-user/', CompleteEventUserList.as_view(), name='complete-event-user'),
    path('create-user-mark/', CreateUserMark.as_view(), name='create-user-mark'),
    path('user-mark/', UserMarkList.as_view(), name='user-mark'),
    path('search_category/', search_event_category, name='search-event-category'),
    path('search_event/', search_event, name='search-event'),
    path('create/', create_event, name='create'),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
