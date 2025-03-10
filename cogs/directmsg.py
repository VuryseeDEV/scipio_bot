import nextcord
from nextcord.ext import commands
import asyncio
from nextcord import slash_command, Interaction, SlashOption, Embed
import sqlite3
import os

# Database file
DB_FILE = "dm_bot.db"

class DmCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()
        
        # Setup listener for DM responses
        bot.add_listener(self.on_message, 'on_message')
        
    def init_db(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create table for DM channels if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dm_channels (
            guild_id TEXT PRIMARY KEY,
            channel_id INTEGER NOT NULL
        )
        ''')
        
        # Create table for active threads if needed in the future
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dm_threads (
            guild_id TEXT,
            user_id INTEGER,
            thread_id INTEGER,
            PRIMARY KEY (guild_id, user_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_dm_channel(self, guild_id):
        """Get the DM channel ID for a guild"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT channel_id FROM dm_channels WHERE guild_id = ?', (str(guild_id),))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def set_dm_channel(self, guild_id, channel_id):
        """Set the DM channel ID for a guild"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO dm_channels (guild_id, channel_id)
        VALUES (?, ?)
        ''', (str(guild_id), channel_id))
        
        conn.commit()
        conn.close()
    
    def save_thread_info(self, guild_id, user_id, thread_id):
        """Save thread information for quick lookups"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO dm_threads (guild_id, user_id, thread_id)
        VALUES (?, ?, ?)
        ''', (str(guild_id), user_id, thread_id))
        
        conn.commit()
        conn.close()
    
    def get_thread_id(self, guild_id, user_id):
        """Get thread ID for a user in a guild"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT thread_id FROM dm_threads WHERE guild_id = ? AND user_id = ?', 
                       (str(guild_id), user_id))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    @nextcord.slash_command(name="dmchannel", description="Set the channel for DM responses")
    async def dmchannel(self, interaction: Interaction, channel: nextcord.abc.GuildChannel = SlashOption(
        name="channel",
        description="The channel to log DM responses",
        required=True,
        channel_types=[nextcord.ChannelType.text]
    )):
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
            
        guild_id = interaction.guild_id
        self.set_dm_channel(guild_id, channel.id)
        
        await interaction.response.send_message(f"DM responses will now be logged in {channel.mention}", ephemeral=True)
    
    @nextcord.slash_command(name="dm", description="Send a direct message to a member")
    async def dm(self, interaction: Interaction, 
                member: nextcord.Member = SlashOption(name="user", description="The user to DM", required=True),
                message: str = SlashOption(name="message", description="The message to send", required=True)):
        # Check if user has ban permissions (mod role)
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("You need moderator permissions to use this command.", ephemeral=True)
            return
            
        guild_id = interaction.guild_id
        
        # Check if DM channel is set for this guild
        channel_id = self.get_dm_channel(guild_id)
        if not channel_id:
            await interaction.response.send_message("Please set a DM channel first using `/dmchannel set`", ephemeral=True)
            return
            
        try:
            # Send initial response to let the user know we're working on it
            await interaction.response.send_message(f"Sending DM to {member.mention}...", ephemeral=True)
            
            # Get the target channel
            target_channel = self.bot.get_channel(channel_id)
            
            if not target_channel:
                await interaction.followup.send("Target channel not found. Please set the channel again using `/dmchannel set`", ephemeral=True)
                return
            
            # Look up existing thread or create a new one    
            thread_name = f"{member.name}-dmlog"
            thread_id = self.get_thread_id(guild_id, member.id)
            thread = None
            
            if thread_id:
                thread = self.bot.get_channel(thread_id)
            
            # If thread doesn't exist or couldn't be found, create a new one
            if not thread:
                # Create a new thread
                thread = await target_channel.create_thread(
                    name=thread_name,
                    auto_archive_duration=1440,  # 1 day
                    type=nextcord.ChannelType.public_thread
                )
                
                # Save the thread information
                self.save_thread_info(guild_id, member.id, thread.id)
            
            # Send the message to the user
            dm_embed = Embed(
                title="Message from Server Staff",
                description=message,
                color=nextcord.Color.blue()
            )
            dm_embed.set_footer(text=f"From: {interaction.user.name} | Reply to this message to respond")
            
            await member.send(embed=dm_embed)
            
            # Log in the thread
            log_embed = Embed(
                title=f"Message sent to {member.name}",
                description=message,
                color=nextcord.Color.green()
            )
            log_embed.set_footer(text=f"Sent by: {interaction.user.name}")
            
            await thread.send(embed=log_embed)
            
            # Send a confirmation to the command user
            await interaction.followup.send(f"Message sent to {member.mention}. Responses will be logged in {thread.mention}", ephemeral=True)
            
        except nextcord.errors.Forbidden:
            await interaction.followup.send(f"Could not send a DM to {member.mention}. They may have DMs disabled.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
    
    async def on_message(self, message):
        """Listen for DM responses"""
        # Ignore messages from the bot itself
        if message.author.bot:
            return
            
        # Check if this is a DM to the bot
        if isinstance(message.channel, nextcord.DMChannel):
            user = message.author
            
            # We need to check each guild to find where this user belongs
            for guild in self.bot.guilds:
                guild_id = guild.id
                channel_id = self.get_dm_channel(guild_id)
                
                if not channel_id:
                    continue
                    
                # Check if user is in this guild
                member = guild.get_member(user.id)
                if not member:
                    continue
                    
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    continue
                
                # Find existing thread or create a new one
                thread_id = self.get_thread_id(guild_id, user.id)
                thread = None
                
                if thread_id:
                    thread = self.bot.get_channel(thread_id)
                
                # If thread doesn't exist or couldn't be found, create a new one
                if not thread:
                    thread_name = f"{user.name}-dmlog"
                    thread = await channel.create_thread(
                        name=thread_name,
                        auto_archive_duration=1440,  # 1 day
                        type=nextcord.ChannelType.public_thread
                    )
                    
                    # Save the thread information
                    self.save_thread_info(guild_id, user.id, thread.id)
                
                # Log the response in the thread
                response_embed = Embed(
                    title=f"Response from {user.name}",
                    description=message.content,
                    color=nextcord.Color.purple()
                )
                
                # Add attachments if any
                if message.attachments:
                    response_embed.add_field(name="Attachments", value="\n".join([a.url for a in message.attachments]))
                
                await thread.send(embed=response_embed)
                
                # No need to check other guilds once we've found the right one
                break

def setup(bot):
    bot.add_cog(DmCog(bot))