import nextcord
from nextcord.ext import commands
import sqlite3

database = sqlite3.connect('scipio.db')
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS messages (message_content STRING, message_id INT)")

class DatabaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command()  
    async def write(self, interaction : nextcord.Interaction, message : str):
        query = "INSERT INTO messages VALUES (?, ?)"
        cursor.execute(query, (message, interaction.id))
        database.commit()
        await interaction.response.send_message("Message written to database.")

    @nextcord.slash_command()
    async def delete(self, interaction : nextcord.Interaction, message : str):

        query = "DELETE FROM messages WHERE message_content = ? AND message_id = ?"
        cursor.execute(query, (message,))
        database.commit()

        await interaction.response.send_message("Message deleted from database.")
def setup(bot):
    bot.add_cog(DatabaseCommands(bot))