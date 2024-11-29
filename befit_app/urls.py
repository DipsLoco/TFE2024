from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Inclure les chemins de langue
    # path('api/', include('api.urls')),  # Inclut les URLs de l'application API sans prefixe de langue ex : http://127.0.0.1:8000/api
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# URLs avec préfixe linguistique
urlpatterns += i18n_patterns(
    path('api/', include('api.urls')),  # Inclut les URLs de l'application API avec le prefixe de langue devant ex en local : http://127.0.0.1:8000/fr/api
    path('', include('gym_app.urls')),  # Inclut l'application principale 'gym_app' avec préfixe de langue
    path('gym/', include('gym_app.urls')),  # Même pour la route gym/
    path('cart/', include('cart.urls', namespace='cart')),  # Inclut 'cart' avec son propre namespace
)
