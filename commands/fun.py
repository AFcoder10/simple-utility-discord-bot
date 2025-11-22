# commands/fun.py
import discord
from discord.ext import commands
from typing import List

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="poll", description="Creates a poll with up to 10 options.")
    async def poll(self, ctx: commands.Context, question: str,
                   option1: str, option2: str, option3: str = None,
                   option4: str = None, option5: str = None, option6: str = None,
                   option7: str = None, option8: str = None, option9: str = None,
                   option10: str = None):
        """Creates a poll with up to 10 options."""
        options = [opt for opt in [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10] if opt is not None]

        # Emojis for reactions
        react_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        description = []
        for i, option in enumerate(options):
            description.append(f"{react_emojis[i]} {option}")

        embed = discord.Embed(
            title=question,
            description="\\n".join(description),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Poll by {ctx.author.display_name}")

        # For prefix commands, we don't want the original command message to be visible.
        # For slash commands, this does nothing, which is fine.
        if ctx.interaction is None:
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass # Ignore if we can't delete the message

        poll_message = await ctx.send(embed=embed)

        for i in range(len(options)):
            await poll_message.add_reaction(react_emojis[i])


async def setup(bot):
    await bot.add_cog(Fun(bot))
