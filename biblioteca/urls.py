from django.urls import path
from .views import (
    ListarLinguagensView,
    ListarTopicosLinguagemView,
    DetalheTopicoLinguagemView,
)

urlpatterns = [
    path("linguagens/", ListarLinguagensView.as_view(), name="listar-linguagens"),
    path(
        "linguagens/<slug:texto_linguagem>/topicos/",
        ListarTopicosLinguagemView.as_view(),
        name="listar-topicos-linguagem",
    ),
    path(
        "linguagens/<slug:texto_linguagem>/topicos/<slug:topico>/",
        DetalheTopicoLinguagemView.as_view(),
        name="detalhar-topico-linguagem",
    ),
]
