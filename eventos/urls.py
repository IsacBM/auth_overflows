from django.urls import path
from .views import (
    CriarEventoView,
    ListarEventosView,
    DetalheEventoView,
    AtualizarEventoView,
    DeletarEventoView,
    EntrarNoEventoView,
)

urlpatterns = [
    path("eventos/", ListarEventosView.as_view(), name="listar-eventos"),
    path("eventos/criar/", CriarEventoView.as_view(), name="criar-evento"),
    path("eventos/<int:pk>/", DetalheEventoView.as_view(), name="detalhar-evento"),
    path("eventos/<int:pk>/atualizar/", AtualizarEventoView.as_view(), name="atualizar-evento"),
    path("eventos/<int:pk>/deletar/", DeletarEventoView.as_view(), name="deletar-evento"),
    path("eventos/entrar/", EntrarNoEventoView.as_view(), name="entrar-evento"),
]
