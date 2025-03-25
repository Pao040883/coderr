from django.db import models
from app_user_auth.models import Profile

class Review(models.Model):
    business_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='written_reviews')
    rating = models.IntegerField(default=0)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.reviewer} for {self.business_user}"