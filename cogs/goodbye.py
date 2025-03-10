import nextcord
from nextcord.ext import commands
from nextcord import File, Embed, SlashOption
from io import BytesIO
import requests
from PIL import Image

class Goodbye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.goodbye_channels = {}  # Dictionary to store goodbye channels for each guild

    @nextcord.slash_command(name="goodbye", description="Set the goodbye channel for leaving members")
    async def set_goodbye_channel(
        self, 
        interaction: nextcord.Interaction, 
        channel: nextcord.abc.GuildChannel = SlashOption(
            name="channel",
            description="The channel to send goodbye messages to",
            required=True
        )
    ):
        guild_id = interaction.guild.id
        if isinstance(channel, nextcord.TextChannel):
            self.goodbye_channels[guild_id] = channel.id
            await interaction.response.send_message(f"Goodbye channel set to {channel.mention}!", ephemeral=True)
        else:
            await interaction.response.send_message("Please select a text channel!", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        guild_id = guild.id
        
        # Check if a goodbye channel has been set for this guild
        if guild_id in self.goodbye_channels:
            goodbye_channel_id = self.goodbye_channels[guild_id]
            goodbye_channel = guild.get_channel(goodbye_channel_id)
            
            if goodbye_channel is not None:
                # Create the goodbye banner with user's avatar only (no text)
                goodbye_image = await self.create_goodbye_image(member)

                # Create the embed with the goodbye message
                embed = Embed(
                    title="Goodbye!",
                    description=f"{member.mention} has left {guild.name}. We'll miss you!",
                    color=nextcord.Color.dark_gray()  # You can change the color if needed
                )

                # Attach the goodbye image to the embed
                embed.set_image(url="attachment://goodbye_banner.png")

                # Send the embed with the image
                await goodbye_channel.send(
                    content=f"Goodbye {member.mention}...", 
                    embed=embed, 
                    file=File(goodbye_image, filename="goodbye_banner.png")
                )

    async def create_goodbye_image(self, member):
        # Load your custom background image (replace with your file path or URL)
        background_image_path = "assets/botgoodbyebanner.jpg"
        img = Image.open(background_image_path)
        
        # Resize the background image to fit the desired size (if needed)
        img = img.resize((600, 200))  # Modify this as needed

        # Fetch and add the user's avatar on top of the image
        avatar_url = member.avatar.url
        avatar = await self.get_avatar_image(avatar_url)

        # Get the size of the background image and avatar
        bg_width, bg_height = img.size
        avatar_width, avatar_height = avatar.size

        # Calculate the position to center the avatar
        avatar_position = ((bg_width - avatar_width) // 2, (bg_height - avatar_height) // 2)

        # Paste the avatar on the image
        img.paste(avatar, avatar_position)

        # Save the image to a BytesIO object
        byte_io = BytesIO()
        img.save(byte_io, "PNG")
        byte_io.seek(0)
        
        return byte_io

    async def get_avatar_image(self, url):
        # Fetch and open the avatar image
        response = requests.get(url)
        avatar_img = Image.open(BytesIO(response.content)).resize((50, 50))  # Resize the avatar to your preference
        return avatar_img

def setup(bot):
    bot.add_cog(Goodbye(bot))