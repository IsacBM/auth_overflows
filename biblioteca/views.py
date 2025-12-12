from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema

from .models import Linguagem, TopicoLinguagem
from .serializers import (
    LanguageSerializer,
    LanguageTopicListSerializer,
    LanguageTopicDetailSerializer,
)

@extend_schema(tags=["Biblioteca"])
class ListarLinguagensView(generics.ListAPIView):
    queryset = Linguagem.objects.all().order_by("ordem")
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Listar linguagens suportadas",
        description="Retorna a lista de linguagens suportadas pela plataforma.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(tags=["Biblioteca"])
class ListarTopicosLinguagemView(generics.ListAPIView):
    serializer_class = LanguageTopicListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        linguagem_slug = self.kwargs["texto_linguagem"]
        return TopicoLinguagem.objects.filter(
            language__slug=linguagem_slug
        ).order_by("ordem")

    @extend_schema(
        summary="Listar tópicos de uma linguagem",
        description="Retorna os tópicos (introdução, variáveis, etc.) de uma linguagem.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(tags=["Biblioteca"])
class DetalheTopicoLinguagemView(generics.RetrieveAPIView):
    serializer_class = LanguageTopicDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "topico"

    def get_queryset(self):
        linguagem_slug = self.kwargs["texto_linguagem"]
        return TopicoLinguagem.objects.filter(language__slug=linguagem_slug)

    @extend_schema(
        summary="Detalhar tópico de uma linguagem",
        description="Retorna o conteúdo completo de um tópico: código, saída esperada e explicação.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
