# commands/utility.py
import discord
from discord.ext import commands
import datetime
import time

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.hybrid_command(name="ping", description="Shows the bot's latency.")
    async def ping(self, ctx: commands.Context):
        """Shows the bot's latency."""
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)} ms")

    @commands.hybrid_command(name="uptime", description="Shows how long the bot has been running.")
    async def uptime(self, ctx: commands.Context):
        """Shows how long the bot has been running."""
        current_time = time.time()
        difference = int(round(current_time - self.start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(title="Uptime", description=f"I have been online for {text}", color=discord.Color.blue())
        embed.set_footer(text=f"Last restart: {datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="userinfo", description="Shows a full profile card of a user.")
    @commands.guild_only()
    async def userinfo(self, ctx: commands.Context, *, member: discord.Member = None):
        """Shows a full profile card of a user."""
        member = member or ctx.author

        embed = discord.Embed(title=f"User Info: {member.display_name}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="Username", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Global Name", value=member.global_name, inline=True)
        embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
        
        embed.add_field(name="ID", value=member.id, inline=False)

        account_age = int(member.created_at.timestamp())
        join_date = int(member.joined_at.timestamp())
        embed.add_field(name="Account Created", value=f"<t:{account_age}:F> (<t:{account_age}:R>)", inline=False)
        embed.add_field(name="Joined Server", value=f"<t:{join_date}:F> (<t:{join_date}:R>)", inline=False)
        
        if member.activity:
            activity = member.activity
            activity_str = f"**{activity.type.name.title()}:** {activity.name}"
            if isinstance(activity, discord.Spotify):
                activity_str = f"**Listening to:** {activity.title} by {', '.join(activity.artists)}"
            embed.add_field(name="Activity", value=activity_str, inline=False)

        roles = [role.mention for role in reversed(member.roles) if role.name != "@everyone"]
        if roles:
            embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles), inline=False)

        if member.public_flags.all():
            badges = [flag.name.replace('_', ' ').title() for flag in member.public_flags.all()]
            embed.add_field(name="Badges", value=", ".join(badges), inline=False)

        user = await self.bot.fetch_user(member.id)
        if user.banner:
            embed.set_image(url=user.banner.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", description="Shows information about the server.")
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context):
        """Shows information about the server."""
        guild = ctx.guild

        embed = discord.Embed(title=f"Server Info: {guild.name}", color=discord.Color.blue())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="ID", value=guild.id, inline=True)
        
        creation_ts = int(guild.created_at.timestamp())
        embed.add_field(name="Created On", value=f"<t:{creation_ts}:F> (<t:{creation_ts}:R>)", inline=False)

        embed.add_field(name="Members", value=f"Total: {guild.member_count}", inline=True)
        
        channels = guild.channels
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        embed.add_field(name="Channels", value=f"Total: {len(channels)}\nText: {text_channels}\nVoice: {voice_channels}\nCategories: {categories}", inline=True)

        embed.add_field(name="Emojis & Stickers", value=f"Emojis: {len(guild.emojis)}\nStickers: {len(guild.stickers)}", inline=True)

        if guild.premium_tier > 0:
            embed.add_field(name="Boost Status", value=f"Level {guild.premium_tier} with {guild.premium_subscription_count} boosts", inline=True)

        roles = [role.name for role in reversed(guild.roles) if role.name != "@everyone"]
        role_count = len(roles)
        role_str = ", ".join(roles[:10]) + (f" and {role_count-10} more" if role_count > 10 else "")
        embed.add_field(name=f"Roles ({role_count})", value=role_str if role_str else "None", inline=False)

        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="banner", description="Shows a user's banner.")
    async def banner(self, ctx: commands.Context, *, user: discord.User = None):
        """Shows a user's banner."""
        user = user or ctx.author
        
        user = await self.bot.fetch_user(user.id)

        if user.banner:
            embed = discord.Embed(title=f"{user.name}'s Banner", color=user.accent_color or discord.Color.blue())
            embed.set_image(url=user.banner.url)
            await ctx.send(embed=embed)
        else:
            if user.accent_color:
                embed = discord.Embed(title=f"{user.name}'s Banner", description=f"This user doesn't have a banner, but they have an accent color: `{user.accent_color}`", color=user.accent_color)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{user.name} doesn't have a banner or accent color.")
                
    @commands.hybrid_command(name="avatar", description="Shows a user's avatar(s).")
    async def avatar(self, ctx: commands.Context, *, member: discord.Member = None):
        """Shows a user's avatar(s)."""
        member = member or ctx.author
        
        embed = discord.Embed(title=f"{member.display_name}'s Avatar", description="Showing currently displayed avatar.", color=member.color)
        embed.set_image(url=member.display_avatar.url)
        
        avatar_links = []
        if member.avatar:
            avatar_links.append(f"[Global Avatar]({member.avatar.url})")
        if member.guild_avatar:
            avatar_links.append(f"[Server Avatar]({member.guild_avatar.url})")
        
        if not member.avatar:
             avatar_links.append(f"[Default Avatar]({member.default_avatar.url})")

        embed.add_field(name="Other Avatars", value=" | ".join(avatar_links) if avatar_links else "None")
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="roleinfo", description="Shows information about a role.")
    @commands.guild_only()
    async def roleinfo(self, ctx: commands.Context, *, role: discord.Role):
        """Shows information about a role."""
        embed = discord.Embed(title=f"Role Info: {role.name}", color=role.color)
        
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        
        embed.add_field(name="Members", value=f"{len(role.members)} member(s)", inline=True)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
        embed.add_field(name="Hoisted", value=role.hoist, inline=True)
        
        creation_ts = int(role.created_at.timestamp())
        embed.add_field(name="Created On", value=f"<t:{creation_ts}:F> (<t:{creation_ts}:R>)", inline=False)
        
        permissions = [perm.replace('_', ' ').title() for perm, value in iter(role.permissions) if value]
        if permissions:
            embed.add_field(name="Permissions", value=", ".join(permissions), inline=False)
        else:
            embed.add_field(name="Permissions", value="None", inline=False)
            
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="emoji-info", description="Shows info about a custom emoji.")
    @commands.guild_only()
    async def emoji_info(self, ctx: commands.Context, emoji: discord.Emoji):
        """Shows info about a custom emoji."""
        embed = discord.Embed(title="Emoji Info", color=discord.Color.blue())
        embed.set_thumbnail(url=emoji.url)
        embed.add_field(name="Name", value=emoji.name, inline=True)
        embed.add_field(name="ID", value=emoji.id, inline=True)
        embed.add_field(name="Animated", value=emoji.animated, inline=True)
        
        creation_ts = int(emoji.created_at.timestamp())
        embed.add_field(name="Created At", value=f"<t:{creation_ts}:F> (<t:{creation_ts}:R>)", inline=False)
        
        embed.add_field(name="Server", value=emoji.guild.name, inline=True)
        # emoji.user requires special intents/cache and is not always available.
        
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="inv-info", description="Shows info about an invite link.")
    @commands.guild_only()
    async def inv_info(self, ctx: commands.Context, invite_link: str):
        """Shows info about an invite link."""
        try:
            invite = await self.bot.fetch_invite(invite_link)
        except discord.NotFound:
            await ctx.send("That invite is invalid or has expired.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Invite Info: {invite.code}", color=discord.Color.blue())
        
        if isinstance(invite.guild, discord.Guild):
            embed.add_field(name="Server", value=f"{invite.guild.name} ({invite.guild.id})")
            if invite.guild.icon:
                embed.set_thumbnail(url=invite.guild.icon.url)
        else: # PartialInviteGuild
            embed.add_field(name="Server", value=f"{invite.guild.name}")
            if invite.guild.icon_url:
                embed.set_thumbnail(url=invite.guild.icon_url)

        if invite.channel:
            embed.add_field(name="Channel", value=f"#{invite.channel.name} ({invite.channel.type})")

        if invite.inviter:
            embed.add_field(name="Inviter", value=f"{invite.inviter.name}#{invite.inviter.discriminator}")
        
        if invite.uses is not None:
             embed.add_field(name="Uses", value=f"{invite.uses}/{invite.max_uses if invite.max_uses else '∞'}")

        if invite.expires_at is not None:
            expire_ts = int(invite.expires_at.timestamp())
            embed.add_field(name="Expires At", value=f"<t:{expire_ts}:F> (<t:{expire_ts}:R>)")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
