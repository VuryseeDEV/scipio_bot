import nextcord
from nextcord.ext import commands
import time

"""
    May encounter problems with large ping spikes displayed by
    the bot after a certain amount of uptime. Not sure if this
    is a bug or not.. Too lazy to look into it.
"""


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        uptime = time.time() - self.start_time # Calculate bot uptime in seconds
        embed = nextcord.Embed(title="🏓 Pong!", 
                               description=f"Latency: {latency}ms\nUptime: {round(uptime, 2)}s",
                                color=nextcord.Color.red())
        await ctx.send(embed=embed)

def setup(bot):  
    bot.add_cog(Ping(bot))