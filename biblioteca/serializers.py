from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.db import transaction
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
    autor_nome = serializers.StringRelatedField(source='autor', read_only=True)
    categoria_nome = serializers.StringRelatedField(source='categoria', read_only=True)
    editora_nome = serializers.StringRelatedField(source='editora', read_only=True)

    class Meta:
        model = Livro
        fields = '__all__'

class ExemplarSerializer(serializers.ModelSerializer):
    livro_nome = serializers.StringRelatedField(source='livro', read_only=True)

    class Meta:
        model = Exemplar
        fields = '__all__'


class EmprestimoSerializer(serializers.ModelSerializer):
    exemplar_nome = serializers.StringRelatedField(source='exemplar', read_only=True)
    usuario_nome = serializers.StringRelatedField(source='usuario', read_only=True)

    class Meta:
        model = Emprestimo
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', max_length=150)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'perfil', 'username', 'password']

    def validate_username(self, valor):
        usuarios = User.objects.filter(username=valor)
        if self.instance:
            usuarios = usuarios.exclude(pk=self.instance.user_id)
        if usuarios.exists():
            raise serializers.ValidationError('Já existe um usuário com esse nome de login.')
        return valor

    def validate_password(self, valor):
        password_validation.validate_password(valor)
        return valor

    def validate(self, dados):
        if not self.instance and 'password' not in dados:
            raise serializers.ValidationError({'password': 'Este campo é obrigatório.'})
        return dados

    @transaction.atomic
    def create(self, dados):
        username = dados.pop('user')['username']
        password = dados.pop('password')
        user = User.objects.create_user(username=username, email=dados['email'], password=password)
        return Usuario.objects.create(user=user, **dados)

    @transaction.atomic
    def update(self, instance, dados):
        user_dados = dados.pop('user', {})
        password = dados.pop('password', None)
        if 'username' in user_dados:
            instance.user.username = user_dados['username']
        if password:
            instance.user.set_password(password)
        instance.user.email = dados.get('email', instance.email)
        instance.user.save()
        return super().update(instance, dados)


class EditoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editora
        fields = '__all__'


ID_MAXIMO = 2147483647


class RegistrarEmprestimoSerializer(serializers.Serializer):
    id_usuario = serializers.IntegerField(min_value=1, max_value=ID_MAXIMO)
    id_livro = serializers.IntegerField(min_value=1, max_value=ID_MAXIMO)


class RegistrarDevolucaoSerializer(serializers.Serializer):
    id_usuario = serializers.IntegerField(min_value=1, max_value=ID_MAXIMO)
    id_exemplar = serializers.IntegerField(min_value=1, max_value=ID_MAXIMO)
