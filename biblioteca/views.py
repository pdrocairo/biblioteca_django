import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from biblioteca.models import Autor, Emprestimo, Editora, Exemplar, Usuario, Livro, Categoria
from datetime import date


def pagina_inicial(request):
    return HttpResponse("Bem-Vindo ao BiblioTech!")

def listar_autores(request):
    autores = Autor.objects.all()
    texto = ", ".join([autor.nome for autor in autores])
    return HttpResponse(f"Autores: {texto}")

@csrf_exempt
def registrar_emprestimo(request):
    if request.method == "POST":
        #para buscar emprestimo
        dados = json.loads(request.body)
        id_usuario = dados.get("id_usuario")
        #para buscar exemplar
        id_livro = dados.get("id_livro")

        existe_emprestimo = Emprestimo.objects.filter(id_usuario_id = id_usuario, ativo=True).exists()

        if existe_emprestimo:
            return HttpResponse("Usuario ja tem emprestimo ativo", status= 400)

        existe_exemplar = Exemplar.objects.filter(id_livro_id=id_livro, disponivel=True).first()

        if existe_exemplar:

            existe_exemplar.disponivel = False
            existe_exemplar.save()

            Emprestimo.objects.create(id_exemplar_id=existe_exemplar.id,
                                    id_usuario_id=id_usuario,
                                    data_retirada=date.today(),
                                    ativo=True
                                    )

            return HttpResponse("Emprestimo criado com sucesso!")
        
        return HttpResponse("Nao existe exemplares deste livro disponivel no momento", status=400)
    
    return HttpResponse("Request Method nao permitido", status=405)


@csrf_exempt
def registrar_devolucoes(request):
    if request.method == "PATCH":
        dados = json.loads(request.body)
        id_usuario = dados.get("id_usuario")
        id_exemplar = dados.get("id_exemplar")

        existe_exemplar = Exemplar.objects.filter(id=id_exemplar, disponivel=False).exists()

        if existe_exemplar:

            exemplar = Exemplar.objects.get(id=id_exemplar, disponivel=False)

            existe_emprestimo = Emprestimo.objects.filter(id_usuario_id=id_usuario, id_exemplar_id=id_exemplar, ativo=True).exists()
        
            if existe_emprestimo:

                emprestimo = Emprestimo.objects.get(id_usuario_id=id_usuario, id_exemplar_id=id_exemplar, ativo=True)

                emprestimo.ativo = False
                emprestimo.save()
                exemplar.disponivel=True
                exemplar.save()
                return HttpResponse("Devolucao feita com sucesso", status=200)
            
            return HttpResponse("Nao existe emprestimo realizado", status=400) 
        
        return HttpResponse("Exemplar não encontrado ou já está disponível", status=400) 
    
    return HttpResponse("Request Method nao permitido", status=405)