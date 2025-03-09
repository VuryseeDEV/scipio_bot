import nextcord
from nextcord import SlashOption, Colour
from nextcord.ext import commands

class BoosterPerks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command()
    async def booster(self, interaction: nextcord.Interaction):
        """Commands for server boosters."""
        pass

    @booster.subcommand()
    async def claim(
        self,
        interaction: nextcord.Interaction,
        role_name: str = SlashOption(description="Name of the role"),
        hex_code: str = SlashOption(description="Hex code for the role color (e.g., #ff5733)")
    ):
        """Claim a custom role if you are a server booster."""
        member = interaction.user

        # Check if the user is a server booster by role
        booster_role = nextcord.utils.get(interaction.guild.roles, name="Server Booster")
        if not booster_role or booster_role not in member.roles:
            await interaction.response.send_message("You must be a server booster to use this command!")
            return

        # Check if the hex code is valid
        if not hex_code.startswith("#") or len(hex_code) != 7:
            await interaction.response.send_message("Invalid hex code! Please use a format like #ff5733.")
            return

        try:
            # Convert hex to Colour object
            color = Colour(int(hex_code[1:], 16))

            # Check if the user already has a custom role
            existing_role = next((role for role in member.roles if role.name.startswith(f"{member.name}'s Role")), None)
            if existing_role:
                await existing_role.edit(name=role_name, colour=color)
                await interaction.response.send_message(f"Updated your role to **{role_name}** with color **{hex_code}**!")
            else:
                # Create a new custom role
                new_role = await interaction.guild.create_role(
                    name=role_name,
                    colour=color,
                    reason=f"Custom role for booster {member.name}"
                )
                await member.add_roles(new_role)
                await interaction.response.send_message(f"Created your custom role **{role_name}** with color **{hex_code}**!")

        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @booster.subcommand()
    async def delete(self, interaction: nextcord.Interaction):
        """Delete your custom booster role if you have one."""
        member = interaction.user

        # Check if the user is a server booster by role
        booster_role = nextcord.utils.get(interaction.guild.roles, name="Server Booster")
        if not booster_role or booster_role not in member.roles:
            await interaction.response.send_message("You must be a server booster to use this command!")
            return

        # Find the custom role
        custom_role = next((role for role in member.roles if role.name.startswith(f"{member.name}'s Role")), None)
        if not custom_role:
            await interaction.response.send_message("You don't have a custom role to delete!")
            return

        try:
            await custom_role.delete(reason=f"Custom role deleted by {member.name}")
            await interaction.response.send_message("Your custom role has been deleted successfully!")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(BoosterPerks(bot))
