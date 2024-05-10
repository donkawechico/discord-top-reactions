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

MAX_MESSAGES = 5000

class FetchReactionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_messages(self, channel, interaction=None, initial_message=None):
        """Fetch messages for a given channel and store them with progress logging and optional interaction updates every 10 messages."""
        if channel.id not in self.bot.channel_messages or self.bot.channel_messages[channel.id] is None:
            self.bot.channel_messages[channel.id] = []  # Initialize as empty to indicate fetch in progress
            message_count = 0
            total_messages_fetched = 0
            try:
                # Create an asynchronous iterator to fetch messages
                async for msg in channel.history(limit=MAX_MESSAGES):
                    self.bot.channel_messages[channel.id].append(msg)
                    message_count += 1
                    total_messages_fetched += 1
                    if message_count % 50 == 0:  # Log and optionally update every 10 messages
                        logger.info(f"Fetched {total_messages_fetched} messages so far for {channel.name} (ID: {channel.id})")
                        if interaction and initial_message:
                            await initial_message.edit(content=self.get_progress(total_messages_fetched))
                        
                logger.info(f"Completed fetching and cached {total_messages_fetched} messages for {channel.name} (ID: {channel.id})")
            except discord.errors.Forbidden:
                logger.warning(f"Skipping channel {channel.name} due to lack of permissions")
                self.bot.channel_messages[channel.id] = None
            except Exception as e:
                logger.error(f"Error fetching messages for {channel.name}: {e}")
                self.bot.channel_messages[channel.id] = None

            return total_messages_fetched  # Return the count of messages fetched
        return 0  # Return zero if messages were already fetched


    def get_progress(self, total_messages_fetched):
        """Return a progress string based on the number of messages fetched."""
        return f"Performing one-time history cache. Results will appear here when complete... {total_messages_fetched} messages fetched out of max {MAX_MESSAGES}"

    @app_commands.command(name="top")
    @app_commands.describe(limit="The most recent N messages to consider.", show="The number of top messages to display.")
    async def get_top_reaction_posts(self, interaction: discord.Interaction, limit: int = None, show: int = 5):
        """Fetch top reaction posts in a channel."""
        channel = interaction.channel
        await interaction.response.defer(ephemeral=True)
        
        initial_message = await interaction.followup.send(self.get_progress(0))

        if channel.id not in self.bot.channel_messages or self.bot.channel_messages[channel.id] is None:
            logger.info(f"No messages cached for {channel.name}, fetching now...")
            message_count = await self.fetch_messages(channel, interaction, initial_message)
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
