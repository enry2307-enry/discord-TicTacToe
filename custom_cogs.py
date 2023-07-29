import datetime
from math import fabs

import discord
from discord import app_commands
from discord.ext import commands, tasks
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

        self.channel = None  # We store the channel the game is being played in

        self.signs = [
            ':negative_squared_cross_mark:',
            ':o2:'
        ]

    @commands.command(name="join")
    async def join(self, ctx, id_=None):
        if self.lobby.is_user_in_lobby(ctx.author) and not id_:
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
        if id_:
            user = self.bot.get_user(int(id_))
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
        embed = discord.Embed(title=f"{self.game.get_player_turn().user}'s turn",
                              description="These are the rivals!", color=self.bot.colors['success'])
        embed.set_author(name="Game is started")
        embed.set_footer(text="The game can last a maximum of 2 minutes due to bandwidth limitations.")

        # We insert the players inside the embed
        players = self.lobby.get_players()
        embed.add_field(name=str(players[0].user), value=players[0].sign, inline=True)
        embed.add_field(name=str(players[1].user), value=players[1].sign, inline=True)

        # We send the messages
        await ctx.send(embed=embed)
        await ctx.send(self.game.get_board_formatted_string())

        # We start the timer to check afk players
        self.afk_timer.start()

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
        # uncomment these lines to avoid EVERYONE moving on the board
        """if not self.game.is_user_turn(ctx.author):
            embed = discord.Embed(title=f"It's not your turn!", color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return"""

        position = int(position) - 1  # we fix the array offset
        self.game.move(position)  # we execute the move

        if self.game.winner:
            embed = discord.Embed(title=f"{self.game.winner.user} WON THE GAME!", color=self.bot.colors['success'])
            embed.set_author(name="WINNER #1 🏆")
            await ctx.send(embed=embed)

        if self.game.draw:
            embed = discord.Embed(title=f"The game ends in a draw!", description='There is no winner in this the game',
                                  color=self.bot.colors['white'])
            embed.set_author(name="DRAW 🫱🏽‍🫲🏻")
            await ctx.send(embed=embed)
            
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
        TASKS
    """

    @tasks.loop(seconds=30)
    async def afk_timer(self):
        now = datetime.datetime.now() - datetime.timedelta(minutes=1)
        if fabs((self.game.creation_datetime - now).total_seconds()) <= 60:
            pass
            # qua metti end game
            # poi devi fare che SIA le lobby che i game possono essere fatti in un SOLO canale alla volta

    """
        FUNCTIONS
    """
    def end_game(self):
        self.game = None
        self.lobby.empty()

