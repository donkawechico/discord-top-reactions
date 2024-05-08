
import discord
from discord import app_commands
from discord.ext import commands
from discord.interactions import Interaction
from util.embed_utils import EmbedUtils, MAX_EMBEDS_PER_MESSAGE, MAX_EMBED_DESCRIPTION_LENGTH
from util.reaction_processor import ReactionProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

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

    @app_commands.command(name="top")
    async def get_top_reaction_posts(self, interaction: discord.Interaction, limit: int = None, show: int = 5):
        logger.info(f"Fetching top {show} from {limit} messages in {interaction.channel.name}")

        channel = interaction.channel
        try:
            # Use cached messages if available
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
                    break  # Stop if adding another embed would exceed the total length limit
                total_embed_length += len(embed.description)

            if len(top_posts) > len(embeds):
                remaining_messages = top_posts[len(embeds):]
                summary_str = FetchReactionsCog.summarize_messages(remaining_messages)
                summary_embed = EmbedUtils.create_embed(summary_str)
                EmbedUtils.add_embed(embeds, summary_embed, total_embed_length)

            await interaction.response.send_message(embeds=embeds, ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to process top reactions: {e}")
            await interaction.response.send_message("Failed to process your request.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(FetchReactionsCog(bot=bot))