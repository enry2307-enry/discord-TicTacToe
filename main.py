import discord
from discord.ext import commands
from datetime import datetime

# from typing import Literal, Optional # may be useful

from custom_cogs import GeneralCog, GameCog # for the custom cogs

from tictactoe import TicTacToe # that's my class to manage the game

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

""" Extending bot's class """
class Bot(commands.Bot):
        def __init__(self, command_prefix, intents, self_bot=False):
            commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents, self_bot=self_bot)
            self.colors = {
                'white': 0xffffff,
                'success': 0x4dff00,
                'fail': 0xff0000,
                'warning': 0xffdd00
            }

        """ Overriding this method allows to add cogs """
        async def setup_hook(self):
            await self.add_cog(GeneralCog(self))
            await self.add_cog(GameCog(self))

        """ This method is called when the bot is ready """
        async def on_ready(self):
            print(f'Bot is online - {datetime.today().strftime("Date %Y-%m-%d | Time %H:%M:%S ( Server Datetime ) ")}')
            TicTacToe(1, 2)

        """ This method is called when any user sends a message """
        async def on_message(self, message):
            await self.process_commands(message)

bot = Bot(command_prefix="!", intents=intents)
bot.run("MTEzMTEzNDE5ODM1NTMzNzIyNg.GqDR3u.l3cdzlr1kpvfuCv_MqHdjoLYtV8xgu3gLXiZYA")

# MTEzMTEzNDE5ODM1NTMzNzIyNg.GqDR3u.l3cdzlr1kpvfuCv_MqHdjoLYtV8xgu3gLXiZYA # this token is for my test bot

# invite link
# https://discord.com/api/oauth2/authorize?client_id=PUBLIC_KEY&permissions=0&scope=bot%20applications.commands