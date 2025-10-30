from django.db import models


class Course(models.Model):
    """Модель курса"""
    title = models.CharField(
        max_length=255,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    preview = models.ImageField(
        upload_to="edumanage/courses",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение",
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание", help_text="Добавьте описание"
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="Владелец",
        help_text="Кто создал курс"
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class Subscription(models.Model):
    """Модель подписки пользователя на курс"""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Пользователь",
        help_text="Пользователь, подписанный на курс"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Курс",
        help_text="Курс, на который оформлена подписка"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подписки",
        help_text="Когда была создана подписка"
    )

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['course']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"


class Lesson(models.Model):
    """Модель урока"""
    course = models.ForeignKey(
        Course,
        related_name="lessons",
        on_delete=models.CASCADE,
        verbose_name="Курс",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название урока",
        help_text="Укажите название урока",
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание", help_text="Добавьте описание"
    )
    preview = models.ImageField(
        upload_to="edumanage/lessons",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Добавьте ссылку",
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Владелец",
        help_text="Кто создал урок"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f"{self.title} | {self.course.title}"
