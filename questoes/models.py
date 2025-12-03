from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Questao(models.Model):
    TITULO_MAX_LENGTH = 200

    LINGUAGEM_CHOICES = [
        ("python", "Python"),
        ("javascript", "JavaScript"),
        ("java", "Java"),
        ("c", "C"),
        ("cpp", "C++"),
        ("csharp", "C#"),
    ]

    CATEGORIA_CHOICES = [
        ("matematica", "Matemática"),
        ("logica", "Lógica"),
        ("strings", "Strings"),
        ("arrays", "Arrays"),
        ("algoritmos", "Algoritmos"),
        ("boas_vindas", "Boas-vindas"),
        ("recursao", "Recursão"),
        ("grafos", "Grafos"),
    ]

    NIVEL_CHOICES = [
        ("facil", "Fácil"),
        ("medio", "Médio"),
        ("dificil", "Difícil"),
    ]

    titulo = models.CharField(max_length=TITULO_MAX_LENGTH)
    enunciado = models.TextField()

    linguagem = models.CharField(
        max_length=20,
        choices=LINGUAGEM_CHOICES,
    )

    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIA_CHOICES,
    )

    nivel = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        default="facil",
    )

    pontuacao = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=10,
        help_text="Pontuação da questão (1 a 100).",
    )

    resultado_esperado = models.TextField(
        help_text="Descrição do resultado esperado (ex: saída do programa).",
    )

    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="questoes_criadas",
    )

    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
