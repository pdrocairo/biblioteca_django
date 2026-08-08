from django.urls import path
from biblioteca import views

urlpatterns = [
    path('autores/', views.listar_autores),
    path('', views.pagina_inicial),
    path('registrar/emprestimo/', views.registrar_emprestimo),
    path('registrar/devolucao/', views.registrar_devolucoes)
]