import nextcord
from nextcord.ext import commands
import random
import asyncio
import mysql.connector

from cogs.g_def import connect_db

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=["!"], intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await connect_db()


# Chạy bot
bot.run('ghi token')
