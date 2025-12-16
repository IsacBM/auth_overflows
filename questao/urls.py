from django.urls import path
from .views import (
    ListarQuestoesPlataformaView,
    CriarQuestaoPlataformaView,
    DetalharQuestaoView,
    AtualizarQuestaoView,
    DeletarQuestaoView,

    SubmeterSolucaoView,
    MinhasSubmissoesView,
    DetalheSubmissaoView,

    CriarCasoTesteView,
    ListarCasosTesteView,
    AtualizarCasoTesteView,
    DeletarCasoTesteView,
    )

urlpatterns = [
    path("listar/", ListarQuestoesPlataformaView.as_view()),
    path("criar/", CriarQuestaoPlataformaView.as_view()),
    path("<int:pk>/", DetalharQuestaoView.as_view(), name="detalhar-questao"),
    path("<int:pk>/atualizar/", AtualizarQuestaoView.as_view(), name="atualizar-questao"),
    path("<int:pk>/deletar/", DeletarQuestaoView.as_view(), name="deletar-questao"),
    path("<int:questao_pk>/submeter/", SubmeterSolucaoView.as_view(), name="submeter-solucao"),
    path("meus/", MinhasSubmissoesView.as_view(), name="minhas-submissoes"),
    path("<int:pk>/", DetalheSubmissaoView.as_view(), name="detalhar-submissao"),
    path("<int:questao_pk>/casos-teste/", ListarCasosTesteView.as_view(), name="listar-casos-teste"),
    path("<int:questao_pk>/casos-teste/criar/", CriarCasoTesteView.as_view(), name="criar-caso-teste"),
    path("casos-teste/<int:pk>/editar/", AtualizarCasoTesteView.as_view(), name="editar-caso-teste"),
    path("casos-teste/<int:pk>/deletar/", DeletarCasoTesteView.as_view(), name="deletar-caso-teste"),
]
