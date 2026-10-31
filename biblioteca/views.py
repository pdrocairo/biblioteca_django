from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from biblioteca import services
from biblioteca.models import Autor, Categoria, Livro, Editora, Usuario, Exemplar, Emprestimo
from biblioteca.permissions import IsBibliotecario
from biblioteca.services import ErroDeNegocio
from biblioteca.serializers import (
    AutorSerializer, CategoriaSerializer, LivroSerializer, EditoraSerializer, UsuarioSerializer, ExemplarSerializer, EmprestimoSerializer,
    RegistrarEmprestimoSerializer, RegistrarDevolucaoSerializer,
)

def _primeiro_erro(erros):
    campo, mensagens = next(iter(erros.items()))
    return f"{campo}: {mensagens[0]}"


class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

class EditoraViewSet(viewsets.ModelViewSet):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, IsBibliotecario]

class ExemplarViewSet(viewsets.ModelViewSet):
    queryset = Exemplar.objects.all()
    serializer_class = ExemplarSerializer

class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer


    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated, IsBibliotecario])
    def registrar_emprestimo(self, request):
        entrada = RegistrarEmprestimoSerializer(data=request.data)
        if not entrada.is_valid():
            return Response({"erro": _primeiro_erro(entrada.errors)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            services.registrar_emprestimo(
                usuario_id=entrada.validated_data['id_usuario'],
                livro_id=entrada.validated_data['id_livro'],
            )
        except ErroDeNegocio as erro:
            return Response({"erro": erro.mensagem}, status=erro.status_code)

        return Response({"sucesso": "Emprestimo criado com sucesso!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['PATCH'], permission_classes=[IsAuthenticated, IsBibliotecario])
    def registrar_devolucoes(self, request):
        entrada = RegistrarDevolucaoSerializer(data=request.data)
        if not entrada.is_valid():
            return Response({"erro": _primeiro_erro(entrada.errors)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            services.registrar_devolucao(
                usuario_id=entrada.validated_data['id_usuario'],
                exemplar_id=entrada.validated_data['id_exemplar'],
            )
        except ErroDeNegocio as erro:
            return Response({"erro": erro.mensagem}, status=erro.status_code)

        return Response({"sucesso": "Devolucao feita com sucesso"}, status=status.HTTP_200_OK)
