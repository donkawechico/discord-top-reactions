import pdb
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w'),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger()

DEBUG = True  # Set to False to fetch messages from all channels
TEST_CHANNEL_ID = 998002417234878514  # Replace with your actual test channel ID

load_dotenv()

GUILD_ID = discord.Object(id=os.getenv('GUILD_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.emojis_and_stickers = True

class TopReactionsBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/",
            intents=intents
        )
        self.channel_messages = {}  # Dictionary to store messages per channel

    async def fetch_messages(self, channel):
        """Fetch messages for a given channel and store them."""
        try:
            messages = [msg async for msg in channel.history(limit=None)]  # Adjust limit as needed
            self.channel_messages[channel.id] = messages
            logger.info(f"Fetched and cached {len(messages)} messages for {channel.name} (ID: {channel.id})")
        except discord.errors.Forbidden:
            logger.warning(f"Skipping channel {channel.name} (ID: {channel.id}) due to lack of permissions")
        except Exception as e:
            logger.error(f"Error fetching messages for {channel.name} (ID: {channel.id}): {str(e)}")

    async def on_ready(self):
        await self.tree.sync(guild=GUILD_ID)
        logger.info("Bot is ready!")
        logger.info(f"Logged in as {self.user} ({self.user.id})")
        
        # Determine channels to fetch based on DEBUG mode
        if DEBUG:
            channels_to_fetch = [self.get_channel(int(TEST_CHANNEL_ID))]
            
            logger.info(f"DEBUG mode is on. Fetching messages for test channel ID: {TEST_CHANNEL_ID}")
        else:
            channels_to_fetch = await self.get_all_channels()
            logger.info("DEBUG mode is off. Fetching messages for all channels.")

        # Fetch messages for each channel
        for channel in channels_to_fetch:
            if channel:  # Ensure the channel is not None
                await self.fetch_messages(channel)
            else:
                logger.error(f"Channel ID {TEST_CHANNEL_ID} could not be found.")

    async def get_all_channels(self):
        """Return all text channels in the guild."""
        channels = []
        for guild in self.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    channels.append(channel)
        logger.info(f"Retrieved {len(channels)} text channels across all guilds.")
        return channels

    async def setup_hook(self):
        # Load the cog
        await self.load_extension("slash_commands.fetch_reactions")
        logger.info("Loaded extensions and cogs.")

bot = TopReactionsBot()

bot.run(os.getenv('DISCORD_TOKEN'))
