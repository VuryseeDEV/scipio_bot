import nextcord
import random
from nextcord import Interaction, Embed, ButtonStyle
from nextcord.ext import commands
from nextcord.ui import View, Button

# Function to convert user input into seconds
def convert_time(duration: str) -> int:
    time_units = {
        "s": 1,     # seconds
        "m": 60,    # minutes
        "h": 3600,  # hours
        "d": 86400, # days
        "w": 604800 # weeks
    }

    unit = duration[-1].lower()
    if unit not in time_units:
        return None  # Invalid format

    try:
        value = int(duration[:-1])  # Extract numeric part
    except ValueError:
        return None  # Invalid number

    return value * time_units[unit]  # Convert to seconds

class GiveawayView(View):
    def __init__(self, bot, timeout=60, prize="No prize specified", server_name="Unknown Server"):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.prize = prize
        self.server_name = server_name
        self.entries = []  # List of users who entered

    async def on_timeout(self):
        """Called when the giveaway ends (timeout)."""
        for child in self.children:
            child.disabled = True  # Disable button after giveaway ends

        # Define winner and pick randomly if entries exist
        if self.entries:
            winner = random.choice(self.entries)  # Pick a random winner
            winner_mention = winner.mention
        else:
            winner_mention = "No one entered 😢"
            winner = None  # Define winner as None if no one entered

        # Update embed with winner
        embed = Embed(
            title=f"🎉 Giveaway Ended - {self.prize} 🎉",
            description=f"Winner: {winner_mention}",
            color=nextcord.Color.gold(),
        )

        # Edit message to show the winner
        await self.message.edit(embed=embed, view=self)

        # Send DM to the winner
        if winner:
            try:
                # Send a direct message to the winner
                dm_message = f"Hey {winner.mention}! You won **{self.prize}** from the giveaway in **{self.server_name}**! \nPlease follow any instructions provided to claim your prize!"
                await winner.send(dm_message)
            except nextcord.errors.Forbidden:
                await self.message.channel.send(f"⚠️ I couldn't DM the winner, {winner.mention}. Make sure they allow DMs from server members.")

    @nextcord.ui.button(label="Enter Giveaway", style=ButtonStyle.green)
    async def enter_giveaway(self, button: Button, interaction: Interaction):
        """Button that allows users to enter the giveaway."""
        user = interaction.user
        if user not in self.entries:
            self.entries.append(user)
            await interaction.response.send_message(f"✅ {user.mention}, you have entered the giveaway!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ You have already entered!", ephemeral=True)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="giveaway", description="Starts a giveaway")
    async def giveaway(self, interaction: Interaction, duration: str, prize: str):
        """Starts a giveaway with a specified duration and prize.
        Example: /giveaway 5m Gaming Mouse
        """
        time_in_seconds = convert_time(duration)
        if time_in_seconds is None:
            await interaction.response.send_message(
                "⚠️ Invalid time format! Use `s` (seconds), `m` (minutes), `h` (hours), `d` (days), `w` (weeks). Example: `5m`"
            )
            return

        embed = Embed(
            title="🎉 Giveaway! 🎉",
            description=f"Prize: **{prize}**\nClick the button below to enter!\nGiveaway ends in {duration}.",
            color=nextcord.Color.blue(),
        )

        view = GiveawayView(self.bot, timeout=time_in_seconds, prize=prize, server_name=interaction.guild.name)
        message = await interaction.response.send_message(embed=embed, view=view)
        view.message = message  # Store message reference

    @giveaway.error
    async def giveaway_error(self, interaction: Interaction, error):
        """Handle errors related to the giveaway command."""
        if isinstance(error, nextcord.errors.Forbidden):
            await interaction.response.send_message("⚠️ You need administrator permissions to use this command.")
        else:
            raise error

def setup(bot):
    """Add the Giveaway cog to the bot."""
    bot.add_cog(Giveaway(bot))
