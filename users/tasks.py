from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

@shared_task
def deactivate_inactive_users():
    """
    Деактивирует пользователей, не заходивших более 30 дней.
    """
    # Вычисляем дату: сейчас минус 30 дней
    cutoff_date = timezone.now() - timedelta(days=30)

    # Находим пользователей, у которых last_login старше cutoff_date И is_active=True
    inactive_users = User.objects.filter(
        last_login__lt=cutoff_date,
        is_active=True
    )

    # Деактивируем их
    inactive_users.update(is_active=False)

    # Для логирования (можно убрать или отправить в лог-файл)
    print(f"Деактивировано пользователей: {inactive_users.count()}")
    return inactive_users.count()