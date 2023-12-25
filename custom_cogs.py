import datetime
from math import fabs

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Greedy, Range

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
        self.lobbies = {}

        self.afk_timer = 120  # seconds
        self.afk_detection.start()

        self.signs = [
            ':negative_squared_cross_mark:',
            ':o2:'
        ]

    @commands.command(name="join")
    async def join(self, ctx, id_=None):

        lobby = self.get_lobby(ctx.channel.id)

        if lobby.is_user_in_lobby(ctx.author) and not id_:
            embed = discord.Embed(title="You are already in the lobby!",
                                  description="Wait for someone to join you!",
                                  color=self.bot.colors['warning'])
            await ctx.send(embed=embed)
            return

        if lobby.game:
            embed = discord.Embed(title="A game is already running! ",
                                  description="Wait for the game to finish",
                                  color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return

        # Checking that only one lobby is executed in each channel
        if ctx.channel.id in self.lobbies and lobby.is_ready():
            embed = discord.Embed(title="Only one game per channel can be played!", color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return

        # After all checks user can finally be prepared to join the lobby
        # ---------------------------------------
        # These lines will be replaced by this line {user = ctx.author} they are only used for developing purposes.
        # Basically they allow you to test games without having to call another person. ( you play versus yourself )
        if id_:
            user = self.bot.get_user(int(id_))
        else:
            user = ctx.author
        # ---------------------------------------

        lobby.add(
            Player(
                user,
                sign=self.signs[lobby.size()]
            )
        )

        # Print out to let user know that he joined the lobby
        embed = discord.Embed(title=f"***{user}*** joined the lobby! ({str(lobby.size())}/2)",
                              color=self.bot.colors['success'])
        await ctx.send(embed=embed)

        # Saving the lobby paired with channel id
        self.lobbies[ctx.channel.id] = lobby

        # Each time a new lobby is created, a new starting date is stored
        """if not self.starting_date:
            self.starting_date = datetime.datetime.now()"""

        # We start the timer to check afk players directly on lobby joining
        """if not self.is_timer.is_running():
            self.is_timer.start()"""

        # if lobby is not ready just exit
        if not lobby.is_ready():
            return

        # Starting the game
        await self.start_game(ctx.channel, lobby)

    @commands.command(name="lobby")
    async def lobby(self, ctx):

        lobby = self.get_lobby(ctx.channel.id)

        if lobby.is_empty():
            embed = discord.Embed(title="Lobby is empty!",
                                  description="Join a new one.", color=self.bot.colors['warning'])
            await ctx.send(embed=embed)
            return

        players = lobby.get_players()
        embed = discord.Embed(title="Lobby",
                              description="The players currently inside the lobby are as follows!",
                              color=self.bot.colors['white'])
        for i, p in enumerate(players):
            embed.add_field(name=f"Player #{i+1}", value=f"{p.user.name}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="move")
    async def move(self, ctx, position: Range[int, 1, 9]):
        lobby = self.get_lobby(ctx.channel.id)
        game = lobby.game

        if not lobby.is_user_in_lobby(ctx.author):
            embed = discord.Embed(title="You are not in the current game!",
                                  description="Wait for the current game to finish to join a new one",
                                  color=self.bot.colors['warning'])
            await ctx.send(embed=embed)
            return

        # Everytime a player moves we can reset the timer
        # self.starting_date = datetime.datetime.now()

        # if there is no game started, we can't perform any move
        if not game:
            return

        # user can move only if it's his turn
        # ----------------------------------------------------
        # If you find this lines commented is because of testing. Commenting them means that I can play when it's
        # the turn of another player, which is pretty useful when building the program
        """if not game.is_user_turn(ctx.author):
            embed = discord.Embed(title=f"It's not your turn!", color=self.bot.colors['fail'])
            await ctx.send(embed=embed)
            return"""
        # ----------------------------------------------------

        # Deleting the message just before moving. I just don't like it and it clears the chat
        # await ctx.message.delete()

        position = int(position) - 1  # we fix the array offset
        game.move(position)  # we execute the move

        await ctx.send(game.get_board_formatted_string())

        embed = discord.Embed(
            title=f" ‖{game.get_last_player_moved().sign}‖ {game.get_last_player_moved().user} moved △",
            color=self.bot.colors['success']
        )
        await ctx.send(embed=embed)

        if game.end:
            # Canceling the actual game
            self.end_game(ctx.channel.id)

            # Just output
            if game.winner:
                embed = discord.Embed(title=f"{game.winner.user} WON THE GAME!",
                                      description=f"Congrats both to {lobby.get_player(0).user} and "
                                                  f"{lobby.get_player(1).user}",
                                      color=self.bot.colors['success'])
                embed.set_author(name="WINNER #1 🏆")
                await ctx.send(embed=embed)

            elif game.draw:
                embed = discord.Embed(title=f"The game ends in a draw!",
                                      description='There is no winner in this the game',
                                      color=self.bot.colors['white'])
                embed.set_author(name="DRAW 🫱🏽‍🫲🏻")
                await ctx.send(embed=embed)

            return

        # If code reaches this point it means game is still going on

        embed = discord.Embed(
            title=f"‖{game.get_player_turn().sign}‖ {game.get_player_turn().user}'s turn now! ▼",
            color=self.bot.colors['white']
        )
        await ctx.send(embed=embed)

        # game is a local variable. We save to lobby the changes made to the game object
        lobby.update_game(game)

    @commands.command(name="quit")
    async def quit(self, ctx):
        lobby = self.get_lobby(ctx.channel.id)

        # user can quit the lobby only if he is in it
        if lobby.is_user_in_lobby(ctx.author):
            self.end_game(ctx.channel.id)

            embed = discord.Embed(title="You quit the lobby", color=self.bot.colors['success'])
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="You are not in the lobby", color=self.bot.colors['warning'])
            await ctx.send(embed=embed)

    """
        TASKS
    """

    @tasks.loop(seconds=30)
    async def afk_detection(self):

        # If there are no lobbies there is no need to check for afk
        if not self.lobbies:
            return

        now = datetime.datetime.now()
        for channel_id, lobby in dict(self.lobbies).items():
            print(f'[{channel_id}] -> {int(fabs((lobby.updated_time - now).total_seconds()))} >= {self.afk_timer} ???')
            if int(fabs((lobby.updated_time - now).total_seconds())) >= self.afk_timer:
                embed = discord.Embed(title="Game has been interrupted due to afk players",
                                      description="Join a new lobby!",
                                      color=self.bot.colors['fail'])

                self.end_game(channel_id)
                channel = self.bot.get_channel(channel_id)
                await channel.send(embed=embed)




    """
        FUNCTIONS
    """
    def end_game(self, channel_id):
        if channel_id in self.lobbies:
            self.lobbies.pop(channel_id)
        # self.is_timer.cancel()

    async def start_game(self, channel, lobby):

        # Actually starting the game
        game = lobby.start_game()

        # UI stuff to show that the game is starting
        embed = discord.Embed(title=f"{game.get_player_turn().user}'s turn",
                              description="These are the rivals!", color=self.bot.colors['success'])
        embed.set_author(name="Game is started")
        embed.set_footer(text="The game can last a maximum of 2 minutes due to bandwidth limitations. \n"
                              f"Use \"{self.bot.command_prefix}move N\" (without quotes) where N is the number "
                              f"you want to place your sign to. E.g. {self.bot.command_prefix}move 1")
        players = lobby.get_players()
        embed.add_field(name=str(players[0].user), value=players[0].sign, inline=True)
        embed.add_field(name=str(players[1].user), value=players[1].sign, inline=True)

        await channel.send(embed=embed)
        await channel.send(game.get_board_formatted_string())

    def get_lobby(self, channel_id):
        return self.lobbies[channel_id] if channel_id in self.lobbies else Lobby()

