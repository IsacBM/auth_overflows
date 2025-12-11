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

class Dificuldade(models.TextChoices):
    FACIL = "facil", "Fácil"
    INTERMEDIARIO = "intermediario", "Intermediário"
    DIFICIL = "dificil", "Difícil"

class Categoria(models.TextChoices): # aumentar as categorias dps
    MATEMATICA = "matematica", "Matemática"
    LOGICA = "logica", "Lógica"
    STRINGS = "strings", "Strings"

class LinguagemProgramacao(models.TextChoices):
    C = "c", "C"
    CSHARP = "csharp", "C#"
    CPP = "cpp", "C++"
    PY = "python", "Python"
    JAVA = "java", "Java"
    JS = "javascript", "Javascript"
    LUA = "lua", "Lua"

class Questao(models.Model):
    titulo = models.CharField(max_length=200)
    descricao_curta = models.CharField(max_length=400, blank=True)
    enunciado = models.TextField()
    pontos = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)])
    tentativas = models.PositiveIntegerField(default=0, help_text="0 = ilimitado")
    dificuldade = models.CharField(max_length=20, choices=Dificuldade.choices, default=Dificuldade.INTERMEDIARIO)
    categoria = models.CharField(max_length=50, choices=Categoria.choices, default=Categoria.LOGICA)
    exemplos = models.JSONField(default=list, help_text="Lista de pares {entrada:..., saida:...} mostrados no front")
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} ({self.dificuldade})"

class CasoTeste(models.Model):
    questao = models.ForeignKey(Questao, related_name="casos_teste", on_delete=models.CASCADE)
    entrada = models.TextField()
    saida_esperada = models.TextField()
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("ordem",)

    def __str__(self):
        return f"Caso {self.ordem} - Q:{self.questao.id}"

class Submissao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissoes")
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name="submissoes")
    codigo = models.TextField()
    linguagem = models.CharField(max_length=30, choices=LinguagemProgramacao.choices)
    enviada_em = models.DateTimeField(auto_now_add=True)
    pontuacao = models.FloatField(null=True, blank=True)  # calculada depois
    tentativa_num = models.PositiveIntegerField(default=1)
    judge0_token = models.CharField(max_length=200, blank=True)  # id retornado pelo Judge0 (se usar)
    status = models.CharField(max_length=50, default="pending")  # pending, processing, done, error
    detalhes = models.JSONField(default=dict, blank=True)  # info extra: outputs, errores etc

    class Meta:
        ordering = ("-enviada_em",)

    def __str__(self):
        return f"Submissao #{self.id} Q:{self.questao.id} by {self.usuario.username}"

    def calcular_pontuacao(self):
        """
        Calcula pontuação com base nos resultados dos testes relacionados (ResultadoTeste).
        Se todos os testes passarem -> pontos completos (questao.pontos).
        Senão pontuação proporcional (ex: 3/4 testes passados).
        """
        resultados = self.resultados.all()
        if not resultados.exists():
            return 0
        total = resultados.count()
        passed = resultados.filter(status="ACCEPTED").count()
        # evita divisão por zero
        fraction = passed / total
        self.pontuacao = round(self.questao.pontos * fraction, 2)
        self.save()
        return self.pontuacao

class ResultadoTeste(models.Model):
    submissao = models.ForeignKey(Submissao, related_name="resultados", on_delete=models.CASCADE)
    caso = models.ForeignKey(CasoTeste, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)  # e.g. "ACCEPTED", "WRONG_ANSWER", "TIMEOUT", "RUNTIME_ERROR"
    output = models.TextField(blank=True)
    mensagem = models.TextField(blank=True)  # erro ou detalhamento
    tempo = models.FloatField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado {self.id} S:{self.status}"
    