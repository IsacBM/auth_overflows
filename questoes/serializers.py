from rest_framework import serializers
from .models import Questao


class QuestaoEventoSerializer(serializers.ModelSerializer):
    autor = serializers.CharField(source="autor.username", read_only=True)

    class Meta:
        model = Questao
        fields = [
            "id",
            "titulo",
            "enunciado",
            "linguagem",
            "categoria",
            "nivel",
            "pontuacao",
            "resultado_esperado",
            "autor",
            "criada_em",
        ]
        read_only_fields = ["id", "autor", "criada_em"]

    def validate_pontuacao(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError("A pontuação deve ser entre 1 e 100.")
        return value
