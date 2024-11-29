from django.urls import path, include
from django.conf.urls.static import static
from befit_app import settings
from rest_framework.routers import DefaultRouter
from . import views


# Initialisation du routeur pour DRF
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'plans', views.PlanViewSet)
router.register(r'coaches', views.CoachViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet)
router.register(r'purchase_history', views.PurchaseHistoryViewSet)
router.register(r'workouts', views.WorkoutViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'workout_schedules', views.WorkoutScheduleViewSet)
router.register(r'workout_participations', views.WorkoutParticipationViewSet)
router.register(r'coaches', views.CoachViewSet)
router.register(r'workout_images', views.WorkoutImageViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'messages', views.MessageViewSet)

# Création des URLs pour chaque mois
months = [
    'july', 'august', 'september', 'october', 'november', 'december',
    'january', 'february', 'march', 'april', 'may', 'june'
]

# Création des URLs mensuelles pour l'API
month_urls = [
    path(f'{month}/2024/', include(router.urls)) for month in months
]

# Ajout des points de terminaison pour l'API
urlpatterns = [
    path('', include(router.urls)),  # Point d'entrée principal sans '/api/'
] + month_urls  # Ajouter les routes mensuelles

# Ajout des fichiers statiques
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
