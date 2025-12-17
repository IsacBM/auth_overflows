from django.urls import path
from .views import (
    CriarEventoView,
    ListarEventosView,
    DetalheEventoView,
    AtualizarEventoView,
    DeletarEventoView,
    MeusEventosView,
    EntrarNoEventoView,

    ListarQuestoesDoEventoView,
    CriarQuestaoNoEventoView,

    RankingEventoView,
)

urlpatterns = [
    path("/lista/", ListarEventosView.as_view(), name="listar-eventos"),
    path("/criar/", CriarEventoView.as_view(), name="criar-evento"),
    path("/<int:pk>/", DetalheEventoView.as_view(), name="detalhar-evento"),
    path("/<int:pk>/atualizar/", AtualizarEventoView.as_view(), name="atualizar-evento"),
    path("/<int:pk>/deletar/", DeletarEventoView.as_view(), name="deletar-evento"),
    path("/entrar/", EntrarNoEventoView.as_view(), name="entrar-evento"),
    path("/meus/", MeusEventosView.as_view(), name="meus-eventos"),
    
    path("/<int:evento_pk>/questoes/",ListarQuestoesDoEventoView.as_view(),name="listar-questoes-evento"),
    path("/<int:evento_pk>/questoes/criar/", CriarQuestaoNoEventoView.as_view(), name="criar-questao-evento"),
    path("/<int:evento_pk>/ranking/", RankingEventoView.as_view(), name="ranking-evento"),
]
