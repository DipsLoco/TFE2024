from django.urls import path
from cart import views

urlpatterns = [
    path('', views.cart_summary, name='cart_summary'), 
    path('add/', views.cart_add, name='cart_add'), 
    path('delete/<int:plan_id>/', views.cart_delete, name='cart_delete'),  # Ajout de l'ID du plan
    path('update/', views.cart_update, name='cart_update'), 
    path('checkout_session/', views.CheckoutSessionView.as_view(), name='checkout_session'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),  # Paiement échoué
    path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),  # Paiement annulé
    # path('payment_success/<int:subscription_id>/', views.payment_success, name='payment_success'),
]
