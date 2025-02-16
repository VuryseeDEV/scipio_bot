import nextcord
from nextcord.ext import commands


"""
    Non-Dynamic. (Specific to one server only)
"""
class ReactionR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_message_id = 1340481770528968724  # Replace with actual message ID
        self.emoji_to_role = {
            nextcord.PartialEmoji(name="🔴"): 1340479108609609739,  # Replace with actual role ID
            nextcord.PartialEmoji(name="🟡"): 1340481362636963932,  # Replace with actual role ID
            nextcord.PartialEmoji(name="🟢"): 1340481520951099443,  # Replace with actual emoji & role ID
        }

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        """Assigns a role when a user reacts to the specified message."""
        if payload.message_id != self.role_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role_id = self.emoji_to_role.get(payload.emoji)
        if not role_id:
            return

        role = guild.get_role(role_id)
        if not role:
            return

        try:
            await payload.member.add_roles(role)
        except nextcord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent):
        """Removes a role when a user removes their reaction."""
        if payload.message_id != self.role_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role_id = self.emoji_to_role.get(payload.emoji)
        if not role_id:
            return

        role = guild.get_role(role_id)
        if not role:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        try:
            await member.remove_roles(role)
        except nextcord.HTTPException:
            pass




def setup(bot):  
    bot.add_cog(ReactionR(bot))