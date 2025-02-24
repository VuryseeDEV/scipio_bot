import nextcord
from nextcord.ext import commands
import asyncio
from nextcord import slash_command, Interaction, SlashOption, Embed
# Static target channel ID (for one server)
TARGET_CHANNEL_ID = 1343437425212653568 # Replace with the actual channel ID

class DmCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="dm", description="Send a direct message to a member.")
    async def dm(self, ctx: nextcord.Interaction, member: nextcord.Member, message: str):
        try:
            # Send the DM to the member
            await member.send(message)
            await ctx.send(f"Successfully sent a DM to {member.mention}. Waiting for response...")

            def check(m):
                return m.author == member and isinstance(m.channel, nextcord.DMChannel)

            # Wait for the user's response in the DM
            response = await self.bot.wait_for('message', check=check)

            # Get the target channel
            target_channel = self.bot.get_channel(TARGET_CHANNEL_ID)
            if target_channel:
                await target_channel.send(f"Response from {member.mention}: {response.content}")
                await ctx.send(f"Response from {member.mention} has been sent to the channel.")
            else:
                await ctx.send("Target channel not found.")

        except nextcord.errors.Forbidden:
            await ctx.send(f"Could not send a DM to {member.mention}. They may have DMs disabled.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(DmCog(bot))

