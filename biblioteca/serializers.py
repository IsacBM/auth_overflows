from rest_framework import serializers
from .models import Language, LanguageTopic

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "slug", "nome", "ordem"]

class LanguageTopicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageTopic
        fields = ["id", "slug", "titulo", "categoria", "ordem"]

class LanguageTopicDetailSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = LanguageTopic
        fields = [
            "id",
            "slug",
            "titulo",
            "categoria",
            "language",
            "descricao",
            "codigo",
            "saida_esperada",
            "observacoes",
            "ordem",
        ]
