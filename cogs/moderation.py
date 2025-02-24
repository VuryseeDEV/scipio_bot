import nextcord
from nextcord.ext import commands
from nextcord import slash_command, Interaction, SlashOption, Embed

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
          
    @nextcord.slash_command(name="purge", description="Deletes a specified number of messages from the channel.")
    async def purge(self, interaction: nextcord.Interaction, num: int):
        # Check if the user has the Manage Messages permission
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        # Purge the messages
        deleted = await interaction.channel.purge(limit=num)
        
        # Send a confirmation message
        await interaction.response.send_message(
            f"Deleted {len(deleted)} messages.", ephemeral=True
        )

    @nextcord.slash_command(
        name="sendmsg",
        description="Send a message to another channel via the bot."
    )
    async def sendmsg(
        self, 
        interaction: nextcord.Interaction, 
        channel: nextcord.TextChannel, 
        message: str,
        title: str = None  # Optional title/header
    ):
        # Check if the user has Manage Messages permission
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return
        
        # Check if the user has permission to send messages in the target channel
        if not channel.permissions_for(interaction.user).send_messages:
            await interaction.response.send_message(
                "You do not have permission to send messages in that channel.", ephemeral=True
            )
            return
        
        # Create an embed for the message
        embed = Embed(
            title=title if title else None,  # Set title if provided
            description=message,
            color=nextcord.Color.blue()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
 
        
        # Send the embed to the specified channel
        await channel.send(embed=embed)
        
        # Confirm action to the user
        await interaction.response.send_message(
            f"Message sent to {channel.mention}."
        )


    @nextcord.slash_command(name="setnick", description="Change your or someone else's nickname.")
    async def setnick(self, ctx: nextcord.Interaction, member: nextcord.Member, nickname: str):
        # Check if the user has Manage Nicknames permission
        if not ctx.user.guild_permissions.manage_nicknames:
            await ctx.send("You do not have permission to manage nicknames.")
            return

        try:
            # Change the nickname
            await member.edit(nick=nickname)
            await ctx.send(f"Successfully changed {member.mention}'s nickname to {nickname}.")
        except nextcord.errors.Forbidden:
            await ctx.send("I do not have permission to change that user's nickname.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):  
    bot.add_cog(Mod(bot))