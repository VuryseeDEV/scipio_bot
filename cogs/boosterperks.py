import nextcord
from nextcord import SlashOption, Colour
from nextcord.ext import commands
import sqlite3
import os

class BoosterPerks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "custom_roles.db"
        self._setup_database()
        
    def _setup_database(self):
        """Set up the SQLite database table if it doesn't exist."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_roles (
            user_id TEXT PRIMARY KEY,
            role_id TEXT,
            guild_id TEXT
        )
        ''')
        conn.commit()
        conn.close()
        
    def _get_custom_role(self, user_id, guild_id):
        """Get the custom role ID for a user in a guild."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role_id FROM custom_roles WHERE user_id = ? AND guild_id = ?", 
            (str(user_id), str(guild_id))
        )
        result = cursor.fetchone()
        conn.close()
        return int(result[0]) if result else None
        
    def _save_custom_role(self, user_id, role_id, guild_id):
        """Save a custom role to the database."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO custom_roles (user_id, role_id, guild_id) VALUES (?, ?, ?)",
            (str(user_id), str(role_id), str(guild_id))
        )
        conn.commit()
        conn.close()
        
    def _delete_custom_role(self, user_id, guild_id):
        """Delete a custom role from the database."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM custom_roles WHERE user_id = ? AND guild_id = ?",
            (str(user_id), str(guild_id))
        )
        conn.commit()
        conn.close()

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
        guild = interaction.guild

        # Check if the user is a server booster by role
        booster_role = nextcord.utils.get(guild.roles, name="Server Booster")
        if not booster_role or booster_role not in member.roles:
            await interaction.response.send_message("You must be a server booster to use this command!")
            return

        # Check if the user already has a custom booster role
        custom_role_id = self._get_custom_role(member.id, guild.id)
        if custom_role_id:
            custom_role = nextcord.utils.get(guild.roles, id=custom_role_id)
            
            if custom_role:  # If the role still exists
                await interaction.response.send_message(f"You already have a custom role: **{custom_role.name}**. Use `/booster update` to modify it.", ephemeral=True)
                return

        # Check if the hex code is valid
        if not hex_code.startswith("#") or len(hex_code) != 7:
            await interaction.response.send_message("Invalid hex code! Please use a format like #ff5733.")
            return

        try:
            # Convert hex to Colour object
            color = Colour(int(hex_code[1:], 16))

            # Create a new custom role
            new_role = await guild.create_role(
                name=role_name,
                colour=color,
                reason=f"Custom role for booster {member.name}",
            )

            # Ensure the bot has permission to modify roles
            bot_role = guild.me.top_role
            if bot_role.position <= booster_role.position:
                await interaction.response.send_message("The bot's role must be higher than the Server Booster role to create this role!", ephemeral=True)
                await new_role.delete()  # Clean up the role we just created
                return

            # Find the position of the "Server Booster" role and move the custom role above it
            booster_role_position = booster_role.position
            await new_role.edit(position=booster_role_position + 1)

            # Add the newly created role to the user
            await member.add_roles(new_role)
            
            # Store the role ID in our database
            self._save_custom_role(member.id, new_role.id, guild.id)

            await interaction.response.send_message(f"Created your custom role **{role_name}** with color **{hex_code}**!")

        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
            
    @booster.subcommand()
    async def update(
        self,
        interaction: nextcord.Interaction,
        new_name: str = SlashOption(description="New name for your custom role", required=False),
        new_color: str = SlashOption(description="New hex code for the role color (e.g., #ff5733)", required=False)
    ):
        """Update your existing custom role."""
        member = interaction.user
        guild = interaction.guild
        
        # Check if the user has a custom role
        custom_role_id = self._get_custom_role(member.id, guild.id)
        if not custom_role_id:
            await interaction.response.send_message("You don't have a custom role to update! Use `/booster claim` first.", ephemeral=True)
            return
            
        custom_role = nextcord.utils.get(guild.roles, id=custom_role_id)
        
        if not custom_role:
            # Role no longer exists
            self._delete_custom_role(member.id, guild.id)
            await interaction.response.send_message("Your custom role was not found. You can create a new one with `/booster claim`.", ephemeral=True)
            return
            
        # Update the role
        try:
            update_kwargs = {}
            
            if new_name:
                update_kwargs["name"] = new_name
                
            if new_color:
                if not new_color.startswith("#") or len(new_color) != 7:
                    await interaction.response.send_message("Invalid hex code! Please use a format like #ff5733.")
                    return
                update_kwargs["colour"] = Colour(int(new_color[1:], 16))
                
            if not update_kwargs:
                await interaction.response.send_message("Please provide a new name or color to update your role.", ephemeral=True)
                return
                
            await custom_role.edit(**update_kwargs, reason=f"Custom role update for {member.name}")
            
            response_message = "Updated your custom role: "
            if new_name:
                response_message += f"name to **{new_name}** "
            if new_color:
                response_message += f"color to **{new_color}** "
                
            await interaction.response.send_message(response_message)
            
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
            
    @booster.subcommand()
    async def remove(self, interaction: nextcord.Interaction):
        """Remove your custom role."""
        member = interaction.user
        guild = interaction.guild
        
        custom_role_id = self._get_custom_role(member.id, guild.id)
        if not custom_role_id:
            await interaction.response.send_message("You don't have a custom role to remove!", ephemeral=True)
            return
            
        custom_role = nextcord.utils.get(guild.roles, id=custom_role_id)
        
        if custom_role:
            try:
                await custom_role.delete(reason=f"Custom role removed by {member.name}")
                self._delete_custom_role(member.id, guild.id)
                await interaction.response.send_message("Your custom role has been removed.")
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
        else:
            # Role no longer exists
            self._delete_custom_role(member.id, guild.id)
            await interaction.response.send_message("Your custom role was already removed.")

def setup(bot):
    bot.add_cog(BoosterPerks(bot))