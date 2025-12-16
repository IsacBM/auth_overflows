from rest_framework import serializers
from .models import Evento, ParticipacaoEvento

class EventoSerializer(serializers.ModelSerializer):
    criador = serializers.StringRelatedField(read_only=True)
    codigo_sala = serializers.CharField(read_only=True)
    senha = serializers.CharField(write_only=True, allow_blank=True, required=False)
    insignia = serializers.ImageField(required=False, allow_null=True)
    total_questoes = serializers.IntegerField(read_only=True)
    total_participantes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Evento
        fields = [
            "id",
            "titulo",
            "criador",
            "codigo_sala",
            "tipo",
            "mensagem_boas_vindas",
            "insignia",
            "senha",
            "limite_participantes",
            "total_questoes",
            "total_participantes",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = [
            "id",
            "criador",
            "codigo_sala",
            "total_questoes",
            "total_participantes",
            "criado_em",
            "atualizado_em",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                {"detail": "Usuário não autenticado para criar evento."}
            )

        validated_data["criador"] = request.user
        return super().create(validated_data)

    def validate(self, attrs):

        tipo = attrs.get("tipo", getattr(self.instance, "tipo", Evento.PUBLICO))
        senha = attrs.get("senha", getattr(self.instance, "senha", ""))

        limite = attrs.get(
            "limite_participantes",
            getattr(self.instance, "limite_participantes", None),
        )

        errors = {}

        if tipo == Evento.PRIVADO and not senha:
            errors["senha"] = "Eventos privados precisam de senha."

        if tipo == Evento.PUBLICO and senha:
            errors["senha"] = "Eventos públicos não devem ter senha."

        if limite is not None and limite < 2:
            errors["limite_participantes"] = "O limite mínimo é de 2 participantes."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

class ParticipacaoEventoSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)
    evento = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ParticipacaoEvento
        fields = ["id", "usuario", "evento", "entrou_em"]
        read_only_fields = ["id", "usuario", "evento", "entrou_em"]

class EntrarNoEventoSerializer(serializers.Serializer):
    codigo_sala = serializers.CharField()
    senha = serializers.CharField(write_only=True, allow_blank=True, required=False)

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                {"detail": "Usuário não autenticado."}
            )

        user = request.user
        codigo = attrs["codigo_sala"]
        senha = attrs.get("senha", "")

        # Buscar evento
        try:
            evento = Evento.objects.get(codigo_sala=codigo)
        except Evento.DoesNotExist:
            raise serializers.ValidationError({"codigo_sala": "Evento não encontrado."})

        # Validar senha
        if evento.is_privado:
            if not senha:
                raise serializers.ValidationError({"senha": "Evento privado exige senha."})
            if senha != evento.senha:
                raise serializers.ValidationError({"senha": "Senha incorreta."})

        # Validar limite
        if evento.limite_participantes is not None:
            if evento.total_participantes >= evento.limite_participantes:
                raise serializers.ValidationError(
                    {"detail": "O evento já atingiu o limite de participantes."}
                )

        attrs["evento"] = evento
        attrs["usuario"] = user
        return attrs

    def create(self, validated_data):
        evento = validated_data["evento"]
        usuario = validated_data["usuario"]

        participacao, created = ParticipacaoEvento.objects.get_or_create(
            usuario=usuario,
            evento=evento
        )
        return evento
