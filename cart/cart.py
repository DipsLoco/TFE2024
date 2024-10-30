from gym_app.models import Plan, CatalogService

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add_plan(self, plan):
        plan_id = f'plan-{plan.id}'
        if plan_id not in self.cart:
            self.cart[plan_id] = {'prix': str(plan.price), 'type': 'plan'}
        self.session.modified = True

    def add_service(self, service):
        service_id = f'service-{service.id}'
        if service_id not in self.cart:
            self.cart[service_id] = {'prix': str(service.price), 'type': 'service'}
        self.session.modified = True

    def __len__(self):
        return len(self.cart)

    def get_plans(self):
        plan_ids = [int(key.split('-')[1]) for key in self.cart if self.cart[key]['type'] == 'plan']
        return Plan.objects.filter(id__in=plan_ids)

    def get_services(self):
        service_ids = [int(key.split('-')[1]) for key in self.cart if self.cart[key]['type'] == 'service']
        return CatalogService.objects.filter(id__in=service_ids)

    def delete(self, item_id):
        item_id = str(item_id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.session.modified = True

    def clear(self):
        self.cart.clear()
        self.session.modified = True

    def cart_total(self):
        total = 0
        for key, item in self.cart.items():
            total += float(item['prix'])
        return total
