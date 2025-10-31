from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from . import views

router = DefaultRouter()
router.register(r"payments", views.PaymentViewSet, basename="payment")
router.register(r"users", views.UserAdminViewSet, basename="user")  # CRUD для админа

urlpatterns = [
    # 1. Основные API-эндпоинты (через роутер)
    path("", include(router.urls)),
    # 2. Регистрация и профиль пользователя
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.UserProfileView.as_view(), name="user-profile"),
    # 3. JWT-эндпоинты (встроенные из simplejwt)
    path(
        "api/token/",
        jwt_views.TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
