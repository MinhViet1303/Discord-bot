from nextcord.ext import commands
import random

from cogs.g_def import connect_main_db, get_reset_daily_time

random.seed()

async def load_luck(user_id, update = None or bool, luck = None, temp_luck = None):
    main_connection = await connect_main_db()  # Kết nối đến máy chủ MySQL mà không chọn cơ sở dữ liệu cụ thể
    main_cursor = main_connection.cursor()
    
    if update is None or update != True:
        main_cursor.execute("SELECT db_luck, db_temp_luck FROM global_user_data WHERE db_g_user_id = %s", (user_id,))
        result = main_cursor.fetchone()
        if result is None:
            main_cursor.execute("INSERT INTO global_user_data (db_luck, db_temp_luck) VALUES (%s, %s)", (0, 0))
            main_connection.commit()
        return result if result is not None else (0, 0)
    else:
        main_cursor.execute("UPDATE global_user_data SET db_luck = %s, db_temp_luck = %s WHERE db_g_user_id = %s", (luck, temp_luck, user_id))
        main_connection.commit()

    if main_connection:
        main_cursor.close()
        main_connection.close()

async def random_luck():
    now, reset_daily = await get_reset_daily_time()
    

class Luck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await load_luck()
        await ctx.send("**<@!687325973309423680>**")

def setup(bot):
    bot.add_cog(Luck(bot))