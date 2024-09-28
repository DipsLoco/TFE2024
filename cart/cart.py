class Cart():
    def __init__(self, request):
        self.session = request.session
        # Vérifier si le panier existe dans la session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, plan):
        plan_id = str(plan.id)  # Utiliser plan.id pour obtenir l'ID
        if plan_id in self.cart:
            # Vous pouvez implémenter la logique d'ajout de quantités ici si nécessaire
            pass
        else:
            self.cart[plan_id] = {'prix': str(plan.price)}
        self.session.modified = True  # Marquer la session comme modifiée pour sauvegarder les changements

    def __len__(self):
        return len (self.cart)

