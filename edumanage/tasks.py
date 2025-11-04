# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Subscription, Course

@shared_task
def send_course_update_email(course_id):
    """
    Асинхронная задача: отправляет уведомления подписчикам об обновлении курса
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return  # Курс не найден

    subscribers = Subscription.objects.filter(
        course_id=course_id
    ).select_related('user')

    if not subscribers:
        return

    subject = f'Обновление курса "{course.title}"'
    context = {'course_title': course.title, 'course_id': course.id}

    for subscription in subscribers:
        user = subscription.user
        context['user'] = user

        html_message = render_to_string('emails/course_update.html', context)
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject,
                plain_message,
                'noreply@yourdomain.com',
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Ошибка отправки письма {user.email}: {e}")
