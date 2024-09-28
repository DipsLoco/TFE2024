from .cart import Cart  # Utilisation de l'import relatif


def cart(request):
    return {'cart': Cart(request)}