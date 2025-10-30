from rest_framework import viewsets, filters, permissions
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Payment, User
from .serializers import PaymentSerializer, UserRegistrationSerializer, UserSerializer


class RegisterView(CreateAPIView):
    """Регистрация нового пользователя"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Генерируем JWT
        refresh = RefreshToken.for_user(user)
        response_data = {
            **serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

        headers = self.get_success_headers(serializer.data)
        return Response(
            response_data,
            status=HTTP_201_CREATED,
            headers=headers
        )


class UserProfileView(RetrieveUpdateAPIView):
    """ ViewSet для профиля """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class UserAdminViewSet(viewsets.ModelViewSet):
    """Полный CRUD для пользователей (только IsAdminUser)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentViewSet(viewsets.ModelViewSet):
    ''' ViewSet для работы с платежами '''

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = {
        "payment_date": ["gte", "lte"],  # фильтрация по дате
        "paid_course": ["exact"],  # фильтрация по курсу
        "paid_lesson": ["exact"],  # фильтрация по уроку
        "payment_method": ["exact"],  # фильтрация по способу оплаты
    }

    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]  # сортировка по умолчанию
