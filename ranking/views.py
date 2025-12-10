from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema

from .models import PontuacaoGeral
from .serializers import RankingUsuarioSerializer

@extend_schema(
    tags=["Ranking Geral"],
    summary="Ranking geral da plataforma (Precisa estar autenticado time)",
    description=(
        "Retorna um JSON com ranking dos usuários da plataforma, pegando a posição, "
        "o nome de usuário, o nome, o ano, até três insígnias e a pontuação total."
    ),
)
class RankingGeralView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        usuarios = (
            User.objects.annotate(
                total_pontos=Coalesce(
                    Sum("pontuacao_geral__pontos"), 0
                )
            )
            .order_by("-total_pontos", "username")
        )

        ranking = []
        for idx, user in enumerate(usuarios, start=1):
            serializer = RankingUsuarioSerializer(
                user,
                context={"request": request},
            )
            data = serializer.data
            data["posicao"] = idx
            ranking.append(data)

        return Response(ranking, status=status.HTTP_200_OK)
