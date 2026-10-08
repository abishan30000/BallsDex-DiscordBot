from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from ballsdex.core.utils.transformers import BallEnabledTransform
from bd_models.models import Ball, BallInstance, Player

from ..models import CollectorType

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger(__name__)


class Claim(commands.Cog):
    """Commands to claim collector reward balls."""

    claim = app_commands.Group(name="claim", description="Claim reward balls")

    def __init__(self, bot: "BallsDexBot") -> None:
        self.bot = bot
        self._check_task: asyncio.Task | None = None
        self._registered_command_names: list[str] = []

    async def cog_load(self) -> None:
        collector_types = CollectorType.objects.filter(enabled=True).select_related("source_special", "award_special")
        async for ct in collector_types:
            try:
                cmd = self._make_collector_command(ct)
                self.claim.add_command(cmd)
            except (ValueError, app_commands.CommandAlreadyRegistered):
                log.exception("Could not register /claim command for collector type %r", ct.name)
                continue
            self._registered_command_names.append(cmd.name)
        self._check_task = asyncio.create_task(self._check_loop())

    def cog_unload(self) -> None:
        if self._check_task:
            self._check_task.cancel()
        for name in self._registered_command_names:
            self.claim.remove_command(name)
        self._registered_command_names = []

    def _make_collector_command(self, ct: CollectorType) -> app_commands.Command:
        """Return a /claim <name> slash command bound to the given CollectorType."""
        cog = self

        async def callback(
            interaction: discord.Interaction["BallsDexBot"],
            ball: BallEnabledTransform,
        ) -> None:
            await cog._handle_claim(interaction, ball, ct)

        cmd_name = ct.command_name
        callback.__name__ = cmd_name

        cmd: app_commands.Command = app_commands.Command(
            name=cmd_name,
            description=f"Claim a {ct.name} ball.",
            callback=callback,
        )
        app_commands.describe(ball=f"The ball to claim a {ct.name} for")(cmd)
        return cmd

    async def _handle_claim(
        self,
        interaction: discord.Interaction["BallsDexBot"],
        ball: Ball,
        ct: CollectorType,
    ) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)

        if ct.award_special is None:
            await interaction.followup.send(
                f"The **{ct.name}** collector type has no award special configured. "
                "Please contact a bot administrator.",
                ephemeral=True,
            )
            return
        award_special = ct.award_special

        try:
            player = await Player.objects.aget(discord_id=interaction.user.id)
        except Player.DoesNotExist:
            await interaction.followup.send(
                "You don't have a player profile yet. Catch some balls first!",
                ephemeral=True,
            )
            return

        already_has = await BallInstance.objects.filter(
            ball=ball,
            player=player,
            special=award_special,
        ).aexists()
        if already_has:
            await interaction.followup.send(
                f"You already have a **{ball.country} {ct.name}** ball.",
                ephemeral=True,
            )
            return

        source_qs = BallInstance.objects.filter(ball=ball, player=player)
        if ct.source_special is not None:
            source_qs = source_qs.filter(special=ct.source_special)
        count = await source_qs.acount()
        needed = ct.required_count(ball.rarity)

        if count < needed:
            source_label = f"{ct.source_special.name} " if ct.source_special else ""
            await interaction.followup.send(
                f"You need **{needed}** {source_label}{ball.country} balls to claim a "
                f"{ct.name} ball. You currently have **{count}**.",
                ephemeral=True,
            )
            return

        await BallInstance.objects.acreate(
            ball=ball,
            player=player,
            special=award_special,
        )
        await interaction.followup.send(
            f"Successfully claimed your **{ball.country} {ct.name}** ball!",
            ephemeral=True,
        )

    async def _check_loop(self) -> None:
        await self.bot.wait_until_ready()
        while True:
            await asyncio.sleep(86400)  # 24 hours
            try:
                await self._run_checks()
            except Exception:
                log.exception("Error during collector revocation check")

    async def _run_checks(self) -> None:
        """Revoke collector balls from players who no longer meet the threshold."""
        ct_by_award_id: dict[int, CollectorType] = {}
        async for ct in CollectorType.objects.filter(
            enabled=True, award_special__isnull=False
        ).select_related("source_special", "award_special"):
            ct_by_award_id[ct.award_special_id] = ct

        if not ct_by_award_id:
            return

        collector_balls: list[BallInstance] = [
            bi async for bi in BallInstance.objects.filter(
                special_id__in=list(ct_by_award_id)
            ).select_related("ball", "player", "special")
        ]
        if not collector_balls:
            return

        source_count_maps: dict[int | None, dict[tuple[int, int], int]] = {}
        for ct in ct_by_award_id.values():
            sid = ct.source_special_id
            if sid in source_count_maps:
                continue
            relevant = [
                bi for bi in collector_balls
                if (ct_by_award_id.get(bi.special_id) or ct).source_special_id == sid
            ]
            player_ids = list({bi.player_id for bi in relevant})
            ball_ids = list({bi.ball_id for bi in relevant})
            if not player_ids:
                source_count_maps[sid] = {}
                continue
            qs = BallInstance.objects.filter(player_id__in=player_ids, ball_id__in=ball_ids)
            if sid is not None:
                qs = qs.filter(special_id=sid)
            count_map: dict[tuple[int, int], int] = defaultdict(int)
            rows = [row async for row in qs.values_list("player_id", "ball_id")]
            for player_id, ball_id in rows:
                count_map[(player_id, ball_id)] += 1
            source_count_maps[sid] = count_map

        for bi in collector_balls:
            ct = ct_by_award_id.get(bi.special_id)
            if ct is None:
                continue

            count_map = source_count_maps.get(ct.source_special_id, {})
            count = count_map.get((bi.player_id, bi.ball_id), 0)
            needed = ct.required_count(bi.ball.rarity)
            if count >= needed:
                continue

            bi.deleted = True
            await bi.asave(update_fields=["deleted"])
            log.info(
                "Revoked %s %s from player %s (has %d, needs %d)",
                bi.ball.country,
                ct.name,
                bi.player.discord_id,
                count,
                needed,
            )

            try:
                user = self.bot.get_user(bi.player.discord_id) or await self.bot.fetch_user(
                    bi.player.discord_id
                )
                source_label = f"{ct.source_special.name} " if ct.source_special else ""
                await user.send(
                    f"Your **{bi.ball.country} {ct.name}** ball has been removed "
                    f"because you no longer meet the requirement of **{needed}** "
                    f"{source_label}{bi.ball.country} balls (you currently have **{count}**)."
                )
            except discord.HTTPException:
                log.info(
                    "Could not DM player %s about %s %s revocation.",
                    bi.player.discord_id,
                    bi.ball.country,
                    ct.name,
                )
