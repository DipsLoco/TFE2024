from datetime import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.db import IntegrityError
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from .cart import Cart
from gym_app.models import CatalogService, Plan, PurchaseHistory, Subscription, User, Message, ServiceImage

# Stripe configuration
stripe.api_key = settings.STRIPE_SECRET_KEY

# Vue de résumé du panier
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

# Ajouter un plan au panier
def cart_add_plan(request, plan_id):
    cart = Cart(request)
    plan = get_object_or_404(Plan, id=plan_id)
    cart.add_plan(plan=plan)
    messages.success(request, "Plan ajouté au panier avec succès.")
    return redirect('cart:cart_summary')

# Ajouter un service au panier avec une image spécifique si sélectionnée
def cart_add_service(request, service_id):
    image_id = request.GET.get('image_id')  # Récupère l'image ID depuis la requête GET
    cart = Cart(request)
    service = get_object_or_404(CatalogService, id=service_id)
    cart.add_service(service=service, image_id=image_id)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': "Service ajouté au panier avec succès.",
            'cart_count': len(cart)
        })

    messages.success(request, "Service ajouté au panier avec succès.")
    return redirect('cart:cart_summary')

# def cart_add_service(request, service_id):
#     image_id = request.GET.get('image_id')  # Récupère l'image ID depuis la requête GET
#     cart = Cart(request)
#     service = get_object_or_404(CatalogService, id=service_id)
#     cart.add_service(service=service, image_id=image_id)
#     messages.success(request, "Service ajouté au panier avec succès.")
#     return redirect('cart:cart_summary')

# Supprimer un élément du panier
def cart_delete(request, item_type, item_id):
    cart = Cart(request)
    cart.delete(item_id=item_id, item_type=item_type)
    messages.success(request, f"{item_type.capitalize()} supprimé du panier.")
    return redirect('cart:cart_summary')
from django.shortcuts import redirect
from django.contrib import messages
from .cart import Cart

def delete_selected_items(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        cart = Cart(request)
        
        for item in selected_items:
            item_type, item_id = item.split('-')
            cart.delete(item_id=item_id, item_type=item_type)
        
        messages.success(request, "Les articles sélectionnés ont été supprimés du panier.")
    return redirect('cart:cart_summary')


# Effacer tout le panier
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, "Panier vidé avec succès.")
    return redirect('cart:cart_summary')

# Mise à jour d'un élément dans le panier
def cart_update(request, item_type, item_id):
    cart = Cart(request)
    if item_type == 'plan':
        plan = get_object_or_404(Plan, id=item_id)
        cart.update(item_id, item_type='plan', item=plan)
        messages.success(request, "Le plan a été mis à jour dans le panier.")
    elif item_type == 'service':
        service = get_object_or_404(CatalogService, id=item_id)
        cart.update(item_id, item_type='service', item=service)
        messages.success(request, "Le service a été mis à jour dans le panier.")
    return redirect('cart:cart_summary')

# CheckoutSessionView pour créer une session de paiement
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
            success_url=YOUR_DOMAIN + '/cart/payment_success/',
            cancel_url=YOUR_DOMAIN + '/cart/payment_cancelled/',
        )
        return redirect(session.url, code=303)

# Vue pour afficher la page de checkout
@login_required
def checkout(request, plan_id=None):
    cart = Cart(request)

    # Si un plan_id est fourni, on l'ajoute au panier
    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)
        cart.add_plan(plan=plan)
    
    # Récupérer les plans et les services dans le panier
    cart_plans = cart.get_plans()  # Récupère les plans du panier
    cart_services = cart.get_services()  # Récupère les services du panier

    # Calcul du montant total du panier
    total_amount = cart.cart_total()

    return render(request, 'checkout.html', {
        'cart_plans': cart_plans,
        'cart_services': cart_services,
        'total_amount': total_amount,
    })

# Créer une session de paiement Stripe
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

    return JsonResponse({'id': checkout_session.id})

# Gérer le succès du paiement pour les plans et services
@login_required
def payment_success(request):
    # Obtenir le panier et ses contenus
    cart = Cart(request)
    purchased_plans = cart.get_plans()
    purchased_services = cart.get_services()
    cart.clear()

    # Préparer les données pour le template
    plan = purchased_plans[0] if purchased_plans else None  # Utiliser le premier plan acheté, si disponible
    service = purchased_services[0] if purchased_services else None  # Utiliser le premier service acheté, si disponible

    # Enregistrement des plans achetés dans l'historique et création de la souscription
    for plan_item in purchased_plans:
        try:
            # Créer une souscription pour chaque plan acheté
            subscription = Subscription.objects.create(
                user=request.user,
                plan=plan_item,
                payment_status='paid',
            )
            print("Subscription enregistrée pour le plan:", plan_item.name)

            # Enregistrement dans l'historique des achats pour le plan
            PurchaseHistory.objects.create(
                user=request.user,
                item_type='plan',
                price=plan_item.price,
                plan=plan_item,
                purchase_date=subscription.start_date  # Utiliser la date de souscription pour éviter les erreurs de période
            )
            print("PurchaseHistory enregistré pour le plan:", plan_item.name)
            
            # Mise à jour de l'état premium de l'utilisateur
            request.user.is_premium = True
            request.user.save()

        except Exception as e:
            print(f"Erreur lors de l'enregistrement de l'achat de plan: {e}")

    # Enregistrement des services achetés dans l'historique
    for service_item in purchased_services:
        try:
            price = service_item.images.first().price if service_item.images.exists() and service_item.images.first().price else service_item.price
            PurchaseHistory.objects.create(
                user=request.user,
                item_type='service',
                price=price,
                catalog_service=service_item
            )
            print("PurchaseHistory enregistré pour le service:", service_item.name)
        except IntegrityError as e:
            print(f"Erreur lors de l'enregistrement de l'achat de service: {e}")

    # Envoi de confirmation de souscription par message si un administrateur est trouvé
    try:
        admin_user = User.objects.filter(role='admin').first()  # Utiliser le premier admin disponible
        if admin_user:
            Message.objects.create(
                sender=admin_user,
                recipient=request.user,
                subject="Confirmation de souscription",
                body="Merci pour votre souscription. Profitez de vos avantages premium avec BE-FIT."
            )
            print("Message de confirmation envoyé.")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message de confirmation : {e}")

    return render(request, 'payment_success.html', {'plan': plan, 'service': service})

# Pages d'annulation et d'échec de paiement
def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')

def payment_failed(request):
    return render(request, 'payment_failed.html')
