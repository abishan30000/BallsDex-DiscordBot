from django.contrib import admin

from .models import CraftRecipe


@admin.register(CraftRecipe)
class CraftRecipeAdmin(admin.ModelAdmin):
    autocomplete_fields = ("input_ball_1", "input_ball_2", "result_ball", "special")
    save_on_top = True
    fieldsets = [
        ("Inputs", {"fields": ("input_ball_1", "input_ball_2")}),
        ("Result", {"fields": ("result_ball", "special", "inherit_special")}),
        ("Advanced", {"fields": ("enabled",), "classes": ("collapse",)}),
    ]

    list_display = (
        "__str__",
        "input_ball_1",
        "input_ball_2",
        "result_ball",
        "special",
        "inherit_special",
        "enabled",
    )
    list_editable = ("enabled",)
    list_filter = ("enabled", "special", "inherit_special")

    search_fields = ("input_ball_1__country", "input_ball_2__country", "result_ball__country")
    search_help_text = "Search by input or result countryball name"
