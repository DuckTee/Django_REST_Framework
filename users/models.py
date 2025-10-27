from django.contrib.auth.models import AbstractUser
from django.db import models

from edumanage.models import Course, Lesson


class User(AbstractUser):
    """Модель пользователя"""

    username = None

    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Введите номер телефона",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите город",
    )

    avatar = models.ImageField(
        upload_to="users/avatars",
        null=True,
        blank=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    """Модель платежа"""

    PAYMENT_METHOD_CHOICES = [("cash", "Наличные"), ("transfer", "Перевод на счет")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")

    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")

    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course_payments",
    )

    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lesson_payments",
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )

    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты"
    )

    def __str__(self):
        return f"Платеж №{self.id} от {self.payment_date} на сумму {self.amount}"
