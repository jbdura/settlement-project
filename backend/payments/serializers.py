# payments/serializers.py

from rest_framework import serializers
from .models import Merchant, Payment, Fee, Settlement


class MerchantSerializer(serializers.ModelSerializer):
    total_payments = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Merchant
        fields = ['id', 'name', 'settlement_account', 'created_at',
                  'total_payments', 'total_revenue']
        read_only_fields = ['created_at']


class PaymentSerializer(serializers.ModelSerializer):
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'merchant', 'merchant_name', 'amount', 'method',
                  'status', 'created_at']
        read_only_fields = ['created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating payments"""

    class Meta:
        model = Payment
        fields = ['merchant', 'amount', 'method']


class PaymentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=['SUCCESS', 'FAILED', 'PENDING']
    )


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = ['method', 'percentage']

    def validate_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Percentage must be between 0 and 100"
            )
        return value


class SettlementSerializer(serializers.ModelSerializer):
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)

    class Meta:
        model = Settlement
        fields = ['id', 'merchant', 'merchant_name', 'gross_amount',
                  'fee_amount', 'net_amount', 'created_at']
        read_only_fields = ['gross_amount', 'fee_amount', 'net_amount',
                            'created_at']


class SettlementDetailSerializer(serializers.ModelSerializer):
    merchant = MerchantSerializer(read_only=True)
    fee_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Settlement
        fields = ['id', 'merchant', 'gross_amount', 'fee_amount',
                  'net_amount', 'fee_percentage', 'created_at']

    def get_fee_percentage(self, obj):
        if obj.gross_amount > 0:
            return round((obj.fee_amount / obj.gross_amount) * 100, 2)
        return 0


class MerchantSummarySerializer(serializers.Serializer):
    merchant = serializers.CharField()
    total_payments = serializers.IntegerField()
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    settlements = SettlementSerializer(many=True)
