from django.db.models import F
from .models import PontuacaoGeral

def adicionar_pontos(usuario, pontos):
    pg, _ = PontuacaoGeral.objects.get_or_create(usuario=usuario)
    pg.pontos = F("pontos") + pontos
    pg.save(update_fields=["pontos"])
    pg.refresh_from_db()
    return pg
