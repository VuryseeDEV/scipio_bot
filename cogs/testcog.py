import nextcord
from nextcord.ext import commands


"""
    Provided by Nextcord Github Repository
"""

class Testcog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command()
    async def my_slash_command(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is a slash command in a cog!")

    @nextcord.user_command()
    async def my_user_command(self, interaction: nextcord.Interaction, member: nextcord.Member):
        await interaction.response.send_message(f"Hello, {member}!")

    @nextcord.message_command()
    async def my_message_command(
        self, interaction: nextcord.Interaction, message: nextcord.Message
    ):
        await interaction.response.send_message(f"{message}")


def setup(bot):
    bot.add_cog(Testcog(bot))