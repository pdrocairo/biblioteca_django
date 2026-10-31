from rest_framework.permissions import SAFE_METHODS, BasePermission

from biblioteca.models import Usuario


class IsBibliotecario(BasePermission):
    message = 'Apenas bibliotecários podem realizar esta operação.'

    def has_permission(self, request, view):
        usuario = getattr(request.user, 'usuario', None)
        return usuario is not None and usuario.perfil == Usuario.PERFIL_BIBLIOTECARIO


class IsBibliotecarioOuSomenteLeitura(IsBibliotecario):
    """Qualquer usuario autenticado le; so o bibliotecario escreve."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)
