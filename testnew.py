import nextcord
from nextcord.ext import commands
import random
import asyncio
import datetime
import pytz

from cogs.g_def import *
from config import *

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=["!"], intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await connect_db()





bot.run(TOKEN)
