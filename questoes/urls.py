from django.urls import path
from . import views

urlpatterns = [
    path("criar/", views.CriarQuestaoView.as_view(), name="criar-questao"),
    path("listar/", views.ListarQuestoesView.as_view(), name="listar-questoes"),
    path("<int:pk>/", views.DetalheQuestaoView.as_view(), name="detalhe-questao"),
    path("<int:pk>/atualizar/", views.AtualizarQuestaoView.as_view(), name="atualizar-questao"),
    path("<int:pk>/deletar/", views.DeletarQuestaoView.as_view(), name="deletar-questao"),
]
