from nextcord.ext import commands
import random
import mysql.connector

from cogs.g_def import *


# Hàm tăng cấp người dùng
async def level_up(message, user_id):
    main_connection = await connect_main_db()
    main_cursor = main_connection.cursor()

    try:
        main_cursor.execute('SELECT db_exp, db_level, db_exp_need, db_wallet FROM user_data WHERE db_user_id = %s', (user_id,))
        user_data = main_cursor.fetchone()

        if user_data:
            level = user_data[1]
            a = round(random.uniform(-0.5, 1), 1)
            b = round(random.uniform(1, 2), 1)
            c = random.randint(-9, 9)

            exp_needed = 10 * (level ** 2)
            if level == 0:
                exp_needed = 10
            exp_awarded_raw = round(a * (level ** 2) + b * level + c, 2)
            factor = random.choice([0.1, 0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0])
            bonus_exp = random.randint(-9, 9)
            exp_awarded = int(exp_awarded_raw * factor) + bonus_exp
            percent_exp_need = int(exp_needed * 0.15)

            if exp_awarded < 0 and level in [0, 1]:
                exp_awarded = 1
            if level < 3:
                percent_exp_need = 5
            if exp_awarded > percent_exp_need:
                exp_awarded = percent_exp_need
            exp = int(user_data[0] + exp_awarded)
            reward = 0

            while exp >= exp_needed:
                level += 1
                exp -= exp_needed
                exp_needed = 10 * (level ** 2)

                if level < 5:
                    reward = level * 100
                else:
                    reward = level * (100 * (level // 10))
                wallet = user_data[3] + reward

                if level < 10:
                    reward = level * 100
                else:
                    reward = level * (100 * (level // 10))
                if message.channel.id != 879185402404143144:
                    await message.channel.send(f"Chúc mừng, {message.author.mention}! Bạn vừa lên cấp {level} và được thưởng `{reward} Cash`!")

            main_cursor.execute('UPDATE user_data SET db_exp = %s, db_level = %s, db_exp_need = %s, db_wallet = db_wallet + %s WHERE db_user_id = %s', (exp, level, exp_needed, reward, user_id))
            main_connection.commit()
    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")
    finally:
        if main_connection:
            main_cursor.close()
            main_connection.close()


class User_Levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)

        # Xử lý việc tăng cấp người dùng
        await level_up(message, user_id)

def setup(bot):
    bot.add_cog(User_Levelling(bot))
