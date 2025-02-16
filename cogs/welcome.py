import nextcord
from nextcord.ext import commands
from nextcord import File, Embed
from io import BytesIO
import requests
from PIL import Image

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            # Create the welcome banner with user's avatar only (no text)
            welcome_image = await self.create_welcome_image(member)

            # Create the embed with the welcome message
            embed = Embed(
                title="Welcome to the server!",
                description=f"Welcome {member.mention} to {guild.name}! We're happy to have you here.",
                color=nextcord.Color.red()  # You can change the color if you prefer
            )

            # Attach the welcome image to the embed
            embed.set_image(url="attachment://welcome_banner.png")

            # Send the embed with the image
            await guild.system_channel.send(
                content=f"Welcome {member.mention}!", 
                embed=embed, 
                file=File(welcome_image, filename="welcome_banner.png")
            )

    async def create_welcome_image(self, member):
        # Load your custom background image (replace with your file path or URL)
        background_image_path = "assets/botwelcombanner.jpg"
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
    bot.add_cog(Welcome(bot))
