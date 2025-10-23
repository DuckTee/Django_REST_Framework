from django.db import models


# --- Модель курса ---
class Course(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Название курса",
        help_text="Укажите название курса"
    )
    preview = models.ImageField(
        upload_to='edumanage/courses',
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Добавьте описание"
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


# --- Модель урока ---
class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        related_name='lessons',
        on_delete=models.CASCADE,
        verbose_name="Курс",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название урока",
        help_text="Укажите название урока"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Добавьте описание"
    )
    preview = models.ImageField(
        upload_to='edumanage/lessons',
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение"
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Добавьте ссылку"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f"{self.title} | {self.course.title}"
