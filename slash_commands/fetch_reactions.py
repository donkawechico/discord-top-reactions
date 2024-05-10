import pdb
from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
from util.embed_utils import EmbedUtils
from util.reaction_processor import ReactionProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class FetchReactionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_messages(self, channel):
        """Fetch messages for a given channel and store them."""
        if channel.id not in self.bot.channel_messages or self.bot.channel_messages[channel.id] is None:
            self.bot.channel_messages[channel.id] = []  # Initialize as empty to indicate fetch in progress
            try:
                messages = [msg async for msg in channel.history(limit=5000)]
                self.bot.channel_messages[channel.id] = messages
                logger.info(f"Fetched and cached {len(messages)} messages for {channel.name} (ID: {channel.id})")
            except discord.errors.Forbidden:
                logger.warning(f"Skipping channel {channel.name} due to lack of permissions")
                self.bot.channel_messages[channel.id] = None
            except Exception as e:
                logger.error(f"Error fetching messages for {channel.name}: {e}")
                self.bot.channel_messages[channel.id] = None
            return len(messages if self.bot.channel_messages[channel.id] is not None else [])
        return 0

    @app_commands.command(name="top")
    @app_commands.describe(limit="The most recent N messages to consider.",
                           show="The number of top messages to display.")
    async def get_top_reaction_posts(self, interaction: discord.Interaction, limit: int = None, show: int = 5):
        """Fetch top reaction posts in a channel."""
        logger.info(f"Fetching top {show} from {limit} messages in {interaction.channel.name}")
        channel = interaction.channel

        await interaction.response.defer(ephemeral=True)
        initial_message = None

        # Check if messages need to be fetched or are already cached
        if channel.id not in self.bot.channel_messages or self.bot.channel_messages[channel.id] is None:
            logger.info(f"No messages cached for {channel.name}, fetching now...")
            initial_message = await interaction.followup.send("Please wait for a (one-time) fetch and cache of this channel's messages... This can take up to a minute for some channels. This message will update with results once complete. If message never updates, please try again later.", ephemeral=True)  
            message_count = await self.fetch_messages(channel)
            if message_count == 0:
                await initial_message.edit(content="Unable to fetch messages for this channel.")
                return

        messages = self.bot.channel_messages.get(channel.id, [])
        if limit:
            messages = messages[:limit]

        top_posts = sorted(messages, key=lambda msg: sum(reaction.count for reaction in msg.reactions), reverse=True)[:show]

        embeds = [
            EmbedUtils.create_embed(
                f"{msg.content}\n{ReactionProcessor.process_reactions(msg)}\n**[[JUMP]({msg.jump_url})]**",
                msg.attachments
            ) for msg in top_posts
        ]


        if initial_message:
            await initial_message.edit(content="", embeds=embeds)
        else:
            await interaction.followup.send(embeds=embeds, ephemeral=True)

async def setup(bot):
    await bot.add_cog(FetchReactionsCog(bot=bot))
