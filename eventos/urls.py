from django.urls import path
from .views import (
    CriarEventoView,
    ListarEventosView,
    DetalheEventoView,
    AtualizarEventoView,
    DeletarEventoView,
    EntrarNoEventoView,

    ListarQuestoesDoEventoView,
    CriarQuestaoNoEventoView,
    DetalharQuestaoView,
    AtualizarQuestaoView,
    DeletarQuestaoView,

    SubmeterSolucaoView,
    MinhasSubmissoesView,
    DetalheSubmissaoView,

    RankingEventoView,
)

urlpatterns = [
    path("eventos/", ListarEventosView.as_view(), name="listar-eventos"),
    path("eventos/criar/", CriarEventoView.as_view(), name="criar-evento"),
    path("eventos/<int:pk>/", DetalheEventoView.as_view(), name="detalhar-evento"),
    path("eventos/<int:pk>/atualizar/", AtualizarEventoView.as_view(), name="atualizar-evento"),
    path("eventos/<int:pk>/deletar/", DeletarEventoView.as_view(), name="deletar-evento"),
    path("eventos/entrar/", EntrarNoEventoView.as_view(), name="entrar-evento"),
    
    path("eventos/<int:evento_pk>/questoes/",ListarQuestoesDoEventoView.as_view(),name="listar-questoes-evento"),
    path("eventos/<int:evento_pk>/questoes/criar/", CriarQuestaoNoEventoView.as_view(), name="criar-questao-evento"),
    path("eventos/<int:evento_pk>/questoes/<int:pk>/", DetalharQuestaoView.as_view(), name="detalhar-questao"),
    path("eventos/<int:evento_pk>/questoes/<int:pk>/atualizar/", AtualizarQuestaoView.as_view(), name="atualizar-questao"),
    path("eventos/<int:evento_pk>/questoes/<int:pk>/deletar/", DeletarQuestaoView.as_view(), name="deletar-questao"),
    path("eventos/<int:evento_pk>/questoes/<int:questao_pk>/submeter/", SubmeterSolucaoView.as_view(), name="submeter-solucao"),
    path("submissoes/meus/", MinhasSubmissoesView.as_view(), name="minhas-submissoes"),
    path("submissoes/<int:pk>/", DetalheSubmissaoView.as_view(), name="detalhar-submissao"),
    path("eventos/<int:evento_pk>/ranking/", RankingEventoView.as_view(), name="ranking-evento"),
]
