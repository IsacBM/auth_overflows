from django.urls import path
from .views import (
    ListarLinguagensView,
    ListarTopicosLinguagemView,
    DetalheTopicoLinguagemView,
)

urlpatterns = [
    path("linguagens/", ListarLinguagensView.as_view(), name="listar-linguagens"),
    path(
        "linguagens/<slug:language_slug>/topicos/",
        ListarTopicosLinguagemView.as_view(),
        name="listar-topicos-linguagem",
    ),
    path(
        "linguagens/<slug:language_slug>/topicos/<slug:slug>/",
        DetalheTopicoLinguagemView.as_view(),
        name="detalhar-topico-linguagem",
    ),
]
