# bot.py
import os
import datetime
from typing import Dict, Optional

from dotenv import load_dotenv

import discord
from discord.ext import commands

from aiohttp import web
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ---------- DISCORD BOT SETUP ----------

intents = discord.Intents.default()
intents.members = True        # server members intent
intents.presences = True      # presence intent
intents.message_content = True  # optional, for commands

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

_web_started = False

# Cache banners so we don't spam fetch_user every 7s
user_banner_cache: Dict[int, Optional[str]] = {}


async def get_banner_url(member: discord.Member) -> Optional[str]:
    """
    Try to get banner URL, with caching per user.
    """
    if member.id in user_banner_cache:
        return user_banner_cache[member.id]

    banner_url = None
    try:
        full_user = await bot.fetch_user(member.id)
        if full_user.banner:
            banner_url = str(full_user.banner.url)
    except Exception:
        banner_url = None

    user_banner_cache[member.id] = banner_url
    return banner_url


def serialize_activity(activity: discord.Activity):
    """
    Serialize a Discord activity object to a dictionary, including all details.
    """
    if not activity:
        return None

    # Base data
    data = {
        "type": activity.type.name if hasattr(activity.type, 'name') else str(activity.type),
        "name": getattr(activity, "name", None),
    }

    # Timestamps for activities that support it
    if hasattr(activity, "start") and activity.start:
        if "timestamps" not in data:
            data["timestamps"] = {}
        data["timestamps"]["start"] = activity.start.isoformat()
    if hasattr(activity, "end") and activity.end:
        if "timestamps" not in data:
            data["timestamps"] = {}
        data["timestamps"]["end"] = activity.end.isoformat()

    # Generic details
    if hasattr(activity, "details"):
        data["details"] = activity.details
    if hasattr(activity, "state"):
        data["state"] = activity.state

    # Activity-specific fields
    if isinstance(activity, discord.CustomActivity):
        if activity.emoji:
            # Handle both unicode and custom emojis
            if activity.emoji.is_custom_emoji():
                data["emoji"] = {"name": activity.emoji.name, "url": str(activity.emoji.url), "id": str(activity.emoji.id)}
            else:
                data["emoji"] = {"name": str(activity.emoji)}
    elif isinstance(activity, discord.Game):
        pass  # Covered by generic fields
    elif isinstance(activity, discord.StreamingActivity):
        data.update({
            "platform": getattr(activity, "platform", None),
            "url": getattr(activity, "url", None),
        })
    elif isinstance(activity, discord.Spotify):
        data.update({
            "title": activity.title,
            "artists": activity.artists,
            "album": activity.album,
            "album_cover_url": activity.album_cover_url,
            "track_id": activity.track_id,
            "duration": activity.duration.total_seconds() if activity.duration else None,
        })

    # Assets
    if hasattr(activity, "assets"):
        assets = {}
        if activity.large_image_url:
            assets["large_image_url"] = str(activity.large_image_url)
        if activity.large_image_text:
            assets["large_image_text"] = activity.large_image_text
        if activity.small_image_url:
            assets["small_image_url"] = str(activity.small_image_url)
        if activity.small_image_text:
            assets["small_image_text"] = activity.small_image_text
        if assets:
            data["assets"] = assets
    
    # Party info
    if hasattr(activity, "party") and activity.party and activity.party.get("id"):
        data["party"] = {"id": activity.party.get("id"), "size": activity.party.get("size")}


    return {k: v for k, v in data.items() if v is not None}


async def build_snapshot():
    """
    Build a live snapshot of all guilds and members.
    Called on each API request.
    """
    now = datetime.datetime.utcnow().isoformat() + "Z"
    result = {
        "generated_at": now,
        "guilds": []
    }

    for guild in bot.guilds:
        guild_data = {
            "id": str(guild.id),
            "name": guild.name,
            "icon_url": guild.icon.url if guild.icon else None,
            "member_count": guild.member_count or len(guild.members),
            "members": []
        }

        for member in guild.members:
            # underlying user object
            user = member._user if hasattr(member, "_user") else member

            # avatar
            avatar_url = str(member.display_avatar.url) if member.display_avatar else None

            # banner via cache
            banner_url = await get_banner_url(member)

            # badges via public_flags
            badges = []
            try:
                if getattr(user, "public_flags", None):
                    badges = [flag.name for flag in user.public_flags.all()]
            except Exception:
                badges = []

            # status
            status = str(member.status) if hasattr(member, "status") else "offline"

            # activities as structured list
            activities = []
            try:
                for activity in member.activities or []:
                    serialized = serialize_activity(activity)
                    if serialized:
                        activities.append(serialized)
            except Exception:
                pass

            # roles (skip @everyone)
            roles = [
                {
                    "id": str(role.id),
                    "name": role.name,
                    "color": role.color.value if role.color.value != 0 else None,
                    "position": role.position,
                }
                for role in member.roles
                if not role.is_default()
            ]
            roles.sort(key=lambda r: r["position"], reverse=True)

            member_obj = {
                "id": str(member.id),
                "name": user.name,
                "discriminator": user.discriminator,
                "global_name": getattr(user, "global_name", None),
                "display_name": member.display_name,
                "nick": member.nick,
                "avatar_url": avatar_url,
                "banner_url": banner_url,
                "accent_color": user.accent_color.value if getattr(user, "accent_color", None) else None,
                "badges": badges,
                "status": status,
                "activities": activities,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "roles": roles,
            }

            guild_data["members"].append(member_obj)

        guild_data["members"].sort(
            key=lambda m: (m["display_name"] or m["name"] or "").lower()
        )
        result["guilds"].append(guild_data)

    result["guilds"].sort(key=lambda g: g["name"].lower())
    return result


# ---------- AIOHTTP API WITH CORS ----------

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


async def snapshot_handler(request: web.Request):
    snapshot = await build_snapshot()
    return web.json_response(snapshot, headers=cors_headers())


async def options_handler(request: web.Request):
    return web.Response(status=200, headers=cors_headers())


async def start_web_app():
    """
    Start aiohttp web server on port 5005.
    """
    app = web.Application()
    app.router.add_route("GET", "/api/snapshot", snapshot_handler)
    app.router.add_route("OPTIONS", "/api/snapshot", options_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5005)
    await site.start()

    print("🌐 REST API running at http://127.0.0.1:5005/api/snapshot")


async def load_cogs():
    for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'commands')):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f"✅ Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load cog {filename}: {e}")

@bot.event
async def on_ready():
    global _web_started
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    
    # Chunk members so cache is filled
    for guild in bot.guilds:
        try:
            print(f"🔄 Chunking guild: {guild.name}")
            await guild.chunk()
        except Exception as e:
            print(f"Failed to chunk {guild.name}: {e}")

    if not _web_started:
        _web_started = True
        bot.loop.create_task(start_web_app())

    # Sync slash commands after cogs are loaded and bot is ready
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")


async def main():
    async with bot:
        await load_cogs()
        if not TOKEN:
            raise SystemExit("DISCORD_TOKEN not found in .env")
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

