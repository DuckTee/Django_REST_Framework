from rest_framework import permissions



class IsModerator(permissions.BasePermission):
    """Разрешает доступ только пользователям с ролью 'moderator'"""
    message = "Доступ разрешён только модераторам."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'is_moderator')
            and request.user.is_moderator()
        )



class IsOwner(permissions.BasePermission):
    """Разрешает доступ только владельцу объекта"""
    message = "Вы не являетесь владельцем этого объекта."

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
