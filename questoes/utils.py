from django.db.models import F

def adicionar_pontos_usuario(usuario, pontos):
    profile = usuario.profile
    profile.pontuacao_total = F('pontuacao_total') + pontos
    profile.save(update_fields=['pontuacao_total'])
    profile.refresh_from_db(fields=['pontuacao_total'])
    return profile.pontuacao_total
