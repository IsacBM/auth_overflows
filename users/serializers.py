from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from .models import Profile
from datetime import date
import re

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'nome',
            'data_nascimento',
            'sexo',
            'tipo_usuario',
            'aceitou_termos',
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'profile',
        ]


class RegisterSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(max_length=150, write_only=True)
    data_nascimento = serializers.DateField(write_only=True)
    sexo = serializers.ChoiceField(write_only=True,choices=Profile.SEXO_CHOICES)
    tipo_usuario = serializers.ChoiceField(write_only=True, choices=Profile.TIPO_USUARIO_CHOICES)

    password = serializers.CharField(write_only=True)
    confirmar_senha = serializers.CharField(write_only=True)

    aceitou_termos = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'confirmar_senha',
            'nome',
            'data_nascimento',
            'sexo',
            'tipo_usuario',
            'aceitou_termos',
        ]

    def validate(self, attrs):
        password = attrs['password']
        confirmar_senha = attrs['confirmar_senha']
        email = attrs.get('email')
        data_nascimento = attrs.get('data_nascimento')
        username = attrs.get('username')

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': "Este e-mail já está sendo usado!"})

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'nome_de_usuario': "Este nome de usuário já existe por aqui :)"})
        
        if data_nascimento and data_nascimento > date.today():
            raise serializers.ValidationError({'data_nascimento': "Já existe máquina do tempo? A data de nascimento não pode ser no futuro! :)"})

        if len(password) < 8:
            raise serializers.ValidationError({"password": "Sua senha precisa de pelo menos uns 8 caracteres :)"})

        if password != confirmar_senha:
            raise serializers.ValidationError({"confirmar_senha": "As senhas não coincidem..."})

        if password and (password.isdigit() or password.isalpha()):
            raise serializers.ValidationError({'password': "A senha deve conter letras e números."})

        if password and not re.search(r"[!@#$%^&*()_+\-={}\[\]:;,.<>?/]", password):
            raise serializers.ValidationError({'password': "A senha deve conter pelo menos um caractere especial."})

        if not attrs.get('aceitou_termos', False):
            raise serializers.ValidationError({"aceitou_termos": "Você precisa aceitar os termos dá plataforma!"})

        return attrs


    def create(self, validated_data):
        nome = validated_data.pop('nome')
        data_nascimento = validated_data.pop('data_nascimento')
        sexo = validated_data.pop('sexo')
        tipo_usuario = validated_data.pop('tipo_usuario')
        aceitou_termos = validated_data.pop('aceitou_termos')

        validated_data.pop('confirmar_senha') # Não vai para o banco
        password = validated_data.pop('password')

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(password)
        user.save()

        Profile.objects.create(
            user=user,
            nome=nome,
            data_nascimento=data_nascimento,
            sexo=sexo,
            tipo_usuario=tipo_usuario,
            aceitou_termos=aceitou_termos,
        )

        return user

class AlterarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True)
    confirmar_senha = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user

        senha_atual = attrs.get('senha_atual')
        nova_senha = attrs.get('nova_senha') or ""
        confirmar_senha = attrs.get('confirmar_senha')
        errors = {}

        if not user.check_password(senha_atual):
            raise serializers.ValidationError({
                "senha_atual": "A senha atual não confere, tenta de novo aí :)"
            })

        if senha_atual == nova_senha:
            raise serializers.ValidationError({
                "nova_senha": "A nova senha não pode ser igual à senha atual :)"
            })

        if len(nova_senha) < 8:
            raise serializers.ValidationError({
                "nova_senha": "A nova senha precisa de pelo menos uns 8 caracteres :)"
            })

        if nova_senha != confirmar_senha:
            raise serializers.ValidationError({
                "confirmar_senha": "As novas senhas não coincidem..."
            })

        if nova_senha.isdigit() or nova_senha.isalpha():
            raise serializers.ValidationError({
                "nova_senha": "A nova senha deve conter letras e números."
            })

        if not re.search(r"[!@#$%^&*()_+\-={}\[\]:;,.<>?/]", nova_senha):
            raise serializers.ValidationError({
                "nova_senha": "A nova senha deve conter pelo menos um caractere especial."
            })

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        nova_senha = self.validated_data['nova_senha']
        user.set_password(nova_senha)
        user.save()
        return user

class EsqueciSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        if not User.objects.filter(email=email).exists():
            # validação pelo e-mail, como você pediu ;)
            raise serializers.ValidationError({
                "email": "Não encontramos nenhuma conta com este e-mail."
            })
        return attrs

    def save(self, **kwargs):
        email = self.validated_data["email"]
        usuario = User.objects.get(email=email)

        gerador = PasswordResetTokenGenerator()
        token = gerador.make_token(usuario)
        uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))

        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        link_redefinicao = f"{frontend_url}/redefinir-senha/{uidb64}/{token}/"

        assunto = "Redefinição de senha - Overflow"
        mensagem = (
            f"Olá!\n\n"
            f"Recebemos um pedido para redefinir a sua senha na plataforma Overflow.\n\n"
            f"Use o link abaixo para criar uma nova senha:\n{link_redefinicao}\n\n"
            f"Se você não fez essa solicitação, pode ignorar este e-mail."
        )

        send_mail(
            assunto,
            mensagem,
            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@overflow.com"),
            [email],
        )

        return {"uid": uidb64, "token": token}


class RedefinirSenhaSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    nova_senha = serializers.CharField(write_only=True)
    confirmar_senha = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uidb64 = attrs.get("uid")
        token = attrs.get("token")
        nova_senha = attrs.get("nova_senha") or ""
        confirmar_senha = attrs.get("confirmar_senha")

        # validações de senha no mesmo estilo do RegisterSerializer:

        if len(nova_senha) < 8:
            raise serializers.ValidationError({
                "nova_senha": "A nova senha precisa de pelo menos uns 8 caracteres :)"
            })

        if nova_senha != confirmar_senha:
            raise serializers.ValidationError({
                "confirmar_senha": "As novas senhas não coincidem..."
            })

        if nova_senha.isdigit() or nova_senha.isalpha():
            raise serializers.ValidationError({
                "nova_senha": "A nova senha deve conter letras e números."
            })

        if not re.search(r"[!@#$%^&*()_+\-={}\[\]:;,.<>?/]", nova_senha):
            raise serializers.ValidationError({
                "nova_senha": "A nova senha deve conter pelo menos um caractere especial."
            })

        # validar uid + token
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            usuario = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({
                "uid": "Link de redefinição inválido. Tente gerar um novo."
            })

        gerador = PasswordResetTokenGenerator()
        if not gerador.check_token(usuario, token):
            raise serializers.ValidationError({
                "token": "Token inválido ou expirado. Tente gerar um novo link."
            })

        # guarda user pra usar no save()
        self.usuario = usuario
        return attrs

    def save(self, **kwargs):
        nova_senha = self.validated_data["nova_senha"]
        usuario = self.usuario
        usuario.set_password(nova_senha)
        usuario.save()
        return usuario