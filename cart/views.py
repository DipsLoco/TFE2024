from datetime import datetime, timedelta, timezone
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
from gym_app.models import CatalogService, Plan, PurchaseHistory,  User, Message, ServiceImage,Subscription
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime

print(ServiceImage.objects.all())  # Vérifier que l'accès à ServiceImage fonctionne sans erreur

# Vue de résumé du panier
def cart_summary(request):
    cart = Cart(request)
    cart_plans = cart.get_plans()
    cart_services = cart.get_services()

    # Calcul du total avec les quantités
    totaltvac = cart.cart_total()

    # Ajouter la date du jour et calculer la date d'échéance pour les plans
    for plan in cart_plans:
        plan.start_date = datetime.now()
        plan.end_date = plan.start_date + timedelta(days=plan.duration)

    return render(request, 'cart_summary.html', {
        "cart_plans": cart_plans,
        "cart_services": cart_services,
        "totaltvac": totaltvac,
    })


# Stripe configuration
stripe.api_key = settings.STRIPE_SECRET_KEY

def delete(self, item_id, item_type):
        keys_to_delete = [key for key in self.cart if key.startswith(f'{item_type}-{item_id}')]
        for key in keys_to_delete:
            del self.cart[key]
            print(f"[DEBUG] {item_type.capitalize()} supprimé : {key}")  # Point de débogage
        self.session.modified = True

def clear(self):
        self.cart.clear()
        self.session.modified = True
        print("[DEBUG] Panier vidé.")  # Point de débogage

def cart_total(self):
        total = sum(float(item['prix']) for item in self.cart.values())
        return total




@login_required
def add_plan(self, plan):
        plan_id = f'plan-{plan.id}'
        if plan_id not in self.cart:
            self.cart[plan_id] = {
                'prix': str(plan.price),
                'type': 'plan',
                'duration': plan.duration,
            }
        self.session.modified = True
@login_required
def add_service(self, service, image_id=None):
        service_key = f'service-{service.id}-image-{image_id}' if image_id else f'service-{service.id}'
        if service_key not in self.cart:
            image_price = service.price  # Prix général de CatalogService
            self.cart[service_key] = {'prix': str(image_price), 'type': 'service', 'image_id': image_id}
        self.session.modified = True

def get_plans(self):
        plan_ids = [int(key.split('-')[1]) for key in self.cart if self.cart[key]['type'] == 'plan']
        plans = Plan.objects.filter(id__in=plan_ids)
        return plans

def get_services(self):
        services = []
        for key, item in self.cart.items():
            if item['type'] == 'service':
                service_id = int(key.split('-')[1])
                service = get_object_or_404(CatalogService, id=service_id)
                item['name'] = service.name
                item['prix'] = item['prix']
                if 'image_id' in item and item['image_id']:
                    try:
                        image = ServiceImage.objects.get(id=item['image_id'])
                        item['image_url'] = image.image.url
                    except ServiceImage.DoesNotExist:
                        item['image_url'] = None
                services.append(item)
        return services

def delete(self, item_id, item_type):
        keys_to_delete = [key for key in self.cart if key.startswith(f'{item_type}-{item_id}')]
        for key in keys_to_delete:
            del self.cart[key]
        self.session.modified = True

def clear(self):
        self.cart.clear()
        self.session.modified = True

def cart_total(self):
        total = sum(float(item['prix']) for item in self.cart.values())
        return total

# Ajouter un plan au panier
@login_required
def cart_add_plan(request, plan_id):
    cart = Cart(request)
    plan = get_object_or_404(Plan, id=plan_id)
    cart.add_plan(plan=plan)
    messages.success(request, "Plan ajouté au panier avec succès.")
    return redirect('cart:cart_summary')

# Ajouter un service au panier avec une image spécifique si sélectionnée

@login_required
def cart_add_service(request, service_id):
    image_id = request.GET.get('image_id')  # ID de l'image sélectionnée
    quantity = int(request.GET.get('quantity', 1))  # Quantité par défaut : 1
    cart = Cart(request)
    service = get_object_or_404(CatalogService, id=service_id)

    # Ajout au panier
    cart.add_service(service=service, image_id=image_id, quantity=quantity)
    
    # Vérifie si AJAX est utilisé
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': "Service ajouté au panier avec succès.",
            'cart_count': len(cart)
        })

    messages.success(request, "Service ajouté au panier avec succès.")
    return redirect('cart:cart_summary')





# Supprimer un élément du panier
def cart_delete(request, item_type, item_id):
    cart = Cart(request)
    cart.delete(item_id=item_id, item_type=item_type)
    messages.success(request, f"{item_type.capitalize()} supprimé du panier.")
    return redirect('cart:cart_summary')

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
    cart_plans = cart.get_plans()  
    cart_services = cart.get_services() 

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

from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from datetime import datetime

from django.utils.timezone import now
from datetime import datetime

@login_required
def payment_success(request):
    cart = Cart(request)
    purchased_plans = cart.get_plans()
    purchased_services = cart.get_services()
    cart.clear()

    plan = purchased_plans[0] if purchased_plans else None

    # Enregistrement d'une souscription si un plan a été acheté
    if plan:
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            payment_status='paid',
        )

        # Mettre à jour l'utilisateur en premium
        request.user.is_premium = True
        request.user.save()

        # Enregistrer l'achat du plan dans l'historique
        PurchaseHistory.objects.create(
            user=request.user,
            item_type='plan',
            plan=plan,
            price=plan.price,
            purchase_date=now()
        )
        print(f"PurchaseHistory créé pour le plan : {plan.name}")

    # Enregistrement des achats de services
    for service_item in purchased_services:
        try:
            service_id = service_item.get("service_id")
            image_id = service_item.get("image_id")
            
            catalog_service = CatalogService.objects.get(id=service_id)
            service_image = ServiceImage.objects.filter(id=image_id).first()
            price = service_image.price if service_image else catalog_service.price

            # Ajouter au PurchaseHistory
            PurchaseHistory.objects.create(
                user=request.user,
                item_type='service',
                price=price,
                purchase_date=datetime.now(),
                catalog_service=catalog_service
            )
            print(f"Service ajouté à PurchaseHistory : {catalog_service.name}")
        except CatalogService.DoesNotExist:
            print(f"[ERROR] Service introuvable avec ID {service_id}")
        except Exception as e:
            print(f"Erreur lors de l'enregistrement du service : {e}")

    # Envoi de confirmation
    try:
        admin_user = User.objects.filter(role='admin').first()
        if admin_user:
            if purchased_plans:
                Message.objects.create(
                    sender=admin_user,
                    recipient=request.user,
                    subject="Confirmation de souscription",
                    body="Merci pour votre souscription. Profitez de vos avantages premium avec BE-FIT."
                )
            if purchased_services:
                Message.objects.create(
                    sender=admin_user,
                    recipient=request.user,
                    subject="Confirmation d'achat de service",
                    body="Merci pour votre achat. Consultez votre messagerie pour les détails de livraison."
                )
    except Exception as e:
        print(f"Erreur lors de l'envoi du message de confirmation : {e}")

    return render(request, 'payment_success.html', {'plan': plan, 'services': purchased_services})








# Pages d'annulation et d'échec de paiement
def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')

def payment_failed(request):
    return render(request, 'payment_failed.html')
