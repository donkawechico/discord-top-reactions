import discord

class ReactionProcessor:
    @staticmethod
    def process_reactions(message: discord.Message) -> str:
        """Process message reactions and return a formatted string."""
        response = ""
        unrenderable_count = 0
        en_space = "\u2002"
        for reaction in message.reactions:
            emoji_str = ReactionProcessor.get_emoji_str(reaction)
            if emoji_str:
                response += f"{emoji_str} {reaction.count}{en_space*2}"
            else:
                unrenderable_count += reaction.count

        if unrenderable_count > 0:
            response += f"⬜ {unrenderable_count}{en_space*2}"

        return response.strip()

    @staticmethod
    def get_emoji_str(reaction) -> str:
        """Return a formatted string for an emoji, or None if it's unrenderable."""
        if isinstance(reaction.emoji, str):
            return reaction.emoji

        emoji = reaction.emoji
        if isinstance(emoji, discord.Emoji) and emoji.available:
            return f"<a:{emoji.name}:{emoji.id}>" if emoji.animated else f"<:{emoji.name}:{emoji.id}>"
        return None
