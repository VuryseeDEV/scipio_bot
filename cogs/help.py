import nextcord
from nextcord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cushelp")
    async def help(self, ctx):
        help_message = "**Bot Commands List:**\n"

        # Iterate through all the commands in the bot and list them
        for command in self.bot.commands:
            help_message += f"/{command.name} - {command.help or 'No description available'}\n"

        # Send the help message
        await ctx.send(help_message)

# Set up the cog
def setup(bot):
    bot.add_cog(HelpCommand(bot))