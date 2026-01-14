# payments/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from .models import Merchant, Payment, Fee, Settlement, PaymentStatus
from .serializers import (
    MerchantSerializer, PaymentSerializer, PaymentCreateSerializer,
    PaymentStatusUpdateSerializer, FeeSerializer, SettlementSerializer,
    SettlementDetailSerializer, MerchantSummarySerializer
)
from .services import SettlementService


class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Annotate with payment stats
        return queryset.annotate(
            total_payments=Count('payments'),
            total_revenue=Sum(
                'payments__amount',
                filter=Q(payments__status=PaymentStatus.SUCCESS)
            )
        )

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get detailed summary for a merchant"""
        try:
            summary = SettlementService.get_merchant_summary(pk)
            serializer = MerchantSummarySerializer(summary)
            return Response(serializer.data)
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'Merchant not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related('merchant')
    serializer_class = PaymentSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by merchant
        merchant_id = self.request.query_params.get('merchant_id')
        if merchant_id:
            queryset = queryset.filter(merchant_id=merchant_id)

        # Filter by status
        payment_status = self.request.query_params.get('status')
        if payment_status:
            queryset = queryset.filter(status=payment_status)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update payment status"""
        payment = self.get_object()
        serializer = PaymentStatusUpdateSerializer(data=request.data)

        if serializer.is_valid():
            payment.status = serializer.validated_data['status']
            payment.save()
            return Response(PaymentSerializer(payment).data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer


class SettlementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Settlement.objects.all().select_related('merchant')
    serializer_class = SettlementSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SettlementDetailSerializer
        return SettlementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by merchant
        merchant_id = self.request.query_params.get('merchant_id')
        if merchant_id:
            queryset = queryset.filter(merchant_id=merchant_id)

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process settlements for all merchants"""
        result = SettlementService.process_all_settlements()

        return Response({
            'message': 'Settlement processing complete',
            'total_processed': result['total_processed'],
            'total_errors': result['total_errors'],
            'settlements': SettlementSerializer(
                result['settlements'],
                many=True
            ).data,
            'errors': result['errors']
        })

    @action(detail=False, methods=['post'], url_path='process/(?P<merchant_id>[^/.]+)')
    def process_merchant(self, request, merchant_id=None):
        """Process settlement for a specific merchant"""
        try:
            settlement = SettlementService.process_settlement_for_merchant(
                int(merchant_id)
            )
            return Response(
                SettlementDetailSerializer(settlement).data,
                status=status.HTTP_201_CREATED
            )
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'Merchant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
