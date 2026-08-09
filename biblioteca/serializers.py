from rest_framework import serializers
from biblioteca.models import Autor, Categoria, Livro, Exemplar, Emprestimo, Usuario, Editora

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class LivroSerializer(serializers.ModelSerializer):
    autor_nome = serializers.StringRelatedField(source='id_autor', read_only=True)
    categoria_nome = serializers.StringRelatedField(source='id_categoria', read_only=True)
    editora_nome = serializers.StringRelatedField(source='id_editora', read_only=True)

    class Meta:
        model = Livro
        fields = '__all__'

class ExemplarSerializer(serializers.ModelSerializer):
    livro_nome = serializers.StringRelatedField(source='id_livro', read_only=True)

    class Meta:
        model = Exemplar
        fields = '__all__'


class EmprestimoSerializer(serializers.ModelSerializer):
    exemplar_nome = serializers.StringRelatedField(source='id_exemplar', read_only=True)
    usuario_nome = serializers.StringRelatedField(source='id_usuario', read_only=True)

    class Meta:
        model = Emprestimo
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'


class EditoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editora
        fields = '__all__'
