import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Greedy

from tictactoe import TicTacToe
from player import Player
from lobby import Lobby

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
        self.lobby = Lobby()

        self.signs = [
            ':negative_squared_cross_mark:',
            ':o2:'
        ]

    @commands.command(name="join")
    async def join(self, ctx, id=None):
        if self.lobby.is_user_in_lobby(ctx.author) and not id:
            embed = discord.Embed(title="You are already in the lobby!",
                                  description="Wait for someone to join you!",
                                  color=self.bot.colors['warning'])
            await ctx.send(embed=embed)
            return

        if self.game:
            embed = discord.Embed(title="Lobby is empty! ", description="Join a new one using the !join command",
                                  color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return

        user = ctx.author
        if id:
            print('here')
            user = self.bot.get_user(int(id))
        embed = discord.Embed(title=f"***{user}*** joined the lobby!", color=self.bot.colors['success'])
        await ctx.send(embed=embed)

        self.lobby.add(
            Player(
                user,
                sign=self.signs[self.lobby.size()]
            )
        )

        # if lobby is not ready just exit
        if not self.lobby.is_ready():
            return

        # if code goes here it means game is ready, we can start it
        self.game = TicTacToe(
            self.lobby,
            empty_board=[':one:', ':two:', ':three:', ':four:',
                         ':five:', ':six:', ':seven:', ':eight:', ':nine:']
        )

        # We prepare to print the start of the game
        embed = discord.Embed(title="Game is started!",
                              description="These are the rivals", color=self.bot.colors['success'])

        # We insert the players inside the embed
        players = self.lobby.get_players()
        embed.add_field(name=str(players[0].user), value=players[0].sign, inline=True)
        embed.add_field(name=str(players[1].user), value=players[1].sign, inline=True)

        await ctx.send(embed=embed)

        embed = discord.Embed(title="Board", color=self.bot.colors['success'])
        embed.set_author(name=f"{self.game.get_player_turn().user}'s turn")
        await ctx.send(embed=embed)
        await ctx.send(self.game.get_board_formatted_string())

    @commands.command(name="lobby")
    async def lobby(self, ctx):
        # if lobby is empty we can go back
        if self.lobby.is_empty():
            embed = discord.Embed(title="Lobby is empty!",
                                  description="Join a new one.", color=self.bot.colors['warning'])
            await ctx.send(embed=embed)
            return

        players = self.lobby.get_players()
        embed = discord.Embed(title="Lobby",
                              description="The players currently inside the lobby are as follows!",
                              color=self.bot.colors['success'])
        for i, p in enumerate(players):

            embed.add_field(name=f"Player #{i+1}", value=f"{p.user.name}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="move")
    async def move(self, ctx, position):

        # if there is no game started, we can't perform any move
        if not self.game:
            return

        # only the player with turn is supposed to have the rights to play
        if not self.game.is_user_turn(ctx.author):
            await ctx.send('It\'s not your turn')
            return

        position = int(position) - 1  # we fix the array offset
        self.game.move(position)

        if self.game.winner:
            await ctx.send(f'{self.game.winner} won the game!')

        if self.game.draw:
            await ctx.send('DRAW')
            
        await ctx.send(self.game.get_board_formatted_string())

        # if the game is end, we empty the game variable
        if self.game.end:
            self.end_game()
            return

        embed = discord.Embed(title=f"{self.game.get_player_turn().user}'s turn", color=self.bot.colors['success'])
        await ctx.send(embed=embed)

    @commands.command(name="quit")
    async def quit(self, ctx):
        # user can quit the lobby only if he is in it
        if self.lobby.is_user_in_lobby(ctx.author):
            self.end_game()

            embed = discord.Embed(title="You quit the lobby", color=self.bot.colors['success'])
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="You are not in any lobby", color=self.bot.colors['warning'])
            await ctx.send(embed=embed)

    """
        FUNCTIONS
    """
    def end_game(self):
        self.game = None
        self.lobby.empty()

