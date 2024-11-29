from rest_framework import serializers
from api.models import (User, Plan, Coach, Subscription, PurchaseHistory, Workout, Review, WorkoutSchedule,  WorkoutParticipation, Coach, )
from django.contrib.auth import get_user_model
from gym_app.models import WorkoutParticipation, Coach, WorkoutImage, Location, Message, WorkoutSchedule

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'role', 'first_name', 'last_name', 'email',
            'phone', 'address', 'postal_code', 'is_premium', 'image','date_joined'
        ]

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'

class PurchaseHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PurchaseHistory
        fields = '__all__'

class WorkoutSerializer(serializers.ModelSerializer):
    location = serializers.StringRelatedField()
    coachs = CoachSerializer(many=True, read_only=True)

    class Meta:
        model = Workout
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    workout = WorkoutSerializer(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

class WorkoutScheduleSerializer(serializers.ModelSerializer):
    workout = WorkoutSerializer(read_only=True)
    coach = CoachSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutSchedule
        fields = '__all__'

class WorkoutParticipationSerializer(serializers.ModelSerializer):
    workout_schedule = WorkoutScheduleSerializer()
    participant = UserSerializer()
    
    class Meta:
        model = WorkoutParticipation
        fields = ['id', 'workout_schedule', 'participant', 'present']


class CoachSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Serializer imbriqué pour l'utilisateur associé au coach
    specialties = WorkoutSerializer(many=True)  # Sérialisation des spécialités du coach

    class Meta:
        model = Coach
        fields = ['id', 'username', 'user', 'specialties', 'available', 'image', 'exp', 'about']


class WorkoutImageSerializer(serializers.ModelSerializer):
    workout = WorkoutSerializer()

    class Meta:
        model = WorkoutImage
        fields = ['id', 'workout', 'image', 'description']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'city', 'state', 'postal_code']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    recipient = UserSerializer()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'subject', 'body', 'timestamp', 'is_read', 'is_important', 'is_deleted', 'is_archived', 'is_draft']

# from .serializers import CatalogServiceSerializer

# class SecureCatalogServiceViewSet(viewsets.ModelViewSet):
#     queryset = CatalogService.objects.all()
#     serializer_class = CatalogServiceSerializer
#     permission_classes = [IsAuthenticated]  # Restreint l'accès