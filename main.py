import nextcord
from nextcord.ext import commands
import datetime as date

from config import TOKEN
from cogs.utity_cogs import auto_load_cogs, load_prefix
from cogs.admin_cmd_cogs import load_is_restart

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=['EP ',"!"], intents=intents)

async def set_command_prefix():
    prefix = await load_prefix()
    bot.command_prefix = prefix

@bot.event
async def on_ready():
    channel = bot.get_channel(1060166813079568384)
    is_bot_restarting = await load_is_restart()
    
    await set_command_prefix()
    
    if is_bot_restarting:
        await auto_load_cogs(bot)
        await channel.send("Bot đã khởi động lại thành công!")
        print("Bot đã khởi động lại thành công!")
        print("================================")
        await load_is_restart(False)
    else:
        await auto_load_cogs(bot)
        await channel.send('E Pandora-chan đã sẵn sàng!')
        print('E Pandora-chan đã sẵn sàng!')
        print("===========================")
    return

@bot.event
async def on_disconnect():
    print(f"Bot disconnected. Reconnecting...[{date.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]")
    print("==============================================")
if __name__ == "__main__":
    bot.run(TOKEN)