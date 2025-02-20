from rest_framework import serializers
from .models import (
    EventCategory, JobCategory, Event, EventImage,
    EventAgenda, EventJobCategoryLinking, EventMember,
    EventUserWishList, UserCoin
)
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = '__all__'

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = '__all__'

class EventAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAgenda
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    image = EventImageSerializer(source='eventimage', read_only=True)
    agendas = EventAgendaSerializer(source='eventagenda_set', many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    job_category_name = serializers.CharField(source='job_category.name', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'

class EventJobCategoryLinkingSerializer(serializers.ModelSerializer):
    job_category_name = serializers.CharField(source='job_category.name', read_only=True)
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = EventJobCategoryLinking
        fields = '__all__'

class EventMemberSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = EventMember
        fields = '__all__'

class EventUserWishListSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = EventUserWishList
        fields = '__all__'

class UserCoinSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserCoin
        fields = '__all__'
