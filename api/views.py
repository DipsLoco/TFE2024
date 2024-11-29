from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from api.models import Plan, Coach, Subscription, PurchaseHistory, Workout, Review, WorkoutSchedule
from .serializers import UserSerializer, PlanSerializer, CoachSerializer, SubscriptionSerializer, \
    PurchaseHistorySerializer, WorkoutSerializer, ReviewSerializer, WorkoutScheduleSerializer
from rest_framework import viewsets
from gym_app.models import WorkoutParticipation, Coach, WorkoutImage, Location, Message, WorkoutSchedule
from .serializers import (
    WorkoutParticipationSerializer, CoachSerializer, WorkoutImageSerializer, 
    LocationSerializer, MessageSerializer, WorkoutScheduleSerializer
)
from rest_framework import status

# Utilisation de get_user_model pour s'assurer que le modèle User personnalisé est utilisé
User = get_user_model()

# ViewSet pour User
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Permet l'accès sans authentification, changer en [IsAuthenticated] si nécessaire

# ViewSet pour Plan
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [AllowAny] 

# ViewSet pour Coach
class CoachViewSet(viewsets.ModelViewSet):
    queryset = Coach.objects.all()
    serializer_class = CoachSerializer
    permission_classes = [AllowAny]  
# ViewSet pour Subscription
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny]  

# ViewSet pour PurchaseHistory
class PurchaseHistoryViewSet(viewsets.ModelViewSet):
    queryset = PurchaseHistory.objects.all()
    serializer_class = PurchaseHistorySerializer
    permission_classes = [AllowAny]  

# ViewSet pour Workout
class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [AllowAny]  

# ViewSet pour Review
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny] 

# ViewSet pour WorkoutSchedule
class WorkoutScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSchedule.objects.all()
    serializer_class = WorkoutScheduleSerializer
    permission_classes = [AllowAny]  # 

class WorkoutParticipationViewSet(viewsets.ModelViewSet):
    queryset = WorkoutParticipation.objects.all()
    serializer_class = WorkoutParticipationSerializer
    permission_classes = [AllowAny]  

class CoachViewSet(viewsets.ModelViewSet):
    queryset = Coach.objects.all()
    serializer_class = CoachSerializer
    permission_classes = [AllowAny]  

class WorkoutImageViewSet(viewsets.ModelViewSet):
    queryset = WorkoutImage.objects.all()
    serializer_class = WorkoutImageSerializer
    permission_classes = [AllowAny]  

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [AllowAny] 

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]  








# Exemple de vue simple pour tester
class HelloWorldAPIView(APIView):
    def get(self, request, format=None):
        return Response({"message": "Hello, world!"})


    







