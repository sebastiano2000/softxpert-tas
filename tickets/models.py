from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)

class Ticket(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket {self.id} (Sold: {self.is_sold})"
