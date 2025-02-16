import nextcord
from nextcord.ext import commands
import random

class RandomNumberGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="numgen", description="Generate random numbers.")
    async def numgen(self, interaction: nextcord.Interaction, min_num: int, max_num: int, generations: int):
        # Generate the random numbers
        numbers = [random.randint(min_num, max_num) for _ in range(generations)]
        
        # Prepare the response
        response = f"Generated {generations} random number(s) between {min_num} and {max_num}:\n"
        response += '\n'.join(str(num) for num in numbers)

        # Send the result as a message
        await interaction.response.send_message(response)

def setup(bot):
    bot.add_cog(RandomNumberGenerator(bot))