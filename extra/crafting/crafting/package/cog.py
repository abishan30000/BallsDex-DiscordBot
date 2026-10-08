from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

import discord
from asgiref.sync import sync_to_async
from discord import app_commands
from discord.ext import commands
from discord.ui import Container, TextDisplay
from django.db import transaction
from django.db.models import Q

from ballsdex.core.discord import LayoutView
from ballsdex.core.utils.menus import Menu, TextFormatter, TextSource
from ballsdex.core.utils.transformers import BallInstanceTransform, BallEnabledTransform
from bd_models.models import BallInstance
from settings.models import settings

from ..models import CraftRecipe

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger(__name__)

type Interaction = discord.Interaction["BallsDexBot"]


class Crafting(commands.Cog):
    """Combine countryballs into new ones following crafting recipes."""

    def __init__(self, bot: "BallsDexBot") -> None:
        self.bot = bot

    @app_commands.command()
    async def craft(self, interaction: Interaction, ball_one: BallInstanceTransform, ball_two: BallInstanceTransform):
        """
        Combine two of your countryballs into a new one, following a crafting recipe.

        Parameters
        ----------
        ball_one: BallInstance
            The first countryball to use in the recipe.
        ball_two: BallInstance
            The second countryball to use in the recipe.
        """
        await interaction.response.defer(thinking=True, ephemeral=True)

        if ball_one.pk == ball_two.pk:
            await interaction.followup.send(
                f"You need to select two different {settings.collectible_name}s.", ephemeral=True
            )
            return

        recipe = (
            await CraftRecipe.objects.filter(enabled=True)
            .filter(
                Q(input_ball_1_id=ball_one.ball_id, input_ball_2_id=ball_two.ball_id)
                | Q(input_ball_1_id=ball_two.ball_id, input_ball_2_id=ball_one.ball_id)
            )
            .select_related("result_ball", "special")
            .afirst()
        )
        if recipe is None:
            await interaction.followup.send(
                f"No crafting recipe exists for "
                f"{ball_one.description(short=True, include_emoji=True, bot=self.bot)} and "
                f"{ball_two.description(short=True, include_emoji=True, bot=self.bot)}.",
                ephemeral=True,
            )
            return

        # the crafted ball's bonuses are rolled somewhere between the two inputs'
        attack_bonus = random.randint(*sorted((ball_one.attack_bonus, ball_two.attack_bonus)))
        health_bonus = random.randint(*sorted((ball_one.health_bonus, ball_two.health_bonus)))

        crafted = await sync_to_async(self._craft)(ball_one, ball_two, recipe, attack_bonus, health_bonus)

        log.info(
            "%s crafted %s from %s and %s",
            interaction.user.id,
            crafted.countryball.country,
            ball_one.countryball.country,
            ball_two.countryball.country,
        )
        await interaction.followup.send(
            f"You crafted {crafted.description(include_emoji=True, bot=self.bot)}!", ephemeral=True
        )

    @app_commands.command()
    async def recipes(
        self,
        interaction: Interaction,
        ball_one: BallEnabledTransform | None = None,
        ball_two: BallEnabledTransform | None = None,
    ):
        """
        List crafting recipes, optionally narrowed down to ones using the given countryballs.

        Parameters
        ----------
        ball_one: Ball | None
            Only show recipes that use this countryball as an ingredient.
        ball_two: Ball | None
            Only show recipes that also use this countryball as an ingredient.
        """
        await interaction.response.defer(thinking=True)

        queryset = (
            CraftRecipe.objects.filter(enabled=True)
            .select_related("input_ball_1", "input_ball_2", "result_ball", "special")
            .order_by("result_ball__country", "input_ball_1__country", "input_ball_2__country")
        )

        if ball_one and ball_two and ball_one.pk != ball_two.pk:
            queryset = queryset.filter(
                Q(input_ball_1_id=ball_one.pk, input_ball_2_id=ball_two.pk)
                | Q(input_ball_1_id=ball_two.pk, input_ball_2_id=ball_one.pk)
            )
        elif selected := (ball_one or ball_two):
            queryset = queryset.filter(Q(input_ball_1_id=selected.pk) | Q(input_ball_2_id=selected.pk))

        if not await queryset.aexists():
            await interaction.followup.send("No crafting recipes found.")
            return

        def emoji(ball) -> str:
            return f"{self.bot.get_emoji(ball.emoji_id) or ''} "

        text = ""
        async for recipe in queryset:
            special_text = f" ({recipe.special.name})" if recipe.special else ""
            text += (
                f"- {emoji(recipe.input_ball_1)}{recipe.input_ball_1.country} + "
                f"{emoji(recipe.input_ball_2)}{recipe.input_ball_2.country} → "
                f"{emoji(recipe.result_ball)}{recipe.result_ball.country}{special_text}\n"
            )

        view = LayoutView()
        container = Container()
        display = TextDisplay("")
        container.add_item(display)
        view.add_item(container)
        menu = Menu(self.bot, view, TextSource(text), TextFormatter(display))
        await menu.init()
        await interaction.followup.send(view=view)

    @transaction.atomic()
    def _craft(
        self, ball_one: BallInstance, ball_two: BallInstance, recipe: CraftRecipe, attack_bonus: int, health_bonus: int
    ) -> BallInstance:
        # synchronous to allow an atomic transaction, see ballsdex.packages.trade.trade
        for instance in (ball_one, ball_two):
            instance.deleted = True
        BallInstance.objects.bulk_update((ball_one, ball_two), fields=("deleted",))

        if recipe.special_id:
            special_id = recipe.special_id
        elif recipe.inherit_special:
            # 50/50 chance of keeping either input's special, may also be None for a non-special input
            special_id = random.choice((ball_one.special_id, ball_two.special_id))
        else:
            special_id = None

        return BallInstance.objects.create(
            ball=recipe.result_ball,
            player=ball_one.player,
            special_id=special_id,
            attack_bonus=attack_bonus,
            health_bonus=health_bonus,
            server_id=ball_one.server_id,
        )
