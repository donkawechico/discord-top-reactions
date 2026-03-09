import re
import discord

# Regional indicator letters (🇦–🇿) used as poll options — excluded from scoring
NEUTRAL_EMOJIS = {chr(c) for c in range(0x1F1E6, 0x1F200)}

# Emojis that count negatively toward a message's score
NEGATIVE_EMOJIS = {"👎", "🤮", "🙅‍♂️", "🤢"}

# Emojis that count with extra weight (by Unicode character or custom emoji name)
STRONG_POSITIVE_EMOJIS = {"🔥", "fuckyes"}
STRONG_POSITIVE_WEIGHT = 1.1

class ReactionProcessor:
    @staticmethod
    def parse_emoji_input(emoji_str: str) -> set:
        """Normalize space-separated user emoji input into a set of matchable names.

        Handles raw unicode (👍), Discord custom format (<:name:id>), and colon format (:name:).
        """
        names = set()
        for token in emoji_str.split():
            match = re.match(r'<a?:(\w+):\d+>', token)
            if match:
                names.add(match.group(1))
            elif token.startswith(':') and token.endswith(':') and len(token) > 2:
                names.add(token[1:-1])
            else:
                names.add(token)
        return names

    @staticmethod
    def get_emoji_name(reaction) -> str:
        """Return a matchable name for an emoji: the character itself for Unicode, or the name for custom."""
        if isinstance(reaction.emoji, str):
            return reaction.emoji
        return reaction.emoji.name if hasattr(reaction.emoji, 'name') else None

    @staticmethod
    def calculate_score(message: discord.Message, only_set: set = None) -> float:
        """Calculate a weighted score for a message.

        - NEGATIVE_EMOJIS subtract from the score.
        - NEUTRAL_EMOJIS are ignored entirely.
        - STRONG_POSITIVE_EMOJIS count at STRONG_POSITIVE_WEIGHT instead of 1.
        - Everything else counts as +1.
        - If only_set is provided, only reactions whose name is in that set are considered.
        """
        score = 0
        for reaction in message.reactions:
            name = ReactionProcessor.get_emoji_name(reaction)
            if only_set and name not in only_set:
                continue
            identifier = ReactionProcessor.get_emoji_str(reaction)
            if identifier in NEGATIVE_EMOJIS:
                score -= reaction.count
            elif identifier in NEUTRAL_EMOJIS:
                pass
            elif name in STRONG_POSITIVE_EMOJIS:
                score += reaction.count * STRONG_POSITIVE_WEIGHT
            else:
                score += reaction.count
        return score

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
