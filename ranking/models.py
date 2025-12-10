from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PontuacaoGeral(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pontuacao_geral",
    )
    pontos = models.IntegerField(default=0)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.pontos} pts"
