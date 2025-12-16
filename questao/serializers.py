from rest_framework import serializers
from .models import Questao, CasoTeste, Submissao, ResultadoTeste

class CasoTesteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasoTeste
        fields = [
            "id",
            "entrada",
            "saida_esperada",
            "ordem",
        ]

class CasoTesteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasoTeste
        fields = ["id", "entrada", "saida_esperada", "ordem"]

class ExemploQuestaoSerializer(serializers.Serializer):
    entrada = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Entrada do exemplo (pode ser vazia)"
    )
    saida = serializers.CharField(
        help_text="Saída esperada do exemplo"
    )

class QuestaoSerializer(serializers.ModelSerializer):
    casos_teste = CasoTesteSerializer(many=True, read_only=True)
    exemplos = ExemploQuestaoSerializer(many=True, required=False)

    class Meta:
        model = Questao
        fields = [
            "id",
            "titulo",
            "descricao_curta",
            "enunciado",
            "pontos",
            "tentativas",
            "dificuldade",
            "categoria",
            "exemplos",
            "casos_teste",
            "evento",
            "criado_por",
            "criado_em",
        ]
        read_only_fields = ["criado_por", "criado_em"]

class SubmissaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submissao
        fields = ["id", "questao", "codigo", "linguagem"]

class ResultadoTesteSerializer(serializers.ModelSerializer):
    caso = CasoTesteSerializer(read_only=True)
    class Meta:
        model = ResultadoTeste
        fields = ["id", "caso", "status", "output", "mensagem", "tempo"]

class SubmissaoDetailSerializer(serializers.ModelSerializer):
    resultado = serializers.SerializerMethodField()
    resultados = ResultadoTesteSerializer(many=True, read_only=True)

    class Meta:
        model = Submissao
        fields = [
            "id",
            "questao",
            "codigo",
            "linguagem",
            "enviada_em",
            "tentativa_num",
            "pontuacao",
            "status",
            "resultado",
            "resultados",
        ]

    def get_resultado(self, obj):
        qs = obj.resultados.all()
        if not qs.exists():
            return obj.status
        prioridades = ["ACCEPTED", "WRONG_ANSWER", "TIMEOUT", "RUNTIME_ERROR"]
        for p in prioridades:
            if qs.filter(status=p).exists():
                return p
        return qs.first().status
