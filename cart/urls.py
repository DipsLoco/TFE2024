from django.urls import path
from cart import views




urlpatterns = [
    path('', views.cart_summary, name='cart_summary'), 
    path('add/', views.cart_add, name='cart_add'), 
    path('delete/', views.cart_delete, name='cart_delete'), 
    path('update/', views.cart_update, name='cart_update'), 
] 




# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) : 
# Cette ligne permet de servir les fichiers médias (comme les images téléchargées) pendant le développement lorsque le mode debug est activé.

# if settings.DEBUG: : Cela garantit que les fichiers médias sont uniquement servis par Django lorsque vous êtes en mode développement.
#  En production, un serveur web comme Nginx ou Apache s'occupera de cette tâche.