from gym_app.models import Plan, CatalogService, ServiceImage
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add_plan(self, plan):
        # Récupérer l'image du plan et l'ajouter aux données du panier
        plan_id = f'plan-{plan.id}'
        if plan_id not in self.cart:
            plan_image_url = plan.image.url if plan.image else None  # Assure que l'image existe avant d'accéder à l'URL
            self.cart[plan_id] = {
                'prix': str(plan.price),
                'type': 'plan',
                'duration': plan.duration,
                'image_url': plan_image_url  # Ajoute l'URL de l'image au panier
            }
        print(f"[DEBUG] Plan ajouté : {plan_id} avec image : {plan_image_url}")  # Point de débogage
        self.session.modified = True

    def add_service(self, service, image_id=None):
        service_key = f'service-{service.id}-image-{image_id}' if image_id else f'service-{service.id}'
        if service_key not in self.cart:
            try:
                image_price = service.price  # Prix général de CatalogService
                self.cart[service_key] = {'prix': str(image_price), 'type': 'service', 'image_id': image_id}
                print(f"[DEBUG] Service ajouté : {service_key}")  # Point de débogage
            except CatalogService.DoesNotExist:
                print(f"[ERROR] Service avec ID {service.id} introuvable.")
                return
        self.session.modified = True

    def __len__(self):
        return len(self.cart)

    def get_plans(self):
        plan_ids = [int(key.split('-')[1]) for key in self.cart if self.cart[key]['type'] == 'plan']
        plans = Plan.objects.filter(id__in=plan_ids)
        for plan in plans:
            plan_key = f'plan-{plan.id}'
            self.cart[plan_key]['duration'] = plan.duration
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
                else:
                    item['image_url'] = None
                services.append(item)
        return services

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


# Vue pour ajouter un service au panier
def cart_add_service(request, service_id):
    image_id = request.GET.get('image_id')  # Récupère l'image ID depuis la requête GET
    cart = Cart(request)
    service = get_object_or_404(CatalogService, id=service_id)

    # Ajoute le service au panier
    cart.add_service(service=service, image_id=image_id)
    
    # Vérifie si c'est une requête AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': "Service ajouté au panier avec succès.",
            'cart_count': len(cart)  # Ajoute le nombre d'éléments dans le panier
        })
    
    # Si ce n'est pas une requête AJAX, redirige vers le résumé du panier
    messages.success(request, "Service ajouté au panier avec succès.")
    return redirect('cart:cart_summary')
