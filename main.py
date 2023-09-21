import nextcord
from nextcord.ext import commands
import json
import os

from config import *

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

#auto load cogs
async def load_cogs(ctx = None, action = None):
    for filename in os.listdir('./cogs'):
        if filename.endswith('cogs.py'):
            try:
                if action is None:
                    bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'Loaded cog: {filename}')
                else:
                    bot.unload_extension(f'cogs.{filename[:-3]}')
                    bot.load_extension(f'cogs.{filename[:-3]}')
                    await ctx.send(f'Reload cog: **{filename.replace(".py", "")}**')
                    print(f'Reload cog: {filename}')
            except Exception as e:
                print(f'Error loading cog {filename}: {str(e)}')

@bot.command()
async def cogs(ctx, action, cog_name = None):
    if cog_name is not None:
        cog_name = cog_name.lower()  

        if cog_name.endswith("cogs"):
            cog_name1 = f'cogs.{cog_name}'
        else:
            cog_name1 = f'cogs.{cog_name}_cogs'
        
        cog_name2 = cog_name1.replace("cogs.", "")
    
    if cog_name is None and action in ["reloadall", "reload_all", "rall", "r_all"]:
        await load_cogs(ctx, action)
    
    elif action in ["load", "+"]:
        if cog_name1 not in bot.extensions:
            await bot.load_extension(cog_name1)
            await ctx.send(f'Loaded cog: **{cog_name2}**')
            print (f'Loaded cog: {cog_name2}.py')
        else:
            await ctx.send(f'Cog **{cog_name2}** đã đang load!')
    
    elif action in ["unload", "-"]:
        if cog_name1 in bot.extensions:
            await bot.unload_extension(cog_name1)
            await ctx.send(f'Unloaded cog: **{cog_name2}**')
            print (f'Unloaded cog: {cog_name2}.py')
        else:
            await ctx.send(f'Không có cog nào tên **{cog_name2}** đang load!')
    
    elif action in ["reload", "r"]:
        if cog_name1 in bot.extensions:
            await bot.unload_extension(cog_name1)
            await bot.load_extension(cog_name1)
            await ctx.send(f'Reload cog: **{cog_name2}**')
            print (f'Reload cog: {cog_name2}.py')
        else:
            await bot.load_extension(cog_name1)
            await ctx.send(f'Loaded cog: **{cog_name2}**')
            print (f'Loaded cog: {cog_name2}.py')
    
    else:
        await ctx.send("Lỗi cú pháp lệnh!")

@bot.event
async def on_ready():
    channel = bot.get_channel(1060166813079568384) 
    await load_cogs()
    await channel.send('E Pandora-chan đã sẵn sàng!')
    print('E Pandora-chan đã sẵn sàng!')
    await bot.change_presence(status=nextcord.Status.online) #for online
    # await bot.change_presence(status=nextcord.Status.offline) #for offline
    # await bot.change_presence(status=nextcord.Status.idle) #for idle
    # await bot.change_presence(status=nextcord.Status.dnd) #for do not disturb
    return

@bot.event
async def on_disconnect():
    print("Bot disconnected. Reconnecting...")

if __name__ == "__main__":
    bot.run(TOKEN)