from django.urls import path
from .views import LoginView, CadastroView, AlterarSenhaView, AtualizarTokenView,EsqueciSenhaView, RedefinirSenhaView

urlpatterns = [
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('login/', LoginView.as_view(), name='login'),
    path("alterar-senha/", AlterarSenhaView.as_view(), name="alterar_senha"),
    path("atualizar-token/", AtualizarTokenView.as_view(), name="atualizar_token"),
    path("esqueci-senha/", EsqueciSenhaView.as_view(), name="esqueci_senha"),
    path("redefinir-senha/", RedefinirSenhaView.as_view(), name="redefinir_senha"),
]
