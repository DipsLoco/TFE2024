import stripe
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from .cart import Cart
from django.contrib.auth.decorators import login_required
from gym_app.models import Plan, Subscription
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings


def cart_summary(request):
    cart = Cart(request)
    # Appel correct de la méthode get_prods() avec des parenthèses
    cart_plans = cart.get_prods()
    totaltvac, plans = cart.cart_total()
    return render(request, 'cart_summary.html', {"cart_plans": cart_plans, 'totaltvac': totaltvac, 'plans': plans})


def cart_add(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        plan_id = int(request.POST.get('plan_id'))
        plan = get_object_or_404(Plan, id=plan_id)  # Plan avec majuscule

        cart.add(plan=plan)

        # Utiliser len(cart) pour obtenir la taille du panier
        cart_quantity = len(cart)
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, "Abonnement ajouté à votre sélection...")
        return response


def cart_delete(request, plan_id):
    """
    Supprime un élément du panier.
    """
    cart = Cart(request)
    plan = get_object_or_404(Plan, id=plan_id)
    cart.delete(plan_id)
    messages.success(request, "Plan supprimé du panier.")
    return redirect('cart_summary')


def cart_update(request):
    pass


@login_required
def create_checkout_session(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    # Créer une session de paiement Stripe
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': plan.name,
                },
                'unit_amount': plan.price * 100,  # Prix en centimes
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(
            '/payment/success/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/payment/cancel/'),
    )

    # Sauvegarder le plan dans la session pour l'utilisateur
    request.session['plan_id'] = plan.id

    return JsonResponse({
        'id': checkout_session.id
    })


def checkout(request, plan_id):
    return render(request, 'checkout.html')


class CheckoutSessionView(View):
    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        # plan_id = kwargs.get('plan_id')
        # plan = get_object_or_404(Plan, pk=plan_id)
        #  Calcul du montant total de l'acompte (10%) pour toutes les voitures du panier
        totaltvac, plans = cart.cart_total()

        YOUR_DOMAIN = 'http://127.0.0.1:8000'
        montant = int(totaltvac * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f"Votre plan",
                        },
                        'unit_amount': montant,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/cart/payment_success',  # URL de succès
            cancel_url=YOUR_DOMAIN + '/payment_cancelled/',  # Redirection en cas d'annulation
        )
        return redirect(session.url, code=303)


def payment_success(request):
    cart = Cart(request)
    cart.clear()  # Vider le panier après paiement réussi

    


    plan_id = request.session.get('plan_id')
    plan = get_object_or_404(Plan, id=2)

    subscription = Subscription.objects.create(
        user=request.user,
        plan=plan,
        payment_status='paid',
    )

    # Mettre à jour l'utilisateur en premium
    request.user.is_premium = True
    request.user.save()
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
