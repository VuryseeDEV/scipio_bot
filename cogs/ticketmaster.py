import nextcord
from nextcord.ext import commands
from nextcord import ButtonStyle, Interaction, ChannelType, PermissionOverwrite
import sqlite3
import os
import datetime
import asyncio

class TicketButton(nextcord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # Set timeout to None for persistent view
        self.bot = bot

    @nextcord.ui.button(label="Create Ticket", style=ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, button: nextcord.ui.Button, interaction: Interaction):
        # This will be handled by the on_interaction event
        pass

class CloseButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout to None for persistent view

    @nextcord.ui.button(label="Close Ticket", style=ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, button: nextcord.ui.Button, interaction: Interaction):
        channel = interaction.channel
        user = interaction.user
        
        # Send closing message
        embed = nextcord.Embed(
            title="Ticket Closed",
            description=f"This ticket has been closed by {user.mention}.\nThis channel will be deleted in 5 seconds.",
            color=nextcord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Wait a moment and delete
        await asyncio.sleep(5)
        try:
            await channel.delete(reason=f"Ticket closed by {user.name}")
        except Exception as e:
            print(f"Error deleting channel: {e}")

class TicketMaster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "tickets.db"
        self._setup_database()
        self.ticket_views = {}
        bot.loop.create_task(self.register_buttons())
        
    async def register_buttons(self):
        """Register the ticket button after the bot is ready."""
        await self.bot.wait_until_ready()
        self.bot.add_view(TicketButton(self.bot))
        self.bot.add_view(CloseButton())  # Register close button
        
    def _setup_database(self):
        """Set up the SQLite database for tracking tickets."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            user_id TEXT,
            guild_id TEXT,
            channel_id TEXT,
            created_at TEXT,
            status TEXT
        )
        ''')
        conn.commit()
        conn.close()
        
    def _save_ticket(self, ticket_id, user_id, guild_id, channel_id):
        """Save ticket information to the database."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        created_at = datetime.datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO tickets (ticket_id, user_id, guild_id, channel_id, created_at, status) VALUES (?, ?, ?, ?, ?, ?)",
            (str(ticket_id), str(user_id), str(guild_id), str(channel_id), created_at, "open")
        )
        conn.commit()
        conn.close()
        
    def _get_active_ticket(self, user_id, guild_id):
        """Check if a user has an active ticket in the guild."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT channel_id FROM tickets WHERE user_id = ? AND guild_id = ? AND status = 'open'",
            (str(user_id), str(guild_id))
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction):
        """Handle button interactions for ticket creation."""
        if not interaction.data or not interaction.data.get("custom_id"):
            return
            
        custom_id = interaction.data.get("custom_id")
        
        if custom_id == "create_ticket":
            await self.handle_ticket_creation(interaction)
            
    async def handle_ticket_creation(self, interaction: Interaction):
        """Handle the creation of a new ticket."""
        user = interaction.user
        guild = interaction.guild
        
        # Check if user already has an active ticket
        active_ticket_id = self._get_active_ticket(user.id, guild.id)
        if active_ticket_id:
            try:
                channel = guild.get_channel(int(active_ticket_id))
                if channel:
                    return await interaction.response.send_message(
                        f"You already have an open ticket in {channel.mention}. Please use that one.", 
                        ephemeral=True
                    )
            except:
                pass  # If channel not found or error, allow creating a new ticket
        
        # Check if a ticket category exists, if not create one
        ticket_category = nextcord.utils.get(guild.categories, name="TICKETS")
        if not ticket_category:
            # Set up permissions for ticket category - only visible to mods with manage_threads permissions
            overwrites = {
                guild.default_role: PermissionOverwrite(read_messages=False),
                guild.me: PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # Add permissions for roles with manage_threads permission
            for role in guild.roles:
                if role.permissions.manage_threads:
                    overwrites[role] = PermissionOverwrite(read_messages=True, send_messages=True)
                    
            ticket_category = await guild.create_category("TICKETS", overwrites=overwrites)
        
        # Create ticket ID
        ticket_id = f"ticket-{user.name.lower()}-{len(guild.channels)}"
        
        # Create a private forum channel or text channel based on guild features
        if "COMMUNITY" in guild.features and hasattr(ChannelType, "GUILD_FORUM"):
            # Create a forum post in the tickets forum
            tickets_forum = nextcord.utils.get(guild.channels, name="tickets-forum", type=ChannelType.GUILD_FORUM)
            
            if not tickets_forum:
                # Create the forum channel if it doesn't exist
                overwrites = {
                    guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False),
                    guild.me: PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
                }
                
                # Add permissions for roles with manage_threads permission
                for role in guild.roles:
                    if role.permissions.manage_threads:
                        overwrites[role] = PermissionOverwrite(read_messages=True, send_messages=True)
                
                tickets_forum = await guild.create_forum(
                    name="tickets-forum",
                    topic="Support tickets",
                    reason="Automatic creation for ticket system",
                    category=ticket_category,
                    overwrites=overwrites
                )
            
            # Create a thread in the forum
            thread = await tickets_forum.create_thread(
                name=f"Ticket: {user.name}",
                content=f"Ticket created by {user.mention}",
                auto_archive_duration=10080  # 7 days
            )
            ticket_channel = thread
            
        else:
            # Create a private text channel
            overwrites = {
                guild.default_role: PermissionOverwrite(read_messages=False),
                user: PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # Add permissions for roles with manage_threads permission
            for role in guild.roles:
                if role.permissions.manage_threads:
                    overwrites[role] = PermissionOverwrite(read_messages=True, send_messages=True)
                    
            ticket_channel = await guild.create_text_channel(
                name=ticket_id,
                category=ticket_category,
                overwrites=overwrites,
                topic=f"Support ticket for {user.name}"
            )
        
        # Save ticket in database
        self._save_ticket(ticket_id, user.id, guild.id, str(ticket_channel.id))
        
        # Create close ticket button - simplified with direct functionality
        close_view = CloseButton()
        
        # Send initial message in the ticket channel
        embed = nextcord.Embed(
            title=f"Ticket: {user.name}",
            description=f"Support ticket created by {user.mention}\n\nPlease describe your issue, and a staff member will assist you shortly.",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket ID: {ticket_id}")
        
        await ticket_channel.send(embed=embed, view=close_view)
        
        # Notify the user
        await interaction.response.send_message(
            f"Your ticket has been created in {ticket_channel.mention}",
            ephemeral=True
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticket_setup(self, ctx):
        """Set up the ticket system by adding the required permissions to mod roles."""
        guild = ctx.guild
        
        # Get all roles with manage_threads permission
        mod_roles = [role for role in guild.roles if role.permissions.manage_threads]
        
        # Get the ticket category
        ticket_category = nextcord.utils.get(guild.categories, name="TICKETS")
        
        if not ticket_category:
            await ctx.send("Ticket category not found. Please use the ticketmaster command first to set up the system.")
            return
            
        # Update permissions for all channels in the category
        for channel in ticket_category.channels:
            overwrites = channel.overwrites
            
            # Add permissions for all mod roles
            for role in mod_roles:
                overwrites[role] = PermissionOverwrite(read_messages=True, send_messages=True)
                
            # Update channel overwrites
            await channel.edit(overwrites=overwrites)
            
        await ctx.send("Ticket system permissions updated. Users with Manage Threads permissions should now have access to all ticket channels.")

    @commands.command()
    async def ticketmaster(self, ctx):
        """Display the ticket creation panel."""
        embed = nextcord.Embed(
            title="Support Ticket System",
            description="Need help? Click the button below to create a support ticket.",
            color=nextcord.Color.blue()
        )
        
        # Create ticket button
        view = TicketButton(self.bot)
        
        # Send the embed with button
        message = await ctx.send(embed=embed, view=view)
        
        # Save this view in our memory to keep the button working
        self.ticket_views[ctx.guild.id] = view

def setup(bot):
    bot.add_cog(TicketMaster(bot))