from rest_framework import viewsets, generics, permissions

from users.permissions import IsOwner, IsModerator
from .models import Course, Lesson
from .serliazers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        """
        Разграничение прав по действиям:
        """
        if self.action in ['list', 'retrieve']:
            # Все авторизованные могут читать
            return [permissions.IsAuthenticated()]

        elif self.action in ['update', 'partial_update']:
            # Редактировать: владелец ИЛИ модератор
            return [IsOwner() | IsModerator()]

        elif self.action == 'create':
            # Создавать: только админы (можно заменить на IsTeacher)
            return [permissions.IsAdminUser()]

        elif self.action == 'destroy':
            # Удалять: только владелец
            return [IsOwner()]

        return [permissions.AllowAny()]  # fallback

    def get_queryset(self):
        """
        Модераторы видят все курсы, остальные — только свои.
        """
        if self.request.user.is_moderator():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    """Generic-класс для списка и создания уроков"""
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            # Чтение: все авторизованные
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'POST':
            # Создание: только админы
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        # Модераторы видят все уроки, остальные — только свои
        if self.request.user.is_moderator():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Generic-класс для детального просмотра, редактирования и удаления уроков"""
    serializer_class = LessonSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsOwner() | IsModerator()]
        elif self.request.method == 'DELETE':
            return [IsOwner()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.request.user.is_moderator():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)
