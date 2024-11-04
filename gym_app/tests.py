from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Plan, CatalogService, PurchaseHistory

User = get_user_model()

class PurchaseHistoryTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.plan = Plan.objects.create(name='Plan Test', price=100, duration=30)
        self.service = CatalogService.objects.create(name='Service Test', price=50)

    def test_create_purchase_history_plan(self):
        PurchaseHistory.objects.create(user=self.user, item_type='plan', price=self.plan.price, plan=self.plan)
        purchase = PurchaseHistory.objects.get(user=self.user, item_type='plan')
        self.assertEqual(purchase.get_item_name(), self.plan.name)
        self.assertEqual(purchase.get_duration(), self.plan.duration)

    def test_create_purchase_history_service(self):
        PurchaseHistory.objects.create(user=self.user, item_type='service', price=self.service.price, catalog_service=self.service)
        purchase = PurchaseHistory.objects.get(user=self.user, item_type='service')
        self.assertEqual(purchase.get_item_name(), self.service.name)

