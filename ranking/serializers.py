from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from .models import PontuacaoGeral

class RankingUsuarioSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()
    ano = serializers.SerializerMethodField()
    insignias = serializers.SerializerMethodField()
    pontuacao = serializers.IntegerField(source="total_pontos")
    posicao = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "posicao",
            "username",
            "nome",
            "ano",
            "insignias",
            "pontuacao",
        ]

    def get_nome(self, obj):
        return obj.first_name or obj.username

    def get_ano(self, obj):
        return f"OVER-{timezone.now().year}"

    def get_insignias(self, obj):
        """
        Retorna até 3 insígnias de eventos que o usuário participou.
        """
        from eventos.models import ParticipacaoEvento

        request = self.context.get("request")

        try:
            participacoes = (
                ParticipacaoEvento.objects
                .filter(usuario=obj)
                .select_related("evento")
                .order_by("-entrou_em")
            )
        except Exception:
            return []

        insignias = []
        for p in participacoes:
            evento = getattr(p, "evento", None)
            if not evento:
                continue
            insignia = getattr(evento, "insignia", None)
            if insignia and insignia.url:
                url = insignia.url
                if request:
                    url = request.build_absolute_uri(url)
                insignias.append(url)

            if len(insignias) == 3:
                break

        return insignias
