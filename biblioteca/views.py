from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date
from biblioteca.models import Autor, Categoria, Livro, Editora, Usuario, Exemplar, Emprestimo
from biblioteca.permissions import IsBibliotecario
from biblioteca.serializers import (
    AutorSerializer, CategoriaSerializer, LivroSerializer, EditoraSerializer, UsuarioSerializer, ExemplarSerializer, EmprestimoSerializer
)

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
    
        id_usuario = request.data.get("id_usuario")
        id_livro = request.data.get("id_livro")

        existe_emprestimo = Emprestimo.objects.filter(usuario_id = id_usuario, ativo=True).exists()

        if existe_emprestimo:
            return Response({"erro": "Usuario ja tem emprestimo ativo"}, status= 400)

        existe_exemplar = Exemplar.objects.filter(livro_id=id_livro, disponivel=True).first()

        if existe_exemplar:

            existe_exemplar.disponivel = False
            existe_exemplar.save()

            Emprestimo.objects.create(exemplar_id=existe_exemplar.id,
                                    usuario_id=id_usuario,
                                    data_retirada=date.today(),
                                    ativo=True
                                    )

            return Response({"sucesso": "Emprestimo criado com sucesso!"}, status=201)
        
        return Response({"erro": "Nao existe exemplares deste livro disponivel no momento"}, status=400)

    @action(detail=False, methods=['PATCH'], permission_classes=[IsAuthenticated, IsBibliotecario])
    def registrar_devolucoes(self, request):

        id_usuario = request.data.get("id_usuario")
        id_exemplar = request.data.get("id_exemplar")

        existe_exemplar = Exemplar.objects.filter(id=id_exemplar, disponivel=False).exists()

        if existe_exemplar:

            exemplar = Exemplar.objects.get(id=id_exemplar, disponivel=False)

            existe_emprestimo = Emprestimo.objects.filter(usuario_id=id_usuario, exemplar_id=id_exemplar, ativo=True).exists()

            if existe_emprestimo:

                emprestimo = Emprestimo.objects.get(usuario_id=id_usuario, exemplar_id=id_exemplar, ativo=True)

                emprestimo.ativo = False
                emprestimo.save()
                exemplar.disponivel=True
                exemplar.save()
                return Response({"sucesso": "Devolucao feita com sucesso"}, status=200)
            
            return Response({"erro": "Nao existe emprestimo realizado"}, status=400) 
                    
        return Response({"erro": "Exemplar não encontrado ou já está disponível"}, status=400) 




