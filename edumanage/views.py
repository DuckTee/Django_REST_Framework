from rest_framework import viewsets, generics, permissions
from users.permissions import IsOwner, IsModerator
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов"""
    serializer_class = CourseSerializer

    def get_permissions(self):
        """
        Разграничение прав по действиям.
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]

        elif self.action in ['update', 'partial_update']:
            # Редактировать: владелец ИЛИ модератор
            return [permissions.IsAuthenticated(), IsOwner | IsModerator]

        elif self.action == 'create':
            # Создавать: только админы
            return [permissions.IsAdminUser()]

        elif self.action == 'destroy':
            # Удалять: только владелец
            return [permissions.IsAuthenticated(), IsOwner]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Модераторы видят все курсы, остальные — только свои.
        """
        if not self.request.user.is_authenticated:
            return Course.objects.none()
        if self.request.user.is_moderator():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    """Generic-класс для списка и создания уроков"""
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Lesson.objects.none()
        if self.request.user.is_moderator():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Generic-класс для детального просмотра, редактирования и удаления уроков"""
    serializer_class = LessonSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated(), IsOwner | IsModerator]
        elif self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsOwner]
        return [permissions.IsAuthenticated()]  # fallback

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Lesson.objects.none()
        if self.request.user.is_moderator():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)
