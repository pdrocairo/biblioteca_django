from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status

from biblioteca.models import Emprestimo, Exemplar, Livro, Usuario


class ErroDeNegocio(Exception):
    def __init__(self, mensagem, status_code=status.HTTP_409_CONFLICT):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_code = status_code


@transaction.atomic
def registrar_emprestimo(usuario_id, livro_id):
    # Trava o usuario para que dois pedidos simultaneos nao furem a regra
    # de um emprestimo ativo por vez.
    usuario = get_object_or_404(Usuario.objects.select_for_update(), pk=usuario_id)
    livro = get_object_or_404(Livro, pk=livro_id)

    if Emprestimo.objects.filter(usuario=usuario, ativo=True).exists():
        raise ErroDeNegocio('Usuario ja tem emprestimo ativo')

    # skip_locked: pedidos simultaneos pelo mesmo livro pegam exemplares diferentes.
    exemplar = (
        Exemplar.objects.select_for_update(skip_locked=True)
        .filter(livro=livro, disponivel=True)
        .first()
    )
    if exemplar is None:
        raise ErroDeNegocio('Nao existe exemplares deste livro disponivel no momento')

    exemplar.disponivel = False
    exemplar.save(update_fields=['disponivel'])

    return Emprestimo.objects.create(
        exemplar=exemplar,
        usuario=usuario,
        data_retirada=timezone.localdate(),
    )


@transaction.atomic
def registrar_devolucao(usuario_id, exemplar_id):
    exemplar = get_object_or_404(Exemplar.objects.select_for_update(), pk=exemplar_id)

    emprestimo = (
        Emprestimo.objects.select_for_update()
        .filter(usuario_id=usuario_id, exemplar=exemplar, ativo=True)
        .first()
    )
    if emprestimo is None:
        raise ErroDeNegocio('Nao existe emprestimo ativo deste exemplar para este usuario')

    emprestimo.ativo = False
    emprestimo.data_devolucao = timezone.localdate()
    emprestimo.save(update_fields=['ativo', 'data_devolucao'])

    exemplar.disponivel = True
    exemplar.save(update_fields=['disponivel'])

    return emprestimo
