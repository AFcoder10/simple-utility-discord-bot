# commands/security.py
import discord
from discord.ext import commands
import aiohttp
import re

class Security(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="whois", description="Looks up information about an IP address.")
    async def whois(self, ctx: commands.Context, ip_address: str):
        """Looks up information about an IP address."""
        # Basic validation for IP address
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address):
            await ctx.send("Invalid input. Please provide a valid IP address.", ephemeral=True)
            return

        # IP Lookup using ip-api.com
        url = f"http://ip-api.com/json/{ip_address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send("Failed to look up IP address.", ephemeral=True)
                    return
                data = await response.json()
                if data["status"] == "fail":
                    await ctx.send(f"Error: {data['message']}", ephemeral=True)
                    return
                
                embed = discord.Embed(title=f"IP Info: {data.get('query', 'N/A')}", color=discord.Color.orange())
                embed.add_field(name="Country", value=f"{data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})")
                embed.add_field(name="Region", value=f"{data.get('regionName', 'N/A')} ({data.get('region', 'N/A')})")
                embed.add_field(name="City", value=data.get('city', 'N/A'))
                embed.add_field(name="ZIP Code", value=data.get('zip', 'N/A'))
                embed.add_field(name="ISP", value=data.get('isp', 'N/A'))
                embed.add_field(name="Organization", value=data.get('org', 'N/A'))
                embed.add_field(name="AS", value=data.get('as', 'N/A'))
                embed.add_field(name="Latitude", value=data.get('lat', 'N/A'))
                embed.add_field(name="Longitude", value=data.get('lon', 'N/A'))
                
                await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Security(bot))