import discord
from discord import app_commands
from discord.ext import commands
from util.embed_utils import EmbedUtils
from util.reaction_processor import ReactionProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

MAX_MESSAGES = 5000
MAX_EMBEDS_PER_MESSAGE = 10
MAX_EMBED_DESCRIPTION_LENGTH = 6000

class FetchReactionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def summarize_messages(messages: list) -> str:
        """Summarize messages to fit within an embed description."""
        summary_str = ""
        for msg in messages:
            content_preview = (msg.content[:75] + "...") if len(msg.content) > 75 else msg.content
            reactions_str = ReactionProcessor.process_reactions(msg)
            message_summary = f"* {content_preview} {reactions_str} **[[JUMP]({msg.jump_url})]**\n"
            
            if len(summary_str) + len(message_summary) > MAX_EMBED_DESCRIPTION_LENGTH:
                break  # Stop adding more messages if we're going to exceed the embed description limit

            summary_str += message_summary

        return summary_str

    async def fetch_messages(self, channel, interaction=None, initial_message=None):
        """Fetch messages for a given channel and store them with progress logging and optional interaction updates."""
        if channel.id not in self.bot.channel_messages or self.bot.channel_messages[channel.id] is None:
            self.bot.channel_messages[channel.id] = []
            message_count = 0
            total_messages_fetched = 0
            try:
                async for msg in channel.history(limit=MAX_MESSAGES):
                    self.bot.channel_messages[channel.id].append(msg)
                    message_count += 1
                    total_messages_fetched += 1
                    if message_count % 50 == 0:
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

            return total_messages_fetched

    def get_progress(self, total_messages_fetched):
        return f"Performing one-time history cache. Results will appear here when complete... {total_messages_fetched} messages fetched out of max {MAX_MESSAGES}"

    @app_commands.command(name="top")
    @app_commands.describe(limit="The most recent N messages to consider.", show="The number of top messages to display.")
    async def get_top_reaction_posts(self, interaction: discord.Interaction, limit: int = None, show: int = 5):
        """Fetch top reaction posts in a channel."""
        # Show message in docker logs
        logger.info(f"Fetching top {show} from {limit} messages in {interaction.channel.name}")

        channel = interaction.channel
        await interaction.response.defer(ephemeral=True)
        
        initial_message = await interaction.followup.send(self.get_progress(0))

        if channel.id not in self.bot.channel_messages or self.bot.channel_messages[channel.id] is None:
            message_count = await self.fetch_messages(channel, interaction, initial_message)
            if message_count == 0:
                await initial_message.edit(content="Unable to fetch messages for this channel.")
                return

        messages = self.bot.channel_messages.get(channel.id, [])
        if limit:
            messages = messages[:limit]

        top_posts = sorted(messages, key=lambda msg: sum(reaction.count for reaction in msg.reactions), reverse=True)[:show]
        
        embeds, total_embed_length = [], 0
        for msg in top_posts[:MAX_EMBEDS_PER_MESSAGE - 1]:  # Reserve one spot for summary if needed
            reactions_str = ReactionProcessor.process_reactions(msg)
            content_str = f"{msg.content}\n{reactions_str}\n**[[JUMP]({msg.jump_url})]**"
            embed = EmbedUtils.create_embed(content_str, msg.attachments)
            
            if not EmbedUtils.add_embed(embeds, embed, total_embed_length):
                break # Stop if adding another embed would exceed the total length limit
            total_embed_length += len(embed.description)

        # Add a summary embed if there are messages left
        if len(top_posts) > len(embeds):
            remaining_messages = top_posts[len(embeds):]
            summary_str = FetchReactionsCog.summarize_messages(remaining_messages)
            summary_embed = EmbedUtils.create_embed(summary_str)
            EmbedUtils.add_embed(embeds, summary_embed, total_embed_length)

        if initial_message:
            await initial_message.edit(content="", embeds=embeds)
        else:
            await interaction.followup.send(embeds=embeds, ephemeral=True)

async def setup(bot):
    await bot.add_cog(FetchReactionsCog(bot=bot))
