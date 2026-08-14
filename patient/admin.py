from django.contrib import admin

from .models import (
    TraitementAjustement,
    LigneTraitement,
)


class LigneTraitementInline(admin.TabularInline):
    model = LigneTraitement
    extra = 1


@admin.register(TraitementAjustement)
class TraitementAjustementAdmin(admin.ModelAdmin):
    list_display = (
        "observation",
        "version",
        "date_heure",
        "type_ajustement",
    )
    list_filter = (
        "type_ajustement",
    )
    search_fields = (
        "observation__nom",
        "observation__prenoms",
        "motif",
        "notes",
    )
    inlines = [
        LigneTraitementInline,
    ]