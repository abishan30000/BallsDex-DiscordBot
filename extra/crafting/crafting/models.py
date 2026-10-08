from typing import Self

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.manager import Manager


class CraftRecipe(models.Model):
    input_ball_1 = models.ForeignKey(
        "bd_models.Ball",
        on_delete=models.CASCADE,
        related_name="craft_recipes_as_input_1",
        help_text="One of the two countryballs required to craft the result",
    )
    input_ball_2 = models.ForeignKey(
        "bd_models.Ball",
        on_delete=models.CASCADE,
        related_name="craft_recipes_as_input_2",
        help_text="The other countryball required to craft the result",
    )
    result_ball = models.ForeignKey(
        "bd_models.Ball",
        on_delete=models.CASCADE,
        related_name="craft_recipes_as_result",
        help_text="The countryball obtained by crafting the two inputs together",
    )
    special = models.ForeignKey(
        "bd_models.Special",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="craft_recipes",
        help_text="Optional special applied to the crafted countryball",
    )
    special_id: int | None
    inherit_special = models.BooleanField(
        default=False,
        help_text=(
            "Only usable when no special is set above. If enabled, the crafted countryball "
            "randomly keeps one of the two inputs' specials (e.g. crafting a shiny with a "
            "non-shiny has a 50/50 chance of producing a shiny). If disabled, the result "
            "never has a special."
        ),
    )
    enabled = models.BooleanField(default=True, help_text="Whether this recipe can currently be crafted")
    created_at = models.DateTimeField(auto_now_add=True)

    objects: Manager[Self] = Manager()

    class Meta:
        managed = True
        db_table = "craftrecipe"

    def __str__(self) -> str:
        return f"{self.input_ball_1} + {self.input_ball_2} → {self.result_ball}"

    def clean(self) -> None:
        if self.input_ball_1_id and self.input_ball_1_id == self.input_ball_2_id:
            raise ValidationError("The two input countryballs must be different.")
        if self.inherit_special and self.special_id:
            raise ValidationError("Inherit special can only be enabled when no special is set.")
