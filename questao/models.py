from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

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

    # regra meio gambiarra aqui: se for da plataforma = null se for evento adiciona o id do evento
    evento = models.ForeignKey(
        "eventos.Evento",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="questoes"
    )

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
    