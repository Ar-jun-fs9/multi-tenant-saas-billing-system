from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=100)
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')


class Plan(models.Model):
    name = models.CharField(max_length=50)
    stripe_price_id = models.CharField(max_length=100)  # Stripe plan ID
    price = models.FloatField()
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.organization.name} - {self.plan.name}"
