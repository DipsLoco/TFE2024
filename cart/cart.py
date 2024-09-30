from gym_app.models import Plan


class Cart:
    def __init__(self, request):
        self.session = request.session
        # Vérifier si le panier existe dans la session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, plan):
        """
        Ajoute un plan au panier. Si le plan est déjà dans le panier, il ne fait rien.
        """
        plan_id = str(plan.id)  # Utiliser l'ID du plan pour la clé du panier
        if plan_id in self.cart:
            # Option pour implémenter l'ajout de quantité si nécessaire
            pass
        else:
            # Sauvegarde le prix sous forme de chaîne pour éviter les erreurs de sérialisation
            self.cart[plan_id] = {'prix': str(plan.price)}
        self.session.modified = True  # Indique que la session a été modifiée

    def __len__(self):
        """
        Retourne le nombre de plans dans le panier.
        """
        return len(self.cart)

    def get_prods(self):
        """
        Récupère les objets Plan correspondant aux plans dans le panier.
        """
        plan_ids = self.cart.keys()  # Récupère les IDs des plans dans le panier
        # Filtre les objets Plan avec ces IDs
        plans = Plan.objects.filter(id__in=plan_ids)
        return plans

    def delete(self, plan_id):
        """
        Supprime un plan du panier par son ID.
        """
        plan_id = str(
            plan_id)  # Convertir l'ID en chaîne car les clés du panier sont des chaînes
        if plan_id in self.cart:
            del self.cart[plan_id]
            self.session.modified = True  # Indiquer que la session a été modifiée

    def clear(self):
        """
        Vide complètement le panier.
        """
        self.cart.clear()  # Efface toutes les entrées du panier
        self.session.modified = True  # Indiquer que la session a été modifiée

    def cart_total(self):
        plan_ids = self.cart.keys()
        plans = Plan.objects.filter(id__in=plan_ids)
        quantities = self.cart
        totaltvac = 0
        for key, value in quantities.items():
            key = int(key)
            for plan in plans:
                if plan.id == key:
                    totaltvac += plan.price

        return totaltvac, plans
