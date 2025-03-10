import asyncio
import nextcord
from nextcord.ext import commands, tasks
import os
from dotenv import load_dotenv
import traceback

load_dotenv("tkn.env")
token = os.getenv("BOT_TOKEN")

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True  

bot = commands.Bot(command_prefix="$", intents=intents)

async def set_rich_presence():
    activity = nextcord.Activity(
        type=nextcord.ActivityType.watching,
        name="YouTube",
        details="",
        party_size=(1, 100),
        url="https://github.com/VuryseeDEV/scipio_bot/tree/main"  
    )
    await bot.change_presence(activity=activity)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await set_rich_presence()

@bot.event
async def on_command_error(ctx, error):
    print(f"An error occurred: {error}")
    print(traceback.format_exc())
    await ctx.send(f"An error occurred: {error}")

async def load_cogs():
    """Loads all cogs from the 'cogs' folder"""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")
                print(traceback.format_exc())

if __name__ == "__main__":
    bot.loop.create_task(load_cogs())
    bot.run(token)