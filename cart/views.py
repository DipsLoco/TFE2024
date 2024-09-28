from django.shortcuts import render, get_object_or_404
from .cart import Cart
from gym_app.models import Plan
from django.http import JsonResponse
from django.contrib import messages  # Importer correctement les messages


def cart_summary(request):
    return render(request, 'cart_summary.html', {})


def cart_add(request):
    cart = Cart(request)
    
    if request.POST.get('action') == 'post':
        plan_id = int(request.POST.get('plan_id'))
        plan = get_object_or_404(Plan, id=plan_id)  # Plan avec majuscule

        cart.add(plan=plan)

        cart_quantity = len(cart.cart)  # Corriger la méthode pour obtenir la taille du panier
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, "Abonnement ajouté à votre sélection...")
        return response


def cart_delete(request):
    pass

def cart_update(request):
    pass
