# commands/moderation.py
import discord
from discord.ext import commands
from typing import Dict, Optional

# In-memory storage for snipe and afk. For a real bot, a database would be better.
afk_users: Dict[int, str] = {}
last_deleted_message: Dict[int, discord.Message] = {}

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.author.bot:
            last_deleted_message[message.channel.id] = message

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Handle AFK status checks before processing commands to avoid race conditions.
        
        # Un-AFK logic: Remove AFK status if the user sends a message.
        if message.author.id in afk_users:
            del afk_users[message.author.id]
            # To avoid spam, only send the "welcome back" message if it's not a command.
            ctx = await self.bot.get_context(message)
            if not ctx.valid:
                await message.channel.send(f"Welcome back {message.author.mention}! I've removed your AFK status.", delete_after=5)

        # AFK mention check: Notify if an AFK user is mentioned.
        if message.mentions:
            for mention in message.mentions:
                if mention.id in afk_users:
                    await message.reply(f"{mention.display_name} is currently AFK: {afk_users[mention.id]}", delete_after=10)
                    # Break after the first AFK user found to prevent spamming the channel
                    break
        
        # Now, process commands
        await self.bot.process_commands(message)


    @commands.hybrid_command(name="snipe", description="Shows the last deleted message in this channel.")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx: commands.Context):
        """Shows the last deleted message in this channel."""
        if ctx.channel.id in last_deleted_message:
            msg = last_deleted_message[ctx.channel.id]
            embed = discord.Embed(description=msg.content, color=msg.author.color, timestamp=msg.created_at)
            embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar.url if msg.author.avatar else msg.author.default_avatar.url)
            embed.set_footer(text=f"Deleted in #{msg.channel.name}")
            if msg.attachments:
                embed.set_image(url=msg.attachments[0].url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("There is no message to snipe.", ephemeral=True)

    @commands.hybrid_command(name="clean", description="Deletes a number of messages.")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx: commands.Context, amount: int, user: Optional[discord.Member] = None):
        """Deletes a number of messages. Can be filtered by user."""
        await ctx.defer(ephemeral=True)
        
        def check(message):
            if user is None:
                return True
            return message.author == user

        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(f"Deleted {len(deleted)} message(s).", delete_after=5)

    @commands.hybrid_command(name="afk", description="Sets a custom AFK message.")
    @commands.guild_only()
    async def afk(self, ctx: commands.Context, *, message: str = "AFK"):
        """Sets a custom AFK message."""
        afk_users[ctx.author.id] = message
        await ctx.send(f"I've set your AFK status: {message}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Moderation(bot))