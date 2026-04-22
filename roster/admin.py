from django.contrib import admin

from .models import Pokemon, RosterEntry


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = (
        "external_id",
        "display_name_admin",
        "primary_type",
        "secondary_type",
        "total_power_admin",
        "is_default",
        "created_at",
    )
    search_fields = ("name", "external_id")
    list_filter = ("primary_type", "secondary_type", "is_default")
    ordering = ("external_id",)

    @admin.display(description="Nombre")
    def display_name_admin(self, obj):
        return obj.display_name

    @admin.display(description="Total Power")
    def total_power_admin(self, obj):
        return obj.total_power


@admin.register(RosterEntry)
class RosterEntryAdmin(admin.ModelAdmin):
    list_display = (
        "pokemon",
        "location",
        "position",
        "total_power_admin",
        "created_at",
    )
    search_fields = ("pokemon__name", "pokemon__external_id")
    list_filter = ("location",)
    ordering = ("location", "position")
    list_select_related = ("pokemon",)

    @admin.display(description="Total Power")
    def total_power_admin(self, obj):
        return obj.pokemon.total_power