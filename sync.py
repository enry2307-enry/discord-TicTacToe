# using this code : https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f

from typing import Literal, Optional
import discord
from discord.ext.commands import Greedy, Context # or a subclass of yours

async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    """
    Works like:
    !sync -> global sync
    !sync ~ -> sync current guild
    !sync * -> copies all global app commands to current guild and syncs
    !sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
    !sync id_1 id_2 -> syncs guilds with id 1 and 2
    """
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return


    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")