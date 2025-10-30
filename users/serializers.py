from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    ''' Сериализатор для модели платежей '''

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_date",
            "paid_course",
            "paid_lesson",
            "amount",
            "payment_method",
        ]
        read_only_fields = ["id", "payment_date"]


class UserSerializer(serializers.ModelSerializer):
    ''' Сериализатор для модели пользователя '''

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "city",
            "avatar",
            "payments",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Пароль должен быть не менее 8 символов"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Повторите пароль"
    )

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password", "phone", "city"]

    def validate(self, data):
        """Валидация совпадения паролей"""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Пароли не совпадают."}
            )
        return data

    def create(self, validated_data):
        """Создание пользователя через create_user"""
        validated_data.pop("confirm_password", None)

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data.get("phone", ""),
            city=validated_data.get("city", ""),
        )
        return user

    def to_representation(self, instance):
        """Добавляем JWT-токены (access и refresh) к ответу после регистрации"""
        representation = super().to_representation(instance)

        # Генерация токенов через simplejwt
        refresh = RefreshToken.for_user(instance)
        representation["refresh"] = str(refresh)
        representation["access"] = str(refresh.access_token)

        return representation
