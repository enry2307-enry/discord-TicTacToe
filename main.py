import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import os
# Custom import
from custom_cogs import GeneralCog, GameCog

# loading environment variables which TOKEN is stored into
load_dotenv()


class Bot(commands.Bot):
    def __init__(self, command_prefix, intents_, self_bot=False):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents_, self_bot=self_bot)
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

    """ This method is called when any user sends a message """
    async def on_message(self, message):
        await self.process_commands(message)  # This functions checks if the message sent by user is a command


""" Intents declaration """
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

TOKEN = os.getenv('TOKEN')

bot = Bot(command_prefix="!", intents_=intents)
bot.run(TOKEN)

# invite link
# https://discord.com/api/oauth2/authorize?client_id=APPLICATION_ID&permissions=0&scope=bot%20applications.commands
