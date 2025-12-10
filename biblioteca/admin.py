from django.contrib import admin
from .models import Language, LanguageTopic

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "ordem")
    ordering = ("ordem",)

@admin.register(LanguageTopic)
class LanguageTopicAdmin(admin.ModelAdmin):
    list_display = ("titulo", "language", "categoria", "ordem")
    list_filter = ("language", "categoria")
    search_fields = ("titulo", "slug")
    ordering = ("language", "ordem")