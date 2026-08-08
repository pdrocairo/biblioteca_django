from django.contrib import admin

from biblioteca.models import Autor, Categoria, Usuario, Exemplar, Emprestimo, Livro, Editora

admin.site.register(Autor)
admin.site.register(Categoria)
admin.site.register(Usuario)
admin.site.register(Exemplar)
admin.site.register(Emprestimo)
admin.site.register(Livro)
admin.site.register(Editora)
