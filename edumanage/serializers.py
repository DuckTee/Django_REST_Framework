from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import LinkValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока"""

    video_url = serializers.URLField(
        required=False,
        allow_blank=True,
        validators=[LinkValidator()],  # ← валидатор для video_url
    )

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса"""

    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        """Количество уроков в курсе"""

        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "preview",
            "lessons",
            "lessons_count",
            "is_subscribed",
        ]
