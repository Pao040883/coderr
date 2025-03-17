from django.db import models
from app_user_auth.models import Profile

class Order(models.Model):
    STATUS_CHOICE = [
        ('in_progress', 'In_progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    customer_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='customer_orders')
    business_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='business_orders')

    title = models.CharField(max_length=100)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='in_progress')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):       
        return f"Order {self.id} - {self.title} - {self.status}"