from django.db import models


class Language(models.Model):
    slug = models.SlugField(unique=True)  # "python", "c", "cpp", "csharp", "java", "javascript"
    nome = models.CharField(max_length=50)
    ordem = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome

class LanguageTopic(models.Model):
    class Categoria(models.TextChoices):
        INTRO = "introducao", "Introdução"
        SINTAXE = "sintaxe", "Sintaxe"
        VARIAVEIS = "variaveis", "Variáveis"
        TIPOS = "tipos", "Tipos de Dados"
        OPERADORES = "operadores", "Operadores"
        LACOS = "lacos", "Laços de repetição"
        FUNCOES = "funcoes", "Funções"

    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name="topicos",
    )
    slug = models.SlugField()
    titulo = models.CharField(max_length=100)
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.INTRO,
    )

    ordem = models.PositiveIntegerField(default=0)
    descricao = models.TextField()
    codigo = models.TextField()
    saida_esperada = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        unique_together = ("language", "slug")
        ordering = ["language", "ordem"]

    def __str__(self):
        return f"{self.language.nome} - {self.titulo}"
