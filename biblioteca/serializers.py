from rest_framework import serializers
from .models import Linguagem, TopicoLinguagem

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Linguagem
        fields = ["id", "slug", "nome", "ordem"]

class LanguageTopicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicoLinguagem
        fields = ["id", "slug", "titulo", "categoria", "ordem"]

class LanguageTopicDetailSerializer(serializers.ModelSerializer):
    linguagem = LanguageSerializer(read_only=True, source="language") # source="language" precisei apelidar esse caba

    class Meta:
        model = TopicoLinguagem
        fields = [
            "id",
            "slug",
            "titulo",
            "categoria",
            "linguagem",
            "descricao",
            "codigo",
            "saida_esperada",
            "observacoes",
            "ordem",
        ]
