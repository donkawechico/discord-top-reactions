import discord
from discord import app_commands
from discord.ext import commands

MAX_EMBED_DESCRIPTION_LENGTH = 4096
MAX_TOTAL_EMBED_LENGTH = 6000
MAX_EMBEDS_PER_MESSAGE = 10

class EmbedUtils:
    @staticmethod
    def create_embed(description: str, attachments=None) -> discord.Embed:
        """Create and return a Discord Embed with optional attachments."""
        embed = discord.Embed(description=description)
        if attachments:
            embed.set_image(url=attachments[0].url)
        return embed

    @staticmethod
    def add_embed(embeds: list, embed: discord.Embed, current_length: int) -> bool:
        """Attempt to add an embed to the list if it doesn't exceed the total length limit."""
        if current_length + len(embed.description) <= MAX_TOTAL_EMBED_LENGTH:
            embeds.append(embed)
            return True
        return False
