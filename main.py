import nextcord
from nextcord.ext import commands
import json
import os

from cogs.config import *

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=['EP ',"!"], intents=intents)

if not os.path.exists('prefix.json') or os.stat('prefix.json').st_size == 0:
    with open('prefix.json', 'w') as f:
        json.dump({'prefixes': ["EP ", "!"]}, f)
with open('prefix.json', 'r') as f:
    try:
        prefixes = json.load(f)['prefixes']
    except json.JSONDecodeError:
        prefixes = ["EP ", "!"]

bot.command_prefix = prefixes

def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('cogs.py'):
            try:
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded cog: {filename}')
            except Exception as e:
                print(f'Error loading cog {filename}: {str(e)}')

@bot.event
async def on_ready():
    channel = bot.get_channel(1060166813079568384) 
    load_cogs()
    await channel.send('E Pandora-chan đã sẵn sàng!')
    print('E Pandora-chan đã sẵn sàng!')
    await bot.change_presence(status=nextcord.Status.online) #for online
    # await bot.change_presence(status=nextcord.Status.offline) #for offline
    # await bot.change_presence(status=nextcord.Status.idle) #for idle
    # await bot.change_presence(status=nextcord.Status.dnd) #for do not disturb
    return


if __name__ == "__main__":
    bot.run(TOKEN)