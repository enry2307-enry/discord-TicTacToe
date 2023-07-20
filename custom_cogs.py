import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Greedy

from tictactoe import TicTacToe

from sync import sync as default_sync

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx, guilds: Greedy[discord.Object], spec=None) -> None:
        await default_sync(ctx, guilds, spec)

    @app_commands.command(name="status", description="Use this to see if the bot is online!")
    async def status(self, interaction):
        embed = discord.Embed(title="I am online!", description="Use me for anything you need",
                              color=self.bot.colors['success'])
        await interaction.response.send_message(
            embed=embed
        )


class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game = None
        self.lobby = []

    @commands.command(name="join")
    async def join(self, ctx):
        """if ctx.author.id in self.lobby:
            await ctx.send("You are the host of the lobby! Wait for someone to join")
            return"""

        if self.game:
            await ctx.send('A game is already started! Wait for it to end')
            return

        await ctx.send(f'{ctx.author.id} joined the lobby')
        self.lobby.append(ctx.author.id)
        if len(self.lobby) == 2:
            self.game = TicTacToe(
                id1=self.lobby[0],
                id2=self.lobby[1],
                sign1=':negative_squared_cross_mark:',
                sign2=':o2:',
                empty_board=[':one:', ':two:', ':three:', ':four:',
                             ':five:', ':six:', ':seven:', ':eight:', ':nine:']
            )
            await ctx.send(f'Game is started! \n{self.game.get_board_formatted_string()}')

    @commands.command(name="lobby")
    async def lobby(self, ctx):
        if len(self.lobby) > 0:
            output = "Lobby:\n"
            for userid in self.lobby:
                user = self.bot.get_user(userid)
                output += "\t"+str(user)
            await ctx.send(output)
        else:
            await ctx.send("Lobby is empty, join a new one!")


    @commands.command(name="move")
    async def move(self, ctx, position):
        position = int(position) - 1 # we fix the array offset
        self.game.move(position)
        await ctx.send(self.game.get_board_formatted_string())
