import logging
import random

import discord
from discord import app_commands
from discord.ext import commands

from ballsdex.core.bot import BallsDexBot
from ballsdex.core.utils import checks
from ballsdex.core.utils.buttons import ConfirmChoiceView
from bd_models.models import BallInstance, Player

log = logging.getLogger("ballsdex.packages.admin.haven")


@commands.hybrid_group(name="haven")
async def haven(ctx: commands.Context[BallsDexBot]):
    """Manage collectibles caught in this Discord server (haven)."""
    await ctx.send_help(ctx.command)


@haven.command(name="wipe")
@app_commands.guild_only()
@checks.has_permissions("bd_models.delete_ballinstance", "bd_models.change_ballinstance")
async def haven_wipe(
    ctx: commands.Context[BallsDexBot],
    percentage: int,
    hard: bool = False,
    user: discord.User | None = None,
):
    """Delete a percentage of collectibles caught in this server, optionally for one user."""
    if not 1 <= percentage <= 100:
        await ctx.send("Percentage must be a whole number from 1 to 100.", ephemeral=True)
        return
    if ctx.guild is None:
        await ctx.send("Run this command inside the haven you want to wipe.", ephemeral=True)
        return
    await ctx.defer(ephemeral=True)

    filters: dict[str, int] = {"server_id": ctx.guild.id}
    user_label = "all players"
    if user is not None:
        player = await Player.objects.aget_or_none(discord_id=user.id)
        if player is None:
            await ctx.send("That user has no player data to wipe.", ephemeral=True)
            return
        filters["player_id"] = player.pk
        user_label = f"{user} ({user.id})"

    queryset = BallInstance.objects.filter(**filters)
    instance_ids = [pk async for pk in queryset.values_list("pk", flat=True)]
    target_count = min(len(instance_ids), int(len(instance_ids) * percentage / 100))
    if percentage and instance_ids and target_count == 0:
        target_count = 1
    if not target_count:
        await ctx.send("There are no active collectibles matching that haven and user.", ephemeral=True)
        return

    selected_ids = random.sample(instance_ids, target_count)
    deletion_type = "permanently hard-delete" if hard else "soft-delete"
    details = (
        f"{target_count:,} of {len(instance_ids):,} active collectibles ({percentage}%)\n"
        f"Haven: {ctx.guild.name} ({ctx.guild.id})\n"
        f"User: {user_label}\n"
        f"Mode: {deletion_type}"
        + ("\nThis permanently removes selected rows and any cascading related records." if hard else "")
    )
    view = ConfirmChoiceView(
        ctx,
        accept_message="Confirmed. Processing the haven wipe…",
        cancel_message="Haven wipe cancelled.",
    )
    await ctx.send(f"Confirm haven wipe?\n{details}", view=view, ephemeral=True)
    await view.wait()
    if not view.value:
        return

    if hard:
        _, deleted_details = await BallInstance.all_objects.filter(pk__in=selected_ids).adelete()
        count = deleted_details.get("bd_models.BallInstance", target_count)
    else:
        count = await BallInstance.all_objects.filter(pk__in=selected_ids, deleted=False).aupdate(deleted=True)

    await ctx.send(
        f"{count:,} collectibles {'permanently hard-deleted' if hard else 'soft-deleted'} "
        f"from {ctx.guild.name} for {user_label}.",
        ephemeral=True,
    )
    log.warning(
        "%s %s %s collectibles in haven %s (%s), percentage=%s, user=%s",
        ctx.author,
        "hard-deleted" if hard else "soft-deleted",
        count,
        ctx.guild.name,
        ctx.guild.id,
        percentage,
        user_label,
        extra={"webhook": True},
    )
