from django.urls import path
from cart import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_summary, name='cart_summary'),
    path('add_plan/<int:plan_id>/', views.cart_add_plan, name='add_plan_to_cart'),  # Pour ajouter un plan
    # path('add_service/<int:service_id>/', views.cart_add_service, name='add_service_to_cart'),  # Pour ajouter un service
    path('add_service/<int:service_id>/', views.cart_add_service, name='cart_add_service'),
    path('delete/<str:item_type>/<int:item_id>/', views.cart_delete, name='cart_delete'),
    path('delete_selected_items/', views.delete_selected_items, name='delete_selected_items'),
    path('clear/', views.cart_clear, name='cart_clear'),
    path('update/<str:item_type>/<int:item_id>/', views.cart_update, name='cart_update'),
    path('checkout_session/', views.CheckoutSessionView.as_view(), name='checkout_session'),
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
    path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),
]
