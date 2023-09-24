from nextcord.ext import commands
import subprocess

from cogs.g_def import connect_main_db


async def load_is_restart(value = None):
    main_connection = await connect_main_db()  # Kết nối đến máy chủ MySQL mà không chọn cơ sở dữ liệu cụ thể
    main_cursor = main_connection.cursor()

    if value is None:
        main_cursor.execute("SELECT db_utity_boolean FROM utity WHERE db_utity_name = 'is_restart'")
        result = main_cursor.fetchone()
        if result is None:
            main_cursor.execute("INSERT INTO utity (db_utity_id, db_utity_name, db_utity_boolean) VALUES (%s, %s, %s)", (2, 'is_restart', 0))
            main_connection.commit()
        return bool(result[0]) if result else False
    else:
        main_cursor.execute("UPDATE utity SET db_utity_boolean = %s WHERE db_utity_name = 'is_restart'", (1 if value == True else 0,))
        main_connection.commit()

    if main_connection:
        main_cursor.close()
        main_connection.close()


class Admin_CMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="restart", aliases = ["rs"])
    @commands.is_owner() 
    async def restart(self, ctx):
        
        await ctx.send("Bot đang khởi động lại...")
        print("Bot đang khởi động lại...")
        
        # Đặt biến trạng thái là True trước khi khởi động lại
        await load_is_restart(True)
        
        # Khởi động lại bot bằng cách chạy lại chương trình Python
        subprocess.Popen(["python", "-Xfrozen_modules=off", "main.py"])

def setup(bot):
    bot.add_cog(Admin_CMD(bot))