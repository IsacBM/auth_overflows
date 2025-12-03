from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    SEXO_CHOICES = [
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('outro', 'Outro'),
    ]

    TIPO_USUARIO_CHOICES = [
        ('estudante', 'Estudante'),
        ('professor', 'Professor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)

    aceitou_termos = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Perfil"
