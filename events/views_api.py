from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    EventCategory, JobCategory, Event, EventImage,
    EventAgenda, EventJobCategoryLinking, EventMember,
    EventUserWishList, UserCoin
)
from .serializers import (
    EventCategorySerializer, JobCategorySerializer, EventSerializer,
    EventImageSerializer, EventAgendaSerializer, EventJobCategoryLinkingSerializer,
    EventMemberSerializer, EventUserWishListSerializer, UserCoinSerializer,
    UserSerializer
)
from django.contrib.auth.models import User

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email', 'first_name', 'last_name']

class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'code']
    ordering_fields = ['priority', 'created_date', 'name']
    filterset_fields = ['status']

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user, updated_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_user=self.request.user)

class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'venue']
    ordering_fields = ['start_date', 'end_date', 'points', 'created_date']
    filterset_fields = ['category', 'job_category', 'status', 'scheduled_status']

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user, updated_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_user=self.request.user)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        event = self.get_object()
        user = request.user

        # Check if user already joined
        if EventMember.objects.filter(event=event, user=user).exists():
            return Response({'detail': 'Already joined this event'}, status=400)

        # Check if event has reached maximum attendees
        current_attendees = EventMember.objects.filter(event=event).count()
        if current_attendees >= event.maximum_attende:
            return Response({'detail': 'Event has reached maximum attendees'}, status=400)

        member = EventMember.objects.create(
            event=event,
            user=user,
            attend_status='waiting',
            created_user=user,
            updated_user=user,
            status='active'
        )

        return Response(EventMemberSerializer(member).data)

    @action(detail=True, methods=['post'])
    def toggle_wishlist(self, request, pk=None):
        event = self.get_object()
        user = request.user
        wishlist_exists = EventUserWishList.objects.filter(event=event, user=user).exists()

        if wishlist_exists:
            EventUserWishList.objects.filter(event=event, user=user).delete()
            return Response({'detail': 'Removed from wishlist'})
        else:
            wishlist = EventUserWishList.objects.create(
                event=event,
                user=user,
                created_user=user,
                updated_user=user,
                status='active'
            )
            return Response(EventUserWishListSerializer(wishlist).data)

    @action(detail=False)
    def upcoming(self, request):
        from django.utils import timezone
        upcoming_events = Event.objects.filter(
            start_date__gte=timezone.now().date(),
            status='active'
        ).order_by('start_date')
        page = self.paginate_queryset(upcoming_events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)

class EventImageViewSet(viewsets.ModelViewSet):
    queryset = EventImage.objects.all()
    serializer_class = EventImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event']

class EventAgendaViewSet(viewsets.ModelViewSet):
    queryset = EventAgenda.objects.all()
    serializer_class = EventAgendaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['start_time', 'end_time']
    filterset_fields = ['event', 'speaker_name', 'venue_name']

class EventJobCategoryLinkingViewSet(viewsets.ModelViewSet):
    queryset = EventJobCategoryLinking.objects.all()
    serializer_class = EventJobCategoryLinkingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'job_category', 'status']

class EventMemberViewSet(viewsets.ModelViewSet):
    queryset = EventMember.objects.all()
    serializer_class = EventMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['created_date']
    filterset_fields = ['event', 'user', 'attend_status', 'status']

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user, updated_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_user=self.request.user)

    @action(detail=False)
    def my_events(self, request):
        my_events = EventMember.objects.filter(user=request.user)
        page = self.paginate_queryset(my_events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(my_events, many=True)
        return Response(serializer.data)

class EventUserWishListViewSet(viewsets.ModelViewSet):
    queryset = EventUserWishList.objects.all()
    serializer_class = EventUserWishListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['created_date']
    filterset_fields = ['event', 'user', 'status']

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user, updated_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_user=self.request.user)

    @action(detail=False)
    def my_wishlist(self, request):
        my_wishlist = EventUserWishList.objects.filter(user=request.user, status='active')
        page = self.paginate_queryset(my_wishlist)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(my_wishlist, many=True)
        return Response(serializer.data)

class UserCoinViewSet(viewsets.ModelViewSet):
    queryset = UserCoin.objects.all()
    serializer_class = UserCoinSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['gain_coin', 'created_date']
    filterset_fields = ['user', 'gain_type', 'status']

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user, updated_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_user=self.request.user)

    @action(detail=False)
    def my_coins(self, request):
        try:
            my_coins = UserCoin.objects.get(user=request.user)
            serializer = self.get_serializer(my_coins)
            return Response(serializer.data)
        except UserCoin.DoesNotExist:
            return Response({'detail': 'No coins record found'}, status=404)
