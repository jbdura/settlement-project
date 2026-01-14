# payments/services.py

from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Q
from .models import Merchant, Payment, Fee, Settlement, PaymentStatus


class SettlementService:
    """Core business logic for processing settlements"""

    @staticmethod
    def calculate_fee(amount: Decimal, percentage: Decimal) -> Decimal:
        """Calculate fee based on amount and percentage"""
        return (amount * percentage) / Decimal('100')

    @staticmethod
    @transaction.atomic
    def process_settlement_for_merchant(merchant_id: int) -> Settlement:
        """
        Process settlement for a specific merchant

        Steps:
        1. Fetch all SUCCESS payments for merchant
        2. Calculate gross amount
        3. Apply fees based on payment method
        4. Calculate net amount
        5. Create settlement record
        """
        merchant = Merchant.objects.get(id=merchant_id)

        # Get all successful payments that haven't been settled
        successful_payments = Payment.objects.filter(
            merchant=merchant,
            status=PaymentStatus.SUCCESS
        )

        if not successful_payments.exists():
            raise ValueError(f"No successful payments found for merchant {merchant.name}")

        gross_amount = Decimal('0')
        total_fee = Decimal('0')

        # Calculate amounts per payment method
        for payment in successful_payments:
            gross_amount += payment.amount

            # Get fee for this payment method
            try:
                fee = Fee.objects.get(method=payment.method)
                payment_fee = SettlementService.calculate_fee(
                    payment.amount,
                    fee.percentage
                )
                total_fee += payment_fee
            except Fee.DoesNotExist:
                # If no fee defined, assume 0%
                pass

        net_amount = gross_amount - total_fee

        # Create settlement record
        settlement = Settlement.objects.create(
            merchant=merchant,
            gross_amount=gross_amount,
            fee_amount=total_fee,
            net_amount=net_amount
        )

        return settlement

    @staticmethod
    @transaction.atomic
    def process_all_settlements():
        """Process settlements for all merchants with successful payments"""
        merchants_with_payments = Merchant.objects.filter(
            payments__status=PaymentStatus.SUCCESS
        ).distinct()

        settlements = []
        errors = []

        for merchant in merchants_with_payments:
            try:
                settlement = SettlementService.process_settlement_for_merchant(
                    merchant.id
                )
                settlements.append(settlement)
            except Exception as e:
                errors.append({
                    'merchant_id': merchant.id,
                    'merchant_name': merchant.name,
                    'error': str(e)
                })

        return {
            'settlements': settlements,
            'errors': errors,
            'total_processed': len(settlements),
            'total_errors': len(errors)
        }

    @staticmethod
    def get_merchant_summary(merchant_id: int):
        """Get payment summary for a merchant"""
        merchant = Merchant.objects.get(id=merchant_id)

        payments = Payment.objects.filter(merchant=merchant)

        summary = {
            'merchant': merchant.name,
            'total_payments': payments.count(),
            'successful_payments': payments.filter(
                status=PaymentStatus.SUCCESS
            ).count(),
            'failed_payments': payments.filter(
                status=PaymentStatus.FAILED
            ).count(),
            'pending_payments': payments.filter(
                status=PaymentStatus.PENDING
            ).count(),
            'total_amount': payments.filter(
                status=PaymentStatus.SUCCESS
            ).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0'),
            'settlements': Settlement.objects.filter(
                merchant=merchant
            ).order_by('-created_at')[:5]
        }

        return summary
