from rest_framework.permissions import BasePermission

from biblioteca.models import Usuario


class IsBibliotecario(BasePermission):
    message = 'Apenas bibliotecários podem realizar esta operação.'

    def has_permission(self, request, view):
        usuario = getattr(request.user, 'usuario', None)
        return usuario is not None and usuario.perfil == Usuario.PERFIL_BIBLIOTECARIO
