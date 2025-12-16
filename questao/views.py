from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from .models import CasoTeste, Submissao, ResultadoTeste
from questao.models import Questao
from .serializers import (
    QuestaoSerializer,
    SubmissaoCreateSerializer,
    ResultadoTesteSerializer,
    SubmissaoDetailSerializer,
    CasoTesteCreateSerializer,
)

@extend_schema(
    tags=["Seção de Questões | CRUD Plataforma"],
    request=QuestaoSerializer,
    responses=QuestaoSerializer,
)
class CriarQuestaoPlataformaView(generics.CreateAPIView):
    serializer_class = QuestaoSerializer
    permission_classes = [permissions.IsAuthenticated]  # depois vira IsAdminUser

    @extend_schema(
        summary="Criar questão da plataforma",
        description="Cria uma nova questão global (não vinculada a evento).",
        responses=QuestaoSerializer,
    )
    def perform_create(self, serializer):
        serializer.save(
            criado_por=self.request.user,
            evento=None  # força ser da plataforma
        )


@extend_schema(tags=["Seção de Questões | CRUD Plataforma"])
class ListarQuestoesPlataformaView(generics.ListAPIView):
    serializer_class = QuestaoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Questao.objects.filter(evento__isnull=True).order_by("-criado_em")


@extend_schema(tags=["Seção de Questões | CRUD Plataforma"])
class DetalharQuestaoView(generics.RetrieveAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Detalhar questão",
        description="Retorna os detalhes de uma questão específica.",
        responses=QuestaoSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(tags=["Seção de Questões | CRUD Plataforma"])
class AtualizarQuestaoView(generics.UpdateAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Atualizar questão",
        description="Atualiza os dados de uma questão (PUT completo).",
        responses=QuestaoSerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar parte da questão",
        description="Atualiza parcialmente os dados da questão (PATCH).",
        responses=QuestaoSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def perform_update(self, serializer):
        questao = serializer.instance
        if getattr(questao, "criado_por", None) and questao.criado_por != self.request.user:
            raise PermissionDenied("Você não tem permissão para editar essa questão.")
        serializer.save()

@extend_schema(tags=["Seção de Questões | CRUD Plataforma"])
class DeletarQuestaoView(generics.DestroyAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Deletar questão",
        description="Remove a questão especificada (requer permissão).",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if getattr(instance, "criado_por", None) and instance.criado_por != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar essa questão.")
        instance.delete()

@extend_schema(tags=["Seção de Questões | Submissão de Resposta:"])
@extend_schema(tags=["Seção de Questões | Submissão de Resposta"])
class SubmeterSolucaoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Submeter solução",
        description=(
            "Submete uma solução para uma questão. "
            "Se a questão estiver vinculada a um evento, "
            "valida a participação do usuário no evento."
        ),
        request=SubmissaoCreateSerializer,
        responses={200: ResultadoTesteSerializer(many=True)}
    )
    def post(self, request, questao_pk, *args, **kwargs):
        usuario = request.user
        questao = get_object_or_404(Questao, pk=questao_pk)

        # 🔹 Contexto opcional: evento
        evento = questao.evento

        # 🔐 Se for questão de evento, valida participação
        if evento:
            from eventos.models import ParticipacaoEvento

            if not ParticipacaoEvento.objects.filter(
                usuario=usuario,
                evento=evento
            ).exists():
                return Response(
                    {"detail": "Você não está participando deste evento."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = SubmissaoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        codigo = serializer.validated_data["codigo"]
        linguagem = serializer.validated_data["linguagem"]

        # 🔁 Controle de tentativas
        if questao.tentativas > 0:
            total_submissoes = Submissao.objects.filter(
                usuario=usuario,
                questao=questao
            ).count()

            if total_submissoes >= questao.tentativas:
                return Response(
                    {"detail": "Limite de tentativas atingido."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 🧱 Criação da submissão
        with transaction.atomic():
            tentativa_num = (
                Submissao.objects.filter(usuario=usuario, questao=questao).count() + 1
            )

            submissao = Submissao.objects.create(
                usuario=usuario,
                questao=questao,
                codigo=codigo,
                linguagem=linguagem,
                tentativa_num=tentativa_num,
                status="processing",
            )

        # 🚀 Judge0
        judge0_url = getattr(settings, "JUDGE0_SUBMIT_URL", None)
        judge0_key = getattr(settings, "JUDGE0_API_KEY", None)
        lang_map = getattr(settings, "JUDGE0_LANG_MAP", {})

        if not judge0_url:
            submissao.status = "error"
            submissao.detalhes = {"error": "Judge0 não configurado"}
            submissao.save()
            return Response(
                {"detail": "Judge0 não configurado."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        casos = questao.casos_teste.all()
        headers = {"Content-Type": "application/json"}
        if judge0_key:
            headers["Authorization"] = f"Token {judge0_key}"

        language_id = lang_map.get(linguagem, linguagem)

        try:
            import requests

            for caso in casos:
                payload = {
                    "source_code": codigo,
                    "language_id": language_id,
                    "stdin": caso.entrada,
                    "expected_output": caso.saida_esperada,
                }

                r = requests.post(
                    judge0_url,
                    json=payload,
                    headers=headers,
                    timeout=15
                )
                r.raise_for_status()
                resp = r.json()

                status_text = (
                    resp.get("status", {}).get("description")
                    if isinstance(resp, dict)
                    else "UNKNOWN"
                )
                output = resp.get("stdout") or ""
                mensagem = resp.get("stderr") or resp.get("compile_output") or ""
                tempo = resp.get("time")

                ResultadoTeste.objects.create(
                    submissao=submissao,
                    caso=caso,
                    status=status_text or "UNKNOWN",
                    output=output,
                    mensagem=mensagem,
                    tempo=tempo,
                )

            submissao.status = "done"
            submissao.calcular_pontuacao()
            submissao.detalhes = {"processed_at": timezone.now().isoformat()}
            submissao.save()

        except Exception as e:
            submissao.status = "error"
            submissao.detalhes = {"error": str(e)}
            submissao.save()
            return Response(
                {"detail": "Erro ao avaliar a submissão", "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        resultados = ResultadoTesteSerializer(
            submissao.resultados.all(),
            many=True
        ).data

        return Response(
            {
                "submissao_id": submissao.id,
                "pontuacao": submissao.pontuacao,
                "resultados": resultados,
            },
            status=status.HTTP_200_OK
        )

def resumir_resultados(resultados_qs, submissao=None):
    
    resultados = list(resultados_qs)
    total = len(resultados)
    if total == 0:
        s = (getattr(submissao, "status", None) or "PENDING").upper()
        return {
            "status": s,
            "testes_totais": 0,
            "testes_passados": 0,
            "percentual": 0.0,
            "mensagem": None
        }

    passed = sum(1 for r in resultados if (r.status or "").upper() in ("ACCEPTED", "AC"))
    percentual = round((passed / total) * 100, 2)

    # se todos passaram
    if passed == total:
        return {
            "status": "ACCEPTED",
            "testes_totais": total,
            "testes_passados": passed,
            "percentual": percentual,
            "mensagem": None
        }

    # se alguns passaram
    if 0 < passed < total:
        # mensagem: pega primeira mensagem de um teste que tenha mensagem/erro
        first_fail = next((r for r in resultados if (r.status or "").upper() not in ("ACCEPTED", "AC")), None)
        msg = None
        if first_fail:
            msg = first_fail.mensagem or first_fail.output or first_fail.status
        return {
            "status": "PARTIAL",
            "testes_totais": total,
            "testes_passados": passed,
            "percentual": percentual,
            "mensagem": msg
        }

    # se nenhum passou
    # tentar pegar status mais comum ou primeira mensagem útil
    first_fail = next((r for r in resultados if (r.status or "").upper() not in ("ACCEPTED", "AC")), resultados[0])
    msg = first_fail.mensagem or first_fail.output or first_fail.status
    return {
        "status": "FAILED",
        "testes_totais": total,
        "testes_passados": 0,
        "percentual": 0.0,
        "mensagem": msg
    }

@extend_schema(tags=["Seção de Questões | Submissão de Resposta:"])
class MinhasSubmissoesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissaoDetailSerializer

    @extend_schema(
        summary="Listar minhas submissões",
        description="Retorna o histórico de submissões do usuário autenticado, incluindo resumo final e resultados por caso de teste.",
        responses=SubmissaoDetailSerializer(many=True),
    )
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().prefetch_related(Prefetch("resultados"))
        page = self.paginate_queryset(qs)
        objs = page or qs

        serializer = self.get_serializer(objs, many=True)

        # montar extras
        extras = {}
        for sub in objs:
            resultados_qs = sub.resultados.all()
            resumo = resumir_resultados(resultados_qs, submissao=sub)
            detalhes = ResultadoTesteSerializer(resultados_qs, many=True).data
            extras[sub.id] = {"resultado": resumo, "resultados": detalhes}

        serialized_list = serializer.data
        for item in serialized_list:
            sid = item["id"]
            item["resultado"] = extras[sid]["resultado"]
            item["resultados"] = extras[sid]["resultados"]

        if page is not None:
            return self.get_paginated_response(serialized_list)
        return Response(serialized_list, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Submissao.objects.filter(usuario=self.request.user).order_by("-enviada_em")

@extend_schema(tags=["Seção de Questões | Submissão de Resposta:"])
class DetalheSubmissaoView(generics.RetrieveAPIView):
    """
    Retorna os dados de uma submissão específica, incluindo:
    - 'resultado' (em resumo)
    - 'resultados' (em detalhe)
    """
    queryset = Submissao.objects.all().prefetch_related(Prefetch("resultados"))
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissaoDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data

        resultados_qs = instance.resultados.all()
        resultados = ResultadoTesteSerializer(resultados_qs, many=True).data
        resumo = resumir_resultados(resultados_qs, submissao=instance)

        data["resultado"] = resumo
        data["resultados"] = resultados
        return Response(data, status=status.HTTP_200_OK)

@extend_schema(tags=["Seção de Questões | Casos de Teste"])
class CriarCasoTesteView(generics.CreateAPIView):
    serializer_class = CasoTesteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]  # depois vira admin

    @extend_schema(
        summary="Adicionar caso de teste",
        description="Adiciona um novo caso de teste a uma questão.",
        responses=CasoTesteCreateSerializer,
    )
    def perform_create(self, serializer):
        questao = get_object_or_404(
            Questao,
            pk=self.kwargs["questao_pk"]
        )

        serializer.save(questao=questao)

@extend_schema(tags=["Seção de Questões | Casos de Teste"])
class ListarCasosTesteView(generics.ListAPIView):
    serializer_class = CasoTesteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CasoTeste.objects.filter(
            questao_id=self.kwargs["questao_pk"]
        ).order_by("ordem")

@extend_schema(tags=["Seção de Questões | Casos de Teste"])
class AtualizarCasoTesteView(generics.UpdateAPIView):
    queryset = CasoTeste.objects.all()
    serializer_class = CasoTesteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

@extend_schema(tags=["Seção de Questões | Casos de Teste"])
class DeletarCasoTesteView(generics.DestroyAPIView):
    queryset = CasoTeste.objects.all()
    serializer_class = CasoTesteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
