from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema

from .models import Evento
from .serializers import (
    EventoSerializer,
    ParticipacaoEventoSerializer,
    EntrarNoEventoSerializer,
)

@extend_schema(tags=["Seção de Eventos"])
class CriarEventoView(generics.CreateAPIView):
    """
    Cria um novo evento vinculado ao usuário autenticado.
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Criar evento",
        description="Cria um novo evento vinculado ao usuário autenticado."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

@extend_schema(tags=["Seção de Eventos"])
class ListarEventosView(generics.ListAPIView):
    """
    Lista todos os eventos cadastrados.
    """
    queryset = Evento.objects.all().order_by("-criado_em")
    serializer_class = EventoSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Listar eventos",
        description="Lista todos os eventos cadastrados na plataforma."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Seção de Eventos"])
class DetalheEventoView(generics.RetrieveAPIView):
    """
    Detalha um evento específico.
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Detalhar evento",
        description="Mostra informações completas sobre um evento."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Seção de Eventos"])
class AtualizarEventoView(generics.UpdateAPIView):
    """
    Permite que o criador do evento edite suas informações.
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Atualizar evento",
        description="Permite que o criador do evento edite suas informações."
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar parcialmente evento",
        description="Permite que o criador atualize parcialmente um evento."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def perform_update(self, serializer):
        evento = serializer.instance
        if evento.criador != self.request.user:
            raise PermissionDenied("Você não tem permissão para editar este evento.")
        serializer.save()


@extend_schema(tags=["Seção de Eventos"])
class DeletarEventoView(generics.DestroyAPIView):
    """
    Permite que o criador delete o evento.
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Excluir evento",
        description="O criador pode deletar seu evento da plataforma."
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance.criador != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar este evento.")
        instance.delete()

@extend_schema(tags=["Seção de Eventos"])
class EntrarNoEventoView(generics.GenericAPIView):
    """
    Endpoint para o usuário entrar em um evento usando o código da sala
    (e senha, se o evento for privado).
    """
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
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        evento = serializer.save()

        evento_data = EventoSerializer(
            evento,
            context={"request": request}
        ).data
        return Response(evento_data, status=status.HTTP_200_OK)
