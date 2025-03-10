import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import json
import os

class ImageOnlyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.image_only_channels_file = "image_only_channels.json"
        self.image_only_channels = self.load_image_only_channels()
    
    def load_image_only_channels(self):
        """Load existing image-only channels from file"""
        if os.path.exists(self.image_only_channels_file):
            with open(self.image_only_channels_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_image_only_channels(self):
        """Save image-only channels to file"""
        with open(self.image_only_channels_file, 'w') as f:
            json.dump(self.image_only_channels, f)
    
    @nextcord.slash_command(
        name="imgonly",
        description="Set a channel to only allow image messages"
    )
    async def imgonly(
        self, 
        interaction: nextcord.Interaction, 
        channel: nextcord.abc.GuildChannel = SlashOption(
            name="channel",
            description="The channel to set as image-only",
            required=True,
            channel_types=[nextcord.ChannelType.text]
        )
    ):
        """Slash command to set a channel as image-only"""
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
            return
        
        channel_id = channel.id
        
        # Check if channel is already image-only
        if channel_id in self.image_only_channels:
            await interaction.response.send_message(f"Channel {channel.mention} is already set to image-only mode!", ephemeral=True)
            return
        
        # Add channel to image-only list
        self.image_only_channels.append(channel_id)
        self.save_image_only_channels()
        
        await interaction.response.send_message(f"Channel {channel.mention} has been set to image-only mode. Non-image messages will be deleted.", ephemeral=False)
    
    @nextcord.slash_command(
        name="imgonly_disable",
        description="Disable image-only mode for a channel"
    )
    async def imgonly_disable(
        self, 
        interaction: nextcord.Interaction, 
        channel: nextcord.abc.GuildChannel = SlashOption(
            name="channel",
            description="The channel to disable image-only mode for",
            required=True,
            channel_types=[nextcord.ChannelType.text]
        )
    ):
        """Slash command to disable image-only mode for a channel"""
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
            return
        
        channel_id = channel.id
        
        # Check if channel is in image-only list
        if channel_id not in self.image_only_channels:
            await interaction.response.send_message(f"Channel {channel.mention} is not in image-only mode!", ephemeral=True)
            return
        
        # Remove channel from image-only list
        self.image_only_channels.remove(channel_id)
        self.save_image_only_channels()
        
        await interaction.response.send_message(f"Image-only mode has been disabled for channel {channel.mention}.", ephemeral=False)
    
    @nextcord.slash_command(
        name="imgonly_list",
        description="List all channels with image-only mode enabled"
    )
    async def imgonly_list(self, interaction: nextcord.Interaction):
        """Slash command to list all channels with image-only mode enabled"""
        if not self.image_only_channels:
            await interaction.response.send_message("No channels are currently set to image-only mode.", ephemeral=True)
            return
        
        channels_list = []
        for channel_id in self.image_only_channels:
            channel = self.bot.get_channel(channel_id)
            if channel:
                channels_list.append(f"• {channel.mention}")
        
        if channels_list:
            await interaction.response.send_message(f"**Channels with image-only mode enabled:**\n{''.join(channels_list)}", ephemeral=False)
        else:
            await interaction.response.send_message("No valid channels with image-only mode found.", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Event listener for messages to enforce image-only rule"""
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Check if the message is in an image-only channel
        if message.channel.id in self.image_only_channels:
            # Check if message has attachments
            has_image = False
            
            if message.attachments:
                # Check if any attachment is an image
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        has_image = True
                        break
            
            # Check for embeds with images
            if not has_image and message.embeds:
                for embed in message.embeds:
                    if embed.image or embed.thumbnail:
                        has_image = True
                        break
            
            # Delete message if it's not an image
            if not has_image:
                try:
                    await message.delete()
                    # Optional: Send a temporary notification to the user
                    warning = await message.channel.send(
                        f"{message.author.mention}, only images are allowed in this channel!",
                    )
                    # Delete the warning after a few seconds
                    await warning.delete(delay=5)
                except nextcord.errors.NotFound:
                    pass  # Message was already deleted
                except nextcord.errors.Forbidden:
                    # Bot doesn't have permission to delete messages
                    pass

def setup(bot):
    bot.add_cog(ImageOnlyCog(bot))