from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema
from .models import Questao
from .serializers import QuestaoEventoSerializer


@extend_schema(tags=["Seção das Questões | Mobile"])
class CriarQuestaoView(generics.CreateAPIView):
    serializer_class = QuestaoEventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Criar questão",
        description="Cria uma nova questão vinculada ao usuário autenticado.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)


@extend_schema(tags=["Seção das Questões | Mobile"])
class ListarQuestoesView(generics.ListAPIView):
    queryset = Questao.objects.all().order_by("-criada_em")
    serializer_class = QuestaoEventoSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Listar questões",
        description="Lista todas as questões cadastradas na plataforma.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Seção das Questões | Mobile"])
class DetalheQuestaoView(generics.RetrieveAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoEventoSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Detalhar questão",
        description="Mostra informações completas sobre uma questão.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Seção das Questões | Mobile"])
class AtualizarQuestaoView(generics.UpdateAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoEventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Atualizar questão",
        description="Permite que o autor da questão edite suas informações.",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar parcialmente questão",
        description="Permite que o autor atualize parcialmente uma questão.",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def perform_update(self, serializer):
        if serializer.instance.autor != self.request.user:
            raise PermissionError("Você não tem permissão para editar esta questão.")
        serializer.save()


@extend_schema(tags=["Seção das Questões | Mobile"])
class DeletarQuestaoView(generics.DestroyAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoEventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Excluir questão",
        description="O autor pode deletar sua questão da plataforma.",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance.autor != self.request.user:
            raise PermissionError("Você não tem permissão para deletar esta questão.")
        instance.delete()
