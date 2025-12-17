from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

class Evento(models.Model):
    TITULO_MAX_LENGTH = 200

    PUBLICO = "publico"
    PRIVADO = "privado"

    TIPO_EVENTO = [
        (PUBLICO, "Público"),
        (PRIVADO, "Privado"),
    ]

    criador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="eventos_criados"
    )

    titulo = models.CharField(max_length=TITULO_MAX_LENGTH)

    codigo_sala = models.CharField(
        max_length=12,
        unique=True,
        db_index=True,
        default="",
        blank=True,
        help_text="Código único usado para encontrar o evento."
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_EVENTO,
        default=PUBLICO
    )

    # Ajeitar isso aqui dps, acabei deixando sem limite
    limite_participantes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text="Deixe vazio para não limitar."
    )

    mensagem_boas_vindas = models.TextField(
        blank=True,
        help_text="Mensagem exibida quando o usuário entra na sala."
    )

    insignia = models.ImageField(
        upload_to="insignias/",
        null=True,
        blank=True
    )

    # insignia = models.CharField(
    #     max_length=100,
    #     blank=True,
    #     help_text="Nome ou código da insígnia desse evento."
    # )

    # Senha (somente se for privado)
    senha = models.CharField(
        max_length=128,
        blank=True,
        help_text="Senha do evento"
    )

    # Participantes do evento
    participantes = models.ManyToManyField(
        User,
        through="ParticipacaoEvento",
        related_name="eventos_participando",
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} ({self.codigo_sala})"

    def save(self, *args, **kwargs):
        if not self.codigo_sala:
            self.codigo_sala = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.tipo == self.PRIVADO and not self.senha:
            raise ValidationError("Eventos privados precisam de senha.")

        if self.tipo == self.PUBLICO and self.senha:
            raise ValidationError("Eventos públicos não tem senha.")

    @property
    def total_questoes(self):
        return self.questoes.count()

    @property
    def total_participantes(self):
        return self.participantes.count()

    @property
    def is_privado(self):
        return self.tipo == self.PRIVADO

class ParticipacaoEvento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    entrou_em = models.DateTimeField(auto_now_add=True)

    # papel = models.CharField(...)
    # pontuacao = models.IntegerField(default=0)

    class Meta:
        unique_together = ("usuario", "evento")

    def __str__(self):
        return f"{self.usuario.username} em {self.evento.titulo}"
