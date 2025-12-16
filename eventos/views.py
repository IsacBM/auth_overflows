import traceback
import logging
from functools import cmp_to_key

from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from django.db.models import Sum, Count, Max, Min
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from .models import Evento
from questao.models import Questao
from django.apps import apps
from .serializers import (
    EventoSerializer,
    EntrarNoEventoSerializer,
)
from questao.serializers import QuestaoSerializer

logger = logging.getLogger(__name__)

@extend_schema(tags=["Seção de Eventos | CRUD"])
class CriarEventoView(generics.CreateAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Criar evento",
        description="Cria um novo evento vinculado ao usuário autenticado.",
        responses=EventoSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

@extend_schema(tags=["Seção de Eventos | CRUD"])
class ListarEventosView(generics.ListAPIView):
    queryset = Evento.objects.all().order_by("-criado_em")
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Listar eventos",
        description="Lista todos os eventos cadastrados na plataforma.",
        responses=EventoSerializer(many=True),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(tags=["Seção de Eventos | CRUD"])
class DetalheEventoView(generics.RetrieveAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Detalhar evento",
        description="Mostra informações completas sobre um evento.",
        responses=EventoSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(tags=["Seção de Eventos | CRUD"])
class AtualizarEventoView(generics.UpdateAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Atualizar evento",
        description="Permite que o criador do evento edite suas informações.",
        responses=EventoSerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar parcialmente evento",
        description="Permite que o criador atualize parcialmente um evento.",
        responses=EventoSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def perform_update(self, serializer):
        evento = serializer.instance
        if evento.criador != self.request.user:
            raise PermissionDenied("Você não tem permissão para editar este evento.")
        serializer.save()

@extend_schema(tags=["Seção de Eventos | CRUD"])
class DeletarEventoView(generics.DestroyAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Excluir evento",
        description="O criador pode deletar seu evento da plataforma.",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance.criador != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar este evento.")
        instance.delete()

@extend_schema(tags=["Seção de Eventos | Participação"])
class EntrarNoEventoView(generics.GenericAPIView):
    serializer_class = EntrarNoEventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Entrar em evento",
        description=(
            "Permite que um usuário entre em um evento informando "
            "o código da sala e, se necessário, a senha."
        ),
        request=EntrarNoEventoSerializer,
        responses={200: EventoSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        evento = serializer.save()

        evento_data = EventoSerializer(evento, context={"request": request}).data
        return Response(evento_data, status=status.HTTP_200_OK)

@extend_schema(tags=["Seção de Eventos | CRUD Questões"])
class ListarQuestoesDoEventoView(generics.ListAPIView):
    serializer_class = QuestaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Listar as questões do evento",
        description="Retorna as questões vinculadas ao evento informado.",
        responses=QuestaoSerializer(many=True),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        evento_pk = self.kwargs.get("evento_pk")
        evento = get_object_or_404(Evento, pk=evento_pk)

        qs = getattr(evento, "questoes", None)
        if qs is not None:
            try:
                return qs.all().order_by("-criado_em")
            except Exception:
                pass

        try:
            return Questao.objects.filter(evento=evento).order_by("-criado_em")
        except Exception:
            return Questao.objects.all().order_by("-criado_em")

@extend_schema(tags=["Seção de Eventos | CRUD Questões"])
class CriarQuestaoNoEventoView(generics.CreateAPIView):
    serializer_class = QuestaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Criar questão no evento",
        description="Cria uma nova questão vinculada ao evento especificado.",
        responses=QuestaoSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        evento = get_object_or_404(Evento, pk=self.kwargs["evento_pk"])

        if evento.criador != self.request.user:
            raise PermissionDenied(
                "Somente o criador do evento pode adicionar questões."
            )

        serializer.save(
            evento=evento,
            criado_por=self.request.user
        )

@extend_schema(tags=["Seção de Eventos | CRUD Questões"])
class MeusEventosView(generics.ListAPIView):
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Listar meus eventos",
        description="Retorna apenas os eventos criados pelo usuário autenticado.",
        responses=EventoSerializer(many=True),
    )
    def get_queryset(self):
        return (
            Evento.objects
            .filter(criador=self.request.user)
            .order_by("-criado_em")
        )


# loucura do ranking
@extend_schema(tags=["Seção de Eventos | Ranking"])
class RankingEventoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
            summary="Ranking do evento",
            description=(
                "Retorna ranking de participantes com campo 'posicao'. "
                "Regras de desempate: Pontos totais (maior melhor) > submissões totais (menor melhor) > "
                "tempo apenas nas questões em comum (menor melhor) > tempo na questão de maior peso/dificuldade (menor melhor)"
            )
    )
    def get(self, request, evento_pk, *args, **kwargs):
        Submissao = apps.get_model("questoes", "Submissao")

        try:
            evento = get_object_or_404(Evento, pk=evento_pk)
            participantes = list(evento.participantes.all())

            # Se não houver participantes, retorna lista vazia
            if not participantes:
                return Response([], status=status.HTTP_200_OK)

            stats_qs = (
                Submissao.objects
                .filter(usuario__in=participantes)
                .values("usuario__id", "usuario__username")
                .annotate(
                    total_pontos=Sum("pontuacao"),
                    total_submissoes=Count("id"),
                    ultima_sub=Max("enviada_em"),
                )
            )
            stats_map = {item["usuario__id"]: item for item in stats_qs}

            first_ac_qs = (
                Submissao.objects
                .filter(usuario__in=participantes, pontuacao__isnull=False)
                .values("usuario_id", "questao_id")
                .annotate(first_ac=Min("enviada_em"))
            )

            per_user_first_ac = {}
            for r in first_ac_qs:
                uid = r["usuario_id"]
                qid = r["questao_id"]
                per_user_first_ac.setdefault(uid, {})[qid] = r["first_ac"]

            questao_ids = set()
            for uid, qmap in per_user_first_ac.items():
                questao_ids.update(qmap.keys())
            questao_objs = {}
            if questao_ids:
                q_objs = Questao.objects.filter(id__in=questao_ids).values("id", "pontos")
                for q in q_objs:
                    questao_objs[q["id"]] = q["pontos"]

            users_data = []
            for u in participantes:
                s = stats_map.get(u.id, None)
                total_pontos = float(s["total_pontos"] or 0) if s else 0.0
                total_submissoes = int(s["total_submissoes"] or 0) if s else 0
                ultima_sub = s["ultima_sub"] if s else None
                users_data.append({
                    "id": u.id,
                    "username": u.username,
                    "total_pontos": total_pontos,
                    "total_submissoes": total_submissoes,
                    "ultima_sub": ultima_sub,
                    "first_ac_map": per_user_first_ac.get(u.id, {})  # pode ser vazio
                })

            groups = {}
            for ud in users_data:
                key = (ud["total_pontos"], ud["total_submissoes"])
                groups.setdefault(key, []).append(ud)

            def seconds_since_event_start(dt):
                if not dt or not evento.criado_em:
                    return None
                try:
                    delta = dt - evento.criado_em
                    return max(0.0, delta.total_seconds())
                except Exception:
                    return None

            def cmp_users(a, b):
                a_map = a.get("first_ac_map", {})
                b_map = b.get("first_ac_map", {})

                common = set(a_map.keys()).intersection(set(b_map.keys()))
                if common:
                    a_sum = 0.0
                    b_sum = 0.0
                    for qid in common:
                        a_t = seconds_since_event_start(a_map.get(qid))
                        b_t = seconds_since_event_start(b_map.get(qid))
                        # se algum tempo faltar considera como infinito
                        if a_t is None:
                            a_sum = float("inf"); break
                        if b_t is None:
                            b_sum = float("inf"); break
                        a_sum += a_t
                        b_sum += b_t
                    if a_sum != b_sum:
                        return -1 if a_sum < b_sum else 1

                def highest_weight_time(user):
                    fmap = user.get("first_ac_map", {})
                    best_q = None
                    best_points = -1
                    best_time = None
                    for qid, dt in fmap.items():
                        pts = questao_objs.get(qid, 0)
                        if pts > best_points:
                            best_points = pts
                            best_q = qid
                            best_time = dt
                        elif pts == best_points:
                            # se mesmo peso, pega o menor tempo
                            t = seconds_since_event_start(dt)
                            bt = seconds_since_event_start(best_time)
                            if t is not None and bt is not None and t < bt:
                                best_q = qid
                                best_time = dt
                    return best_points, seconds_since_event_start(best_time) if best_time else None

                a_best_pts, a_best_time = highest_weight_time(a)
                b_best_pts, b_best_time = highest_weight_time(b)

                # se somente um tem tempo na maior questão, esse ganha
                if a_best_time is None and b_best_time is not None:
                    return 1
                if b_best_time is None and a_best_time is not None:
                    return -1
                # se ambos têm tempo, o menor vence
                if a_best_time is not None and b_best_time is not None and a_best_time != b_best_time:
                    return -1 if a_best_time < b_best_time else 1

                # desempate por username
                a_name = (a.get("username") or "").lower()
                b_name = (b.get("username") or "").lower()
                if a_name < b_name:
                    return -1
                if a_name > b_name:
                    return 1
                return 0
            
            sorted_group_keys = sorted(groups.keys(), key=lambda k: (-k[0], k[1]))

            final_ordered = []
            for key in sorted_group_keys:
                group_list = groups[key]
                if len(group_list) > 1:
                    group_list_sorted = sorted(group_list, key=cmp_to_key(cmp_users))
                else:
                    group_list_sorted = group_list
                final_ordered.extend(group_list_sorted)

            usuarios_com_pontos = [u for u in final_ordered if u["total_pontos"] > 0]
            usuarios_sem_pontos = [u for u in final_ordered if u["total_pontos"] == 0]

            usuarios_sem_pontos_ordenado = sorted(usuarios_sem_pontos, key=lambda u: (u["username"] or "").lower())

            final_ordered = usuarios_com_pontos + usuarios_sem_pontos_ordenado

            any_submission = Submissao.objects.filter(usuario__in=participantes, pontuacao__isnull=False).exists()
            if not any_submission:
                final_ordered = sorted(final_ordered, key=lambda u: (u["username"][0].lower() if u["username"] else ""))

            ranking = []
            prev_key = None
            current_pos = 0
            dense_rank = 0
            for item in final_ordered:
                dense_rank += 1
                key = (item["total_pontos"], item["total_submissoes"], item.get("ultima_sub"))
                if prev_key is not None and key == prev_key:
                    pos = current_pos
                else:
                    pos = dense_rank
                    current_pos = pos
                    prev_key = key

                ranking.append({
                    "posicao": pos,
                    "id": item["id"],
                    "username": item["username"],
                    "total_pontos": item["total_pontos"],
                    "total_submissoes": item["total_submissoes"],
                    "ultima_sub": item["ultima_sub"],
                })

            return Response(ranking, status=status.HTTP_200_OK)

        except Exception as e:
            tb = traceback.format_exc()
            logger.exception("Erro ao gerar ranking do evento %s: %s", evento_pk, str(e))
            if getattr(settings, "DEBUG", False):
                return Response({"detail": "Erro interno", "exception": str(e), "trace": tb}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"detail": "Erro interno"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
