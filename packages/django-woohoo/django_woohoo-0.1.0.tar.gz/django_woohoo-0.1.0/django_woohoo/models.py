from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class PlatformToken(models.Model):
    class NameChoices(models.TextChoices):
        AMAZON_AUTHORIZATION = "Amazon Authorization"
        AMAZON_BEARER = "Amazon Bearer"
        FLIPKART_AUTHORIZATION = "Flipkart Authorization"
        FLIPKART_BEARER = "Flipkart Bearer"

    name = models.CharField(max_length=255, choices=NameChoices.choices, unique=True)
    token = models.TextField()
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class PlatformPaymentRequestLog(models.Model):
    class PaymentProviderChoices(models.TextChoices):
        CASHFREE = "Cashfree"
        AMAZON = "Amazon"
        FLIPKART = "Flipkart"

    payment_provider = models.CharField(max_length=100, choices=PaymentProviderChoices.choices)
    url = models.TextField()
    body = models.TextField()
    response = models.TextField()
    response_status = models.PositiveIntegerField()

    requested_user_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    requested_user_object_id = models.CharField(max_length=100)
    requested_user = GenericForeignKey('requested_user_content_type', 'requested_user_object_id')
    requested_user_frozen_details = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_provider} - {self.response_status} @ {self.created_at}"
