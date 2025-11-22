# commands/tools.py
import discord
from discord.ext import commands
import asyncio
import aiohttp
import re
import math

# Safe-ish calculator
# A better solution is a dedicated library like 'asteval' or 'simpleeval'
# but this avoids adding new dependencies.
# This is still potentially unsafe and should be used with caution.
ALLOWED_NAMES = {
    k: v for k, v in math.__dict__.items() if not k.startswith("__")
}
ALLOWED_NAMES.update({
    "abs": abs,
    "max": max,
    "min": min,
    "pow": pow,
    "round": round,
})

def safe_eval(expr):
    # A bit safer eval
    # This is not perfectly safe. A dedicated library is recommended for production.
    if not re.match(r"^[0-9+\-*/().\s,a-zA-Z_]+$", expr):
        raise ValueError("Invalid characters in expression.")
    
    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in ALLOWED_NAMES:
            raise NameError(f"Use of '{name}' is not allowed.")

    return eval(code, {"__builtins__": {}}, ALLOWED_NAMES)


class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="remind", description="Sets a reminder.")
    async def remind(self, ctx: commands.Context, duration: str, *, text: str):
        """Sets a reminder. Duration format: 1d, 5h, 10m, 30s"""
        duration_regex = re.compile(r'(\d+)([dhms])')
        matches = duration_regex.findall(duration.lower())
        if not matches:
            await ctx.send("Invalid duration format. Use formats like `2d`, `4h`, `10m`, `30s`.", ephemeral=True)
            return

        seconds = 0
        for value, unit in matches:
            value = int(value)
            if unit == 'd':
                seconds += value * 86400
            elif unit == 'h':
                seconds += value * 3600
            elif unit == 'm':
                seconds += value * 60
            elif unit == 's':
                seconds += value
        
        if seconds <= 0:
            await ctx.send("Duration must be a positive amount of time.", ephemeral=True)
            return

        await ctx.send(f"Okay, I will remind you in `{duration}` about: `{text}`", ephemeral=True)
        await asyncio.sleep(seconds)
        try:
            await ctx.author.send(f"**Reminder:** {text}")
        except discord.Forbidden:
            # If user has DMs closed
            await ctx.channel.send(f"Hey {ctx.author.mention}, here is your reminder: **{text}**")


    @commands.hybrid_command(name="shorten", description="Shortens a URL using TinyURL.")
    async def shorten(self, ctx: commands.Context, url: str):
        """Shortens a URL using TinyURL."""
        api_url = f"http://tinyurl.com/api-create.php?url={url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    short_url = await response.text()
                    await ctx.send(f"Shortened URL: {short_url}")
                else:
                    await ctx.send("Failed to shorten URL.", ephemeral=True)

    @commands.hybrid_command(name="calc", description="Calculates a math expression.")
    async def calc(self, ctx: commands.Context, *, expression: str):
        """Calculates a math expression."""
        try:
            result = safe_eval(expression)
            await ctx.send(f"Result: `{result}`")
        except Exception as e:
            await ctx.send(f"Error: `{e}`", ephemeral=True)

    @commands.hybrid_command(name="quote", description="Quotes a message by its link.")
    @commands.guild_only()
    async def quote(self, ctx: commands.Context, message_link: str):
        """Quotes a message by its link."""
        match = re.match(r"https://discord.com/channels/(\d+)/(\d+)/(\d+)", message_link)
        if not match:
            await ctx.send("Invalid message link.", ephemeral=True)
            return

        guild_id, channel_id, message_id = map(int, match.groups())
        
        if guild_id != ctx.guild.id:
            await ctx.send("I can only quote messages from this server.", ephemeral=True)
            return

        channel = self.bot.get_channel(channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            await ctx.send("I can't find that channel.", ephemeral=True)
            return

        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("I couldn't find that message.", ephemeral=True)
            return
        except discord.Forbidden:
            await ctx.send("I don't have permission to read messages in that channel.", ephemeral=True)
            return

        embed = discord.Embed(
            description=message.content,
            color=message.author.color,
            timestamp=message.created_at
        )
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url, url=message_link)
        embed.set_footer(text=f"in #{channel.name}")

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Tools(bot))
