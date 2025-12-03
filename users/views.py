from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import RegisterSerializer, UserSerializer, AlterarSenhaSerializer, EsqueciSenhaSerializer, RedefinirSenhaSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer pra login com JWT, retornando também dados do usuário.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="Login com username e senha",
        description="Retorna access e refresh tokens JWT junto com dados do usuário.",
        tags=["Autenticação da Conta"],
        request=RegisterSerializer,
        responses=UserSerializer,
        examples=[
            OpenApiExample(
                name="Exemplo de requisição",
                value={
                    "username": "flowPython",
                    "password": "123",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema

class AtualizarTokenView(TokenRefreshView):
    @extend_schema(
        summary="Atualizar token de acesso",
        description="Recebe um refresh token válido e devolve um novo access token.",
        tags=["Autenticação da Conta"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CadastroView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Cadastro do usuário",
        description="Cria usuário",
        tags=["Autenticação da Conta"],
        request=RegisterSerializer,
        responses=UserSerializer,
        examples=[
            OpenApiExample(
                name="Exemplo de requisição",
                value={
                    "username": "Flow",
                    "email": "flow123@overflow.com",
                    "password": "123",
                    "confirmar_senha": "123",
                    "nome": "Overflows",
                    "data_nascimento": "2024-05-15",
                    "sexo": "masculino",
                    "tipo_usuario": "estudante",
                    "aceitou_termos": True,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AlterarSenhaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Alterar senha dentro da plataforma",
        description="Permite que o usuário logado altere sua senha dentro da plataforma",
        tags=["Autenticação da Conta"],
        request=AlterarSenhaSerializer,
        examples=[
            OpenApiExample(
                name="Exemplo de requisição",
                value={
                    "senha_atual": "Overantiga123!",
                    "nova_senha": "FlowNova123!",
                    "confirmar_senha": "FlowNova123!"
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Exemplo de resposta",
                value={"mensagem": "A senha foi alterada com sucesso!"},
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = AlterarSenhaSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"mensagem": "Senha alterada com sucesso."})

class EsqueciSenhaView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Esqueci minha senha",
        description="Envia um e-mail com um link para redefinição de senha, caso o e-mail exista na plataforma.",
        request=EsqueciSenhaSerializer,
        tags=["Autenticação da Conta"],
        examples=[
            OpenApiExample(
                name="Exemplo de requisição",
                value={"email": "user@example.com"},
                request_only=True,
            ),
            OpenApiExample(
                name="Exemplo de resposta",
                value={"mensagem": "Se encontramos este e-mail na plataforma, enviamos um link de redefinição."},
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = EsqueciSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "mensagem": "Se encontramos este e-mail na plataforma, enviamos um link de redefinição."
        })


class RedefinirSenhaView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Redefinir senha",
        description="Redefine a senha a partir de um UID e token válidos enviados por e-mail.",
        request=RedefinirSenhaSerializer,
        tags=["Autenticação da Conta"],
        examples=[
            OpenApiExample(
                name="Exemplo de requisição",
                value={
                    "uid": "dXN1YXJfaWQ=",  # exemplo ilustrativo
                    "token": "tokendeexemplo-123",
                    "nova_senha": "SenhaNova123!",
                    "confirmar_senha": "SenhaNova123!"
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Exemplo de resposta",
                value={"mensagem": "Senha redefinida com sucesso."},
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = RedefinirSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"mensagem": "Senha redefinida com sucesso."})
