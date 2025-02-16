import nextcord
from nextcord.ext import commands
from nextcord import Embed

class Source(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="source")
    async def source(self, ctx):
        # Replace this with your GitHub repository link
        github_repo_url = "https://github.com/VuryseeDEV/scipio_bot/tree/main"

        # Create the embed
        embed = Embed(
            title="GitHub Repository",
            description="Click the link below to view the source code:",
            color=nextcord.Color.blue()
        )
        embed.add_field(name="Repository", value=f"[Click here to view the source]({github_repo_url})")

        # Send the embed
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Source(bot))