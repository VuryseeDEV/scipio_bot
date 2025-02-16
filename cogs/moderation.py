import nextcord
from nextcord.ext import commands
from nextcord import slash_command, Interaction, SlashOption

"""
    List of moderation commands: Kick, Ban, Mute, etc...
"""

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="kick", description="Kick a member from the server")
    async def kick(
           self,
            ctx: Interaction,
            member: nextcord.Member = nextcord.SlashOption(
                name="member",
                description="Member to kick",
                required=True,
            ),
            reason: str = nextcord.SlashOption(
                name="reason",
                description="Reason",
                required=False,
            )
    ): 
        if not ctx.user.guild_permissions.kick_members:
            await ctx.response.send_message(
                "❌ You do not have permission to use this command.", ephemeral=True #Only the user can see this message
            )
            return
           
        if not reason: 
            reason ="No reason provided"
        await member.kick(reason=reason)
        await ctx.response.send_message(f"{member.mention} has been **kicked** by {ctx.user.mention} for **{reason}**.")

    @slash_command(name="ban", description="Ban a member from the server")
    async def ban(
           self,
            ctx: Interaction,
            member: nextcord.Member = nextcord.SlashOption(
                name="member",
                description="Member to ban",
                required=True,
            ),
            reason: str = nextcord.SlashOption(
                name="reason",
                description="Reason",
                required=False,
            )
    ): 
        if not ctx.user.guild_permissions.ban_members:
            await ctx.response.send_message(
                "❌ You do not have permission to use this command.", ephemeral=True #Only the user can see this message
            )
            return
           
        if not reason: 
            reason ="No reason provided"
        await member.ban(reason=reason)
        await ctx.response.send_message(f"{member.mention} has been **banned** by {ctx.user.mention} for **{reason}**.")
           

    @nextcord.slash_command(name="mute", description="Mutes a member")
    async def mute(
        self,
        ctx: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to mute",
            required=True,
        ),
    ):
        # Check if user has permission
        if not ctx.user.guild_permissions.manage_roles:
            await ctx.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        # Find the Muted role, or create one if it doesn't exist
        muted_role = nextcord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            try:
                muted_role = await ctx.guild.create_role(name="Muted", reason="Mute command used")
                
                # Deny send message permissions in all text channels
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
            except nextcord.Forbidden:
                await ctx.response.send_message("I don't have permission to create roles.", ephemeral=True)
                return

        # Add the Muted role to the user
        if muted_role in member.roles:
            await ctx.response.send_message(f"{member.mention} is already muted.", ephemeral=True)
        else:
            await member.add_roles(muted_role)
            await ctx.response.send_message(f"{member.mention} has been muted.")           

def setup(bot):  
    bot.add_cog(Mod(bot))