import stripe
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from .cart import Cart
from django.contrib.auth.decorators import login_required
from gym_app.models import CatalogService, Plan, Subscription
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings


def cart_summary(request):
    cart = Cart(request)
    cart_plans = cart.get_plans()
    cart_services = cart.get_services()
    totaltvac = cart.cart_total()
    return render(request, 'cart_summary.html', {
        "cart_plans": cart_plans,
        "cart_services": cart_services,
        "totaltvac": totaltvac,
    })

def cart_add_plan(request, plan_id):
    cart = Cart(request)
    plan = get_object_or_404(Plan, id=plan_id)
    cart.add_plan(plan=plan)
    return JsonResponse({'qty': len(cart)})

def cart_add_service(request, service_id):
    cart = Cart(request)
    service = get_object_or_404(CatalogService, id=service_id)
    cart.add_service(service=service)
    return JsonResponse({'qty': len(cart)})

def cart_delete(request, item_id):
    cart = Cart(request)
    cart.delete(item_id)
    messages.success(request, "Élément supprimé du panier.")
    return redirect('cart:cart_summary')

def cart_update(request):
    pass

@login_required
def create_checkout_session(request):
    cart = Cart(request)
    total_amount = int(cart.cart_total() * 100)
    
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': "Votre panier BE-FIT",
                },
                'unit_amount': total_amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('cart:payment_success')),
        cancel_url=request.build_absolute_uri(reverse('cart:payment_cancelled')),
    )

    return JsonResponse({
        'id': checkout_session.id
    })

def checkout(request):
    return render(request, 'checkout.html')

class CheckoutSessionView(View):
    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        total_amount = int(cart.cart_total() * 100)
        YOUR_DOMAIN = 'http://127.0.0.1:8000'
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': "Votre panier BE-FIT",
                        },
                        'unit_amount': total_amount,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/cart/payment_success',
            cancel_url=YOUR_DOMAIN + '/cart/payment_cancelled/',
        )
        return redirect(session.url, code=303)

def payment_success(request):
    cart = Cart(request)
    cart.clear()
    return render(request, 'payment_success.html')

def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')

def payment_failed(request):
    return render(request, 'payment_failed.html')




# # Gestion du succès du paiement
# @login_required
# def payment_success(request):
#     session_id = request.GET.get('session_id')
#     session = stripe.checkout.Session.retrieve(session_id)

#     if session.payment_status == 'paid':
#         plan_id = request.session.get('plan_id')
#         plan = get_object_or_404(Plan, id=plan_id)

#         # Créer une souscription pour l'utilisateur
#         subscription = stripe.Subscription.objects.create(
#             user=request.user,
#             plan=plan,
#             payment_status='paid',
#         )

#         # Mettre à jour l'utilisateur en premium
#         request.user.is_premium = True
#         request.user.save()

#         # Supprimer le plan de la session
#         del request.session['plan_id']

#         return render(request, 'payment_success.html', {'plan': plan})

#     return render(request, 'payment_failed.html')

# # Gestion de l'annulation du paiement
# @login_required
# def payment_cancel(request):
#     return render(request, 'payment_cancel.html')


# # Gestion du succès du paiement
# @login_required
# def payment_success(request):
#     session_id = request.GET.get('session_id')
#     session = stripe.checkout.Session.retrieve(session_id)

#     if session.payment_status == 'paid':
#         plan_id = request.session.get('plan_id')
#         plan = get_object_or_404(Plan, id=plan_id)

#         # Créer une souscription pour l'utilisateur
#         subscription = stripe.Subscription.objects.create(
#             user=request.user,
#             plan=plan,
#             payment_status='paid',
#         )

#         # Mettre à jour l'utilisateur en premium
#         request.user.is_premium = True
#         request.user.save()

#         # Supprimer le plan de la session
#         del request.session['plan_id']

#         return render(request, 'payment_success.html', {'plan': plan})

#     return render(request, 'payment_failed.html')
