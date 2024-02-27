import pdb
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

load_dotenv()

GUILD_ID = discord.Object(id=os.getenv('GUILD_ID'))

intents = discord.Intents.default()
intents.message_content=True
intents.emojis_and_stickers=True

class TopReactionsBot(commands.Bot):
    def __init__(self):
        # initialize our bot instance, make sure to pass your intents!
        # for this example, we'll just have everything enabled
        super().__init__(
            command_prefix="/",
            intents=intents
        )

    async def on_ready(self):
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)

        print("Ready!")
        print(f"Logged in as {self.user} ({self.user.id})")
        print("------")

    # the method to override in order to run whatever you need before your bot starts
    async def setup_hook(self):
        await self.load_extension("slash_commands.fetch_reactions")

bot = TopReactionsBot()

bot.run(os.getenv('DISCORD_TOKEN'))