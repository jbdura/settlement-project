# payments/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Merchant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    settlement_account = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'merchants'
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class PaymentMethod(models.TextChoices):
    MPESA = 'MPESA', 'M-Pesa'
    CARD = 'CARD', 'Card'
    BANK = 'BANK', 'Bank Transfer'


class PaymentStatus(models.TextChoices):
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'
    PENDING = 'PENDING', 'Pending'


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    method = models.CharField(
        max_length=10,
        choices=PaymentMethod
    )
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus,
        default=PaymentStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        indexes = [
            models.Index(fields=['merchant', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.merchant.name} - {self.amount} - {self.status}"


class Fee(models.Model):
    method = models.CharField(
        max_length=10,
        choices=PaymentMethod,
        unique=True,
        primary_key=True
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Fee percentage (e.g., 2.5 for 2.5%)"
    )

    class Meta:
        db_table = 'fees'

    def __str__(self):
        return f"{self.method} - {self.percentage}%"


class Settlement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name='settlements'
    )
    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    fee_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'settlements'
        indexes = [
            models.Index(fields=['merchant', 'created_at']),
        ]

    def __str__(self):
        return f"{self.merchant.name} - {self.net_amount} ({self.created_at.date()})"