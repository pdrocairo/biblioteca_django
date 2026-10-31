from django.conf import settings
from django.db import models

class Autor(models.Model):
    nome = models.CharField(max_length=100)
    nacionalidade = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class Editora(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class Emprestimo(models.Model):
    exemplar = models.ForeignKey('Exemplar', on_delete=models.PROTECT)
    usuario = models.ForeignKey('Usuario', on_delete=models.PROTECT)
    data_retirada = models.DateField()  
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Empréstimo #{self.id}"

class Exemplar(models.Model):
    livro = models.ForeignKey('Livro', on_delete=models.CASCADE)
    disponivel = models.BooleanField(default=True)
    codigo_tombo = models.CharField(max_length=10)

    def __str__(self):
        return self.codigo_tombo

class Livro(models.Model):
    titulo = models.CharField(max_length=100)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    autor = models.ForeignKey('Autor', on_delete=models.CASCADE)
    editora = models.ForeignKey('Editora', on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class Usuario(models.Model):
    PERFIL_LEITOR = 'leitor'
    PERFIL_BIBLIOTECARIO = 'bibliotecario'
    PERFIS = [
        (PERFIL_LEITOR, 'Leitor'),
        (PERFIL_BIBLIOTECARIO, 'Bibliotecário'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    perfil = models.CharField(max_length=20, choices=PERFIS, default=PERFIL_LEITOR)

    def __str__(self):
        return self.nome