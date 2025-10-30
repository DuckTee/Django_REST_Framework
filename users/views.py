from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    ''' ViewSet для работы с платежами '''

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = {
        "payment_date": ["gte", "lte"],  # фильтрация по дате
        "paid_course": ["exact"],  # фильтрация по курсу
        "paid_lesson": ["exact"],  # фильтрация по уроку
        "payment_method": ["exact"],  # фильтрация по способу оплаты
    }

    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]  # сортировка по умолчанию
