from rest_framework.routers import DefaultRouter
from biblioteca.views import (
    AutorViewSet, CategoriaViewSet, EditoraViewSet,
    LivroViewSet, ExemplarViewSet, UsuarioViewSet, EmprestimoViewSet
)

router = DefaultRouter()

router.register('autores', AutorViewSet)
router.register('categorias', CategoriaViewSet)
router.register('editoras', EditoraViewSet)
router.register('livros', LivroViewSet)
router.register('exemplares', ExemplarViewSet)
router.register('usuarios', UsuarioViewSet)
router.register('emprestimos', EmprestimoViewSet)

urlpatterns = router.urls