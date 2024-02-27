import discord
from discord import app_commands
from discord.ext import commands
from discord.interactions import Interaction

class FetchReactionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    def process_reactions(self, message):
        response = ""
        unrenderable_count = 0
        en_space = "\u2002"
        for reaction in message.reactions:
            if isinstance(reaction.emoji, str):
                emoji_str = reaction.emoji
            else:
                emoji = reaction.emoji
                if isinstance(emoji, discord.Emoji) and emoji.available:
                    emoji_str = f"<a:{emoji.name}:{emoji.id}>" if emoji.animated else f"<:{emoji.name}:{emoji.id}>"
                else:
                    unrenderable_count += reaction.count
                    continue

            response += f"{emoji_str} {reaction.count}{en_space*2}"

        if unrenderable_count > 0:
            response += f"⬜ {unrenderable_count}{en_space*2}"

        return response.strip()

    def get_jump_str(self, message):
        return f"**[[JUMP]({message.jump_url})]**"

    def summarize_messages(self, messages, total_embed_length):
        MAX_DESCRIPTION_LENGTH = 4096
        summary_str = ""
        for msg in messages:
            content_preview = (msg.content[:10] + "...") if len(msg.content) > 10 else msg.content
            reactions_str = self.process_reactions(msg)
            message_summary = f"{self.get_jump_str(msg)} {content_preview} {reactions_str}\n"
            
            if len(summary_str) + len(message_summary) > MAX_DESCRIPTION_LENGTH:
                break  # Stop adding more messages if we're going to exceed the limit

            if total_embed_length + len(summary_str) + len(message_summary) > 6000:
                print(f"We're going to exceed the limit at {total_embed_length + len(summary_str)}")
                # print(f"Total embed length before summary: {total_embed_length}")
                return summary_str
            
            summary_str += message_summary

        return summary_str

    def add_embed(self, embeds, embed, total_embed_length):
        if total_embed_length + len(embed.description) > 6000:
            return False
        embeds.append(embed)
    
    @app_commands.command(name="top")
    async def get_top_reaction_posts(self, interaction: Interaction, limit: int = None, show: int = 5):
        channel = interaction.channel
        history = [msg async for msg in channel.history(limit=limit, oldest_first=False)]
        top_posts = sorted(history, key=lambda msg: sum(reaction.count for reaction in msg.reactions), reverse=True)[:show]
        total_embed_length = 0
        embeds = []
        for msg in top_posts:
            reactions_str = self.process_reactions(msg)
            attachment_note = ""
            
            if len(embeds) < 9:  # Process normally for the first 9 embeds
                content_str = f"{msg.content}\n{reactions_str}\n{self.get_jump_str(msg)}"
                total_embed_length += len(content_str)
                embed = discord.Embed(description=content_str)
                if msg.attachments:
                    attachment_count = len(msg.attachments)
                    attachment_note = f" ({attachment_count} attachments)" if attachment_count > 0 else ""
                    embed.set_image(url=msg.attachments[0].url)  # Use the first attachment as the embed image

                self.add_embed(embeds, embed, total_embed_length)
            else:
                break  # Stop adding more embeds to avoid exceeding the limit

        # Summarize remaining messages if there are any
        remaining_messages = top_posts[len(embeds):]
        if remaining_messages:
            summary_str = self.summarize_messages(remaining_messages, total_embed_length)
            total_embed_length += len(summary_str)
            embed = discord.Embed(description=summary_str)
            # self.add_embed(embeds, embed, total_embed_length)
            embeds.append(embed)
        
        await interaction.response.send_message(embeds=embeds[:10], ephemeral=True)  # Ensure only up to 10 embeds are sent

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(FetchReactionsCog(bot=bot))
