from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Только автор может редактировать или удалять.
    Чтение доступно всем.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить чтение всем
        if request.method in SAFE_METHODS:
            return True

        # Запретить изменение, если не автор
        return obj.author == request.user