import nextcord
from nextcord.ext import commands, tasks
import os
import asyncio 
from dotenv import load_dotenv
import psutil
import datetime


load_dotenv("tkn.env")
token = os.getenv("BOT_TOKEN")


intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

async def set_rich_presence():
    activity=nextcord.Activity(
        type=nextcord.ActivityType.playing,
        name="with myself",
        details="lol",
        #start=datetime.datetime.utcnow(),
        party_size=(1, 2),
        buttons=[
            {"label": "Github", "url": "https://github.com/VuryseeDEV/scipio_bot/tree/main"},
        ]
    )
    await bot.change_presence(activity=activity)

# 
"""@tasks.loop(seconds=60)  # Adjust the interval as needed (e.g., every 60 seconds)
async def monitor_memory():
    process = psutil.Process(os.getpid())  # Get the process ID
    memory_usage = process.memory_info().rss / (1024 * 1024)  # Convert to MB
    print(f"Memory usage: {memory_usage:.2f} MB")"""
#


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await set_rich_presence()
    #monitor_memory.start()  

async def load_cogs():
    """Loads all cogs from the 'cogs' folder"""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}! TT")
            except Exception as e:
                print(e)



async def main():
    await load_cogs()
    await bot.start(token)

asyncio.run(main()) 