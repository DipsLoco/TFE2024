from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns


app_name = 'cart'
app_name = 'gym°app'


# URLs non dépendantes de la langue (comme l'administration)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    # path('gym/', include('gym_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# URLs avec le préfixe de langue
urlpatterns += i18n_patterns(
    path('', include('gym_app.urls')),  # Application principale
    path('gym/', include('gym_app.urls')),
    path('cart/', include('cart.urls', namespace='cart')),  # Inclut les URLs de l'application cart avec le namespace 'cart'  # Application du panier
)