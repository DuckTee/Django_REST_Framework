from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsOwner, IsModerator
from .models import Course, Lesson, Subscription
from .paginators import StandardResultsSetPagination
from .serializers import CourseSerializer, LessonSerializer
from tasks import send_course_update_email


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов"""

    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsOwner() | IsModerator()]
        elif self.action == "create":
            return [permissions.IsAdminUser()]
        elif self.action == "destroy":
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Course.objects.none()
        if self.request.user.is_moderator():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Переопределяем update для отправки рассылки после сохранения
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Сохраняем изменения
        self.perform_update(serializer)

        # Запускаем асинхронную рассылку подписчикам
        send_course_update_email.delay(instance.id)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Аналогично update, но для частичного обновления
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class LessonListCreateView(generics.ListCreateAPIView):
    """Generic-класс для списка и создания уроков"""

    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        elif self.request.method == "POST":
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
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [permissions.IsAuthenticated(), IsOwner | IsModerator]
        elif self.request.method == "DELETE":
            return [permissions.IsAuthenticated(), IsOwner]
        return [permissions.IsAuthenticated()]  # fallback

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Lesson.objects.none()
        if self.request.user.is_moderator():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class ManageSubscriptionView(APIView):
    """Generic-класс для подписки"""

    @swagger_auto_schema(
        operation_summary="Управление подпиской на курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['course_id'],
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Response('OK', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            404: openapi.Response('Not Found', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    def post(self, request, format=None):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"error": "Требуется авторизация"}, status=status.HTTP_401_UNAUTHORIZED
            )

        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"error": "Не указан course_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем курс или 404
        course = get_object_or_404(Course, id=course_id)

        # Ищем существующую подписку
        subscription = Subscription.objects.filter(user=user, course=course).first()

        if subscription:
            # Подписка есть → удаляем
            subscription.delete()
            message = "Подписка удалена"
        else:
            # Подписки нет → создаём
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"

        return Response({"message": message})
