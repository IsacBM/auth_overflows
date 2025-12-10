from django.urls import path
from .views import RankingGeralView

urlpatterns = [
    path("geral/", RankingGeralView.as_view(), name="ranking-geral"),
]
