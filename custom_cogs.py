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
        embed = discord.Embed(title="I am online!", color=self.bot.colors['success'])
        await interaction.response.send_message(
            embed=embed
        )


class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game = None
        self.lobby = Lobby()

        self.starting_date = None  # Will store the datetime value of when the game starts. It handles afk players
        self.akf_timer = 120  # seconds
        self.channel = None   # We will store the channel the game is being played in

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
            embed = discord.Embed(title="A game is already running! ",
                                  description="Wait for the game to finish",
                                  color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return

        # If we are in the wrong channel we just exit from the function
        if not self.is_channel_valid(ctx.channel):
            embed = discord.Embed(title="Games can only be played in one channel!",
                                  description="Once you join a lobby in a channel, "
                                              "the game can only be played in that channel. "
                                              f"Lobby is current in this channel: {self.channel.mention}",
                                  color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return

        # ---------------------------------------
        # These lines will be replaced by this line {user = ctx.author} they are only used for developing purposes.
        # Basically they allow you to test games without having to call another person. ( you play versus yourself )
        if id_:
            user = self.bot.get_user(int(id_))
        else:
            user = ctx.author
        # ---------------------------------------

        self.channel = ctx.channel  # Game can only be played in this channel
        embed = discord.Embed(title=f"***{user}*** joined the lobby!", color=self.bot.colors['success'])

        await ctx.send(embed=embed)

        self.lobby.add(
            Player(
                user,
                sign=self.signs[self.lobby.size()]
            )
        )

        # Each time a new lobby is created, a new starting date is stored
        if not self.starting_date:
            self.starting_date = datetime.datetime.now()

        # We start the timer to check afk players directly on lobby joining
        if not self.is_timer.is_running():
            self.is_timer.start()

        # if lobby is not ready just exit
        if not self.lobby.is_ready():
            return

        await self.start_game()

    @commands.command(name="lobby")
    async def lobby(self, ctx):

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

        if not self.lobby.is_user_in_lobby(ctx.author):
            embed = discord.Embed(title="You are not in the current game!",
                                  description="Wait for the current game to finish to join a new one",
                                  color=self.bot.colors['warning'])
            await ctx.send(embed=embed)

        if not self.is_channel_valid(ctx.channel):
            embed = discord.Embed(title="You can only play the game in the channel you started it from!",
                                  description="Channel can be changes only when the game finishes or someone quits."
                                              f"\nLobby is current in this channel: {self.channel.mention}",
                                  color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return

        # Everytime a player moves we can reset the timer
        self.starting_date = datetime.datetime.now()

        # if there is no game started, we can't perform any move
        if not self.game:
            return

        # user can move only if it's his turn
        # ----------------------------------------------------
        # If you find this lines commented is because of testing. Commenting them means that I can play when it's
        # the turn of another player, which is pretty useful when building the program
        if not self.game.is_user_turn(ctx.author):
            embed = discord.Embed(title=f"It's not your turn!", color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return
        # ----------------------------------------------------

        position = int(position) - 1  # we fix the array offset
        self.game.move(position)  # we execute the move

        if self.game.winner:
            embed = discord.Embed(title=f"{self.game.winner.user} WON THE GAME!",
                                  description=f"Congrats both to {self.lobby.get_player(0)} and "
                                              f"{self.lobby.get_player(0)}",
                                  color=self.bot.colors['success'])
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

    @tasks.loop(seconds=40)
    async def is_timer(self):

        # If lobby is empty there is no need to check for afk players
        if not self.lobby:
            return

        now = datetime.datetime.now()
        if int(fabs((self.starting_date - now).total_seconds())) >= self.akf_timer:
            embed = discord.Embed(title="Game has been interrupted due to afk players", description="Join a new lobby!",
                                  color=self.bot.colors['fail'])
            await self.channel.send(embed=embed)
            self.end_game()

    """
        FUNCTIONS
    """
    def end_game(self):
        self.game = None
        self.lobby.empty()
        self.channel = None
        self.is_timer.cancel()

    def is_channel_valid(self, ctx_channel):
        return True if not self.channel or self.channel == ctx_channel else False

    async def start_game(self):
        # We reset timer once the game starts
        self.starting_date = datetime.datetime.now()

        # Actually starting the game
        self.game = TicTacToe(
            self.lobby,
            empty_board=[':one:', ':two:', ':three:', ':four:',
                         ':five:', ':six:', ':seven:', ':eight:', ':nine:']
        )

        # UI stuff to show that the game is starting
        embed = discord.Embed(title=f"{self.game.get_player_turn().user}'s turn",
                              description="These are the rivals!", color=self.bot.colors['success'])
        embed.set_author(name="Game is started")
        embed.set_footer(text="The game can last a maximum of 2 minutes due to bandwidth limitations.")
        players = self.lobby.get_players()
        embed.add_field(name=str(players[0].user), value=players[0].sign, inline=True)
        embed.add_field(name=str(players[1].user), value=players[1].sign, inline=True)

        # We send the messages
        await self.channel.send(embed=embed)
        await self.channel.send(self.game.get_board_formatted_string())

