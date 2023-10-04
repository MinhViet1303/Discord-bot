from nextcord.ext import commands
import subprocess
import asyncio
import pygetwindow as gw

from cogs.g_def import update_config


class Admin_CMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="restart", aliases = ["rs"])
    @commands.is_owner() 
    async def restart(self, ctx, action = None):
        await ctx.send("Bot đang khởi động lại...🔄")
        print("===========================")
        print("Bot đang khởi động lại...🔄")
        
        # Đặt biến trạng thái là True trước khi khởi động lại
        await update_config("is_restart", True)
        
        if action is None:
            # Khởi động lại bot bằng cách chạy lại chương trình Python
            subprocess.Popen(["python", "-Xfrozen_modules=off", "main.py"]).wait()
        
        elif action in ["clear", "c"]:
            self.bot.clear()
            subprocess.Popen("cls", shell=True)
            
            await asyncio.sleep(3)
            
            subprocess.Popen(["python", "-Xfrozen_modules=off", "main.py"]).wait()
            
        elif action in ["close", "cl"]:
            self.bot.clear()
            subprocess.Popen(["start", "auto_boots_discord_bot.bat.lnk"], shell=True)
            
            await asyncio.sleep(3)
            
            cmd_window = None
            for title in ["auto_boots_discord_bot.bat", "C:\\WINDOW\\System32\\cmd.exe"]:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    if title == "auto_boots_discord_bot.bat":
                        cmd_window = windows[1]
                    elif title == "C:\\WINDOW\\System32\\cmd.exe":
                        cmd_window = windows[0]
                    break
            
            if cmd_window:
                cmd_window.close()
    
    
    @commands.command(name="shutdown", aliases = ["sd"])
    @commands.is_owner() 
    async def shutdown(self, ctx, action = None):
        await ctx.send("Bot đang tắt...")
        print("===========================")
        print("Bot đang tắt...")
        
        self.bot.clear()
        
        await asyncio.sleep(3)
        
        cmd_window = None
        for title in ["auto_boots_discord_bot.bat", "C:\\WINDOW\\System32\\cmd.exe"]:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                if title == "auto_boots_discord_bot.bat":
                    cmd_window = windows[1]
                elif title == "C:\\WINDOW\\System32\\cmd.exe":
                    cmd_window = windows[0]
                break
        
        if cmd_window:
            cmd_window.close()


def setup(bot):
    bot.add_cog(Admin_CMD(bot))