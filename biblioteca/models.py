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
    id_exemplar = models.ForeignKey('Exemplar', on_delete=models.CASCADE)
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    data_retirada = models.DateField()  
    ativo = models.BooleanField(default=True)

    def __str__(self):
            return f"Data de Retirada:{self.data_retirada} - Ativo{self.ativo}"

class Exemplar(models.Model):
    id_livro = models.ForeignKey('Livro', on_delete=models.CASCADE)
    disponivel = models.BooleanField(default=True)
    codigo_tombo = models.CharField(max_length=10)

    def __str__(self):
         return f"Cód. Tombo {self.codigo_tombo} - Disponível {self.disponivel} - Id do Livro {self.id_livro}"

class Livro(models.Model):
    titulo = models.CharField(max_length=100)
    id_categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    id_autor = models.ForeignKey('Autor', on_delete=models.CASCADE)
    id_editora = models.ForeignKey('Editora', on_delete=models.CASCADE)

    def __str__(self):
         return f"Título {self.titulo} - ID da Categoria {self.id_categoria} - ID da Autor {self.id_autor} - ID da Editora {self.id_editora}"

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    senha = models.CharField(max_length=128)
    perfil = models.CharField(max_length=20)

    def __str__(self):
         return f"Nome {self.nome} - Email {self.email} - Perfil {self.perfil}"