from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from edumanage.models import Course, Lesson


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя"""

    # Переопределяем поля
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

    # Поле для роли пользователя
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('moderator', 'Модератор'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name="Роль",
        help_text="Выберите роль пользователя"
    )

    # Настройки авторизации
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == 'moderator'

    def is_teacher(self):
        """Проверяет, является ли пользователь преподавателем."""
        return self.role == 'teacher'

    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == 'admin'


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
