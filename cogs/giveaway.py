import nextcord
import random
import time
from nextcord.ext import commands
from nextcord import Interaction, Embed, ButtonStyle
from nextcord.ui import View, Button

# Function to convert user input into seconds
def convert_time(duration: str) -> int:
    time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    unit = duration[-1].lower()
    if unit not in time_units:
        return None  # Invalid format
    try:
        value = int(duration[:-1])
    except ValueError:
        return None  # Invalid number
    return value * time_units[unit]

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

        if self.entries:
            winner = random.choice(self.entries)  # Pick a random winner
            winner_mention = winner.mention
        else:
            winner_mention = "No one entered 😢"

        # Update embed with winner
        embed = Embed(
            title=f"🎉 Giveaway Ended - {self.prize} 🎉",
            description=f"Winner: {winner_mention}",
            color=nextcord.Color.gold(),
        )

        # Edit message to show the winner
        await self.message.edit(embed=embed, view=self)

        # Send DM to the winner
        if winner_mention != "No one entered 😢":
            try:
                # Send a direct message to the winner
                dm_message = f"Hey {winner_mention}! You won **{self.prize}** from the giveaway in **{self.server_name}**! \nPlease follow any instructions provided (if any) to claim your prize!"
                await winner.send(dm_message)
            except nextcord.errors.Forbidden:
                # If the bot cannot DM the winner (e.g., they have DMs disabled from server members)
                await self.message.channel.send(f"⚠️ I couldn't DM the winner, {winner_mention}. Make sure they allow DMs from server members.")

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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def giveaway(self, ctx, duration: str, *, prize: str = "A surprise!"):
        """Starts a giveaway. Usage: $giveaway <time><unit> <prize>
        Example: $giveaway 5m Gaming Mouse
        """
        time_in_seconds = convert_time(duration)
        if time_in_seconds is None:
            await ctx.send("⚠️ Invalid time format! Use `s` (seconds), `m` (minutes), `h` (hours), `d` (days), `w` (weeks). Example: `5m`")
            return

        embed = Embed(
            title="🎉 Giveaway! 🎉",
            description=f"Prize: **{prize}**\nClick the button below to enter!\nGiveaway ends in {duration}.",
            color=nextcord.Color.blue(),
        )

        view = GiveawayView(self.bot, timeout=time_in_seconds, prize=prize, server_name=ctx.guild.name)
        message = await ctx.send(embed=embed, view=view)
        view.message = message  # Store message reference

    @giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⚠️ You need administrator permissions to use this command")
        else:
            raise error
        
def setup(bot):
    bot.add_cog(Giveaway(bot))
