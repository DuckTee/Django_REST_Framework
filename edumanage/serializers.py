from rest_framework import serializers
from .models import Course, Lesson
from .validators import LinkValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока"""

    video_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [LinkValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса"""

    lessons = LessonSerializer(many=True, read_only=True)

    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "preview", "lessons", "lessons_count"]

    def get_lessons_count(self, obj):
        """Получение количества уроков"""
        return obj.lesson_set.count()
