import pdb
import os
from typing import Literal, Optional
import discord
from dotenv import load_dotenv
from discord.ext import commands
import logging
from slash_commands.admin import sync

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w'),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger()

load_dotenv()

GUILD_ID = os.getenv('GUILD_ID')
GUILD = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
intents.message_content=True
intents.emojis_and_stickers=True

class TopReactionsBot(commands.Bot):
    def __init__(self):
        # initialize our bot instance, make sure to pass your intents!
        # for this example, we'll just have everything enabled
        super().__init__(
            command_prefix="!",
            intents=intents
        )

        self.channel_messages = {}

    async def setup_hook(self):
        await self.load_extension("slash_commands.fetch_reactions")

        logger.info("Loaded extensions and cogs.")

    async def get_all_channels(self):
        """Return all text channels in the guild."""
        channels = []
        guild = self.get_guild(int(GUILD_ID))

        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                channels.append(channel)
        logger.info(f"Retrieved {len(channels)} text channels across all guilds.")
        return channels

    async def update_cache(self, message: discord.Message):
        """Update the message cache when a message is created, edited, or deleted."""
        if self.channel_messages.get(message.channel.id) is not None:
            logger.info(f"Message event in {message.channel.name} (ID: {message.channel.id})")
            await self.fetch_and_update_cache(message.channel, message.id)

    async def update_cache_raw_message(self, payload: discord.RawMessageUpdateEvent):
        """Update the message cache when a message is edited."""
        channel = self.get_channel(payload.channel_id)
        if channel and self.channel_messages.get(channel.id) is not None:
            logger.info(f"Message edit event in {channel.name} (ID: {channel.id})")
            await self.fetch_and_update_cache(channel, payload.message_id)

    async def update_cache_reaction(self, payload: discord.RawReactionActionEvent):
        """Update the message cache when a reaction is added or removed."""
        channel = self.get_channel(payload.channel_id)
        if channel and self.channel_messages.get(channel.id) is not None:
            logger.info(f"Reaction event in {channel.name} (ID: {channel.id})")
            await self.fetch_and_update_cache(channel, payload.message_id)

    async def fetch_and_update_cache(self, channel, message_id):
        """Fetches a message by ID and updates or adds it to the cache."""
        if not isinstance(channel, discord.TextChannel):
            return

        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            logger.warning(f"Message {message_id} was not found in {channel.name} (ID: {channel.id}).")
            return None
        except discord.HTTPException as e:
            logger.error(f"Failed to fetch message {message_id} in {channel.name} (ID: {channel.id}): {str(e)}")
            return None

        messages = self.channel_messages.get(channel.id, [])
        existing_message_index = next((i for i, msg in enumerate(messages) if msg.id == message.id), None)

        if existing_message_index is not None:
            messages[existing_message_index] = message
            logger.info(f"Updated message {message.id} in cache for {channel.name} (ID: {channel.id})")
        else:
            messages.append(message)
            logger.info(f"Added message {message.id} to cache for {channel.name} (ID: {channel.id})")

        self.channel_messages[channel.id] = messages
        return message

    # Also update the cache when a new message is created
    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot
        if message.author == self.user:
            return
        
        logger.info(f"New message {message.id} in channel {message.channel.id}")
        await self.update_cache(message)
        await self.process_commands(message)
        
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        if payload.cached_message:
            if payload.cached_message.author == self.user:
                return
            
        logger.info(f"Message edit event in {payload.channel_id}")
        await self.update_cache_raw_message(payload)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        logger.info(f"Reaction add event in {payload.channel_id}")
        await self.update_cache_reaction(payload)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        logger.info(f"Reaction remove event in {payload.channel_id}")
        await self.update_cache_reaction(payload)

    async def on_ready(self):
        # Don't sync commands every time the bot restarts
        # Uncomment this block (once) to sync commands then comment it out again
        #
        # self.tree.copy_global_to(guild=GUILD)
        # await self.tree.sync(guild=GUILD)
        
        print("Ready!")
        print(f"Logged in as {self.user} ({self.user.id})")
        print("------")
        logger.info("Bot is ready and waiting for commands.")

bot = TopReactionsBot()
bot.add_command(sync)

bot.run(os.getenv('DISCORD_TOKEN'))
