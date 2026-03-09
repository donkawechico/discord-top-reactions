# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

A Python Discord bot that finds and displays the most-reacted-to messages in a channel via the `/top` slash command. Deployed via Docker.

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in: DISCORD_TOKEN, GUILD_ID, CLIENT_ID, ENV (dev or prod)

# Run locally
python main.py
```

## Docker Deployment

```bash
# Build image
docker build -t top-reactions-bot .

# Run with auto-restart
docker run -d --env-file .env --restart unless-stopped top-reactions-bot

# View logs
docker logs <container_id>
```

## Architecture

**`main.py`** — `TopReactionsBot(commands.Bot)` with two responsibilities:
1. **Message cache** (`channel_messages` dict): populated on startup and kept current via event handlers (`on_message`, `on_raw_message_edit`, `on_raw_reaction_add/remove`). The cache avoids redundant API calls when `/top` runs.
2. **Extension loader**: loads `slash_commands/fetch_reactions` and `slash_commands/admin` cogs on startup.

**`slash_commands/fetch_reactions.py`** — Core feature. The `/top` command fetches up to 5000 messages, sorts by total reaction count, then builds Discord embeds respecting the API limits (10 embeds max, 6000 chars total, 4096 per description). Progress updates are sent every 50 messages during fetching.

**`slash_commands/admin.py`** — Owner-only `/sync` command for manually syncing slash commands to Discord's API (bypassed on restart intentionally).

**`util/reaction_processor.py`** — Formats emoji reactions, handles Unicode and Discord custom/animated emojis, and counts unrenderable ones (shown as ⬜).

**`util/embed_utils.py`** — Creates embeds and enforces Discord size limits.

**`config.py`** — Switches between `DevelopmentConfig` (DEBUG=True) and `ProductionConfig` based on `ENV` env var.

**`logger.py`** — Rotating file logger (`log.txt`, 5MB max, 1 backup). Use `log_info()`, `log_error()`, `log_warning()`, `log_debug()`.

## Key Constraints

- Discord embed limits: max 10 embeds per message, 6000 total chars, 4096 chars per description — enforced in `embed_utils.py`
- Message history limit: 5000 messages max per `/top` invocation
- Slash command syncing is intentionally manual (owner-only `/sync`) to avoid auto-sync overhead on every restart
