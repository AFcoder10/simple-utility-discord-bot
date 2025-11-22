# commands/help.py
import discord
from discord.ext import commands
from discord.ui import View, Button
from collections import defaultdict

class HelpPaginator(View):
    def __init__(self, embeds):
        super().__init__(timeout=120)
        self.embeds = embeds
        self.current_page = 0
        self._update_buttons()

    def _update_buttons(self):
        # The view children are the buttons.
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page == len(self.embeds) - 1

    async def show_page(self, interaction: discord.Interaction):
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.grey)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        await self.show_page(interaction)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        await self.show_page(interaction)

class Help(commands.Cog):
    """A custom help command cog."""
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Shows this help message.")
    async def help(self, ctx: commands.Context, *, command_name: str = None):
        """Shows detailed help for a command or a paginated list of all commands."""
        if command_name:
            command = self.bot.get_command(command_name)
            if not command or command.hidden:
                await ctx.send(f"Command `{command_name}` not found.", ephemeral=True)
                return
            
            embed = discord.Embed(title=f"Help: `!{command.name}`", description=command.help or "No description provided.", color=discord.Color.blue())
            
            usage = f"!{command.name} {command.signature}"
            embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
            
            if command.aliases:
                embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in command.aliases), inline=False)

            perms = []
            guild_only = False
            for check in command.checks:
                qualname = str(check.__qualname__)
                if "is_owner" in qualname:
                    perms.append("Bot Owner")
                elif "has_permissions" in qualname:
                    perms.append("Server Permissions") # General message
                elif "guild_only" in qualname:
                    guild_only = True
            
            if perms:
                embed.add_field(name="Required Permissions", value=", ".join(perms), inline=False)
            if guild_only:
                embed.set_footer(text="This command can only be used in a server.")

            await ctx.send(embed=embed)
        else:
            # Group commands by cog
            cogs = defaultdict(list)
            for command in self.bot.commands:
                # We only want to show hybrid commands in help, and not hidden ones.
                if isinstance(command, commands.hybrid.HybridAppCommand) and not command.hidden and command.cog_name:
                    cogs[command.cog_name].append(command)
            
            embeds = []
            sorted_cogs = sorted(cogs.keys())

            for cog_name in sorted_cogs:
                cog_commands = cogs[cog_name]
                embed = discord.Embed(title=f"{cog_name} Commands", color=discord.Color.green())
                
                for command in sorted(cog_commands, key=lambda c: c.name):
                    usage = f"!{command.name} {command.signature}"
                    description = command.description or "No description."
                    embed.add_field(name=f"`{command.name}`", value=f"*{description}*\n`Usage: {usage}`", inline=False)
                
                embeds.append(embed)
            
            if not embeds:
                await ctx.send("No commands to show.", ephemeral=True)
                return

            for i, embed in enumerate(embeds):
                embed.set_footer(text=f"Page {i+1}/{len(embeds)}")
            
            paginator = HelpPaginator(embeds)
            await ctx.send(embed=embeds[0], view=paginator)

async def setup(bot):
    await bot.add_cog(Help(bot))
