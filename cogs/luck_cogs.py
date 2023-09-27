from nextcord.ext import commands
import random
import datetime


from cogs.g_def import connect_main_db, get_reset_daily_time

random.seed()

async def load_luck(user_id):
    main_connection = await connect_main_db()
    main_cursor = main_connection.cursor()
    try:
        main_cursor.execute("SELECT db_luck, db_temp_luck FROM global_user_data WHERE db_g_user_id = %s", (user_id,))
        result = main_cursor.fetchone()
        
        if result is None:
            main_cursor.execute("INSERT INTO global_user_data (db_luck, db_temp_luck) VALUES (%s, %s)", (0, 0))
            main_connection.commit()
            luck, temp_luck = 0
        else:
            luck, temp_luck = result
        
        return luck, temp_luck
    
    finally:
        if main_connection:
            main_cursor.close()
            main_connection.close()


async def random_luck(user_id, factor, select = [-1, 0,1,2]):
    main_connection = await connect_main_db() 
    main_cursor = main_connection.cursor()
    try:
        main_cursor.execute("SELECT db_user_level FROM global_user_data WHERE db_g_user_id = %s", (user_id,))
        result = main_cursor.fetchone()
        
        lv = result[0]
        luck, temp_luck = await load_luck(user_id)
        
        if lv == 0:
            lv_range = 1
        elif lv <= 10:
            lv_range = lv*2
        elif lv <= 20:
            lv_range = lv*1.5
        elif lv <= 25:
            lv_range = lv*1.2
        else:
            lv_range = lv
        
        if select == -1:
            temp_luck = 0
        
        def calculate_luck_range(value):
            abs_value = abs(value)
            if abs_value <= 5:
                return value
            elif abs_value < 10:
                return value / 2
            else:
                return value / 10
        
        def random_round(value):
            return round(random.uniform(-abs(value), abs(value)), 1)
        
        luck_range = calculate_luck_range(luck)
        temp_luck_range = calculate_luck_range(temp_luck)
        
        rd_lv_range = random_round(lv_range)
        rd_luck_range = random_round(luck_range)
        rd_temp_luck_range = random_round(temp_luck_range)
        
        luck_range = rd_lv_range + rd_luck_range + rd_temp_luck_range       
        
        rd_luck = factor * random_round(luck_range)
        rd_temp_luck = temp_luck = factor * random_round(luck_range)
        
        if select == 0:
            luck += rd_luck
            temp_luck += rd_temp_luck
        elif select == 1:
            luck += rd_luck
        elif select == 2 or -1:
            temp_luck += rd_temp_luck
        
        main_cursor.execute("UPDATE global_user_data SET db_luck = %s, db_temp_luck = %s WHERE db_g_user_id = %s", (luck, temp_luck, user_id))
        main_connection.commit()
        
    finally:
        if main_connection:
            main_cursor.close()
            main_connection.close()


class Luck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def daily(self, ctx):
        # Kiểm tra xem người dùng đã nhận daily chưa
        user_id = ctx.author.id
        display_name = ctx.author.nick if ctx.author.nick is not None else ctx.author.display_name
        
        main_connection = await connect_main_db() 
        main_cursor = main_connection.cursor()
        
        main_cursor.execute("SELECT db_user_level, db_last_daily, db_streak_daily FROM global_user_data WHERE db_g_user_id = %s", (user_id,))
        result = main_cursor.fetchone()
        
        # Lấy thời gian reset_daily
        now, reset_daily = await get_reset_daily_time() 
        time_until_reset_seconds = int((reset_daily - now).total_seconds())
        time_until_reset_hours = time_until_reset_seconds // 3600
        time_until_reset_minutes = (time_until_reset_seconds % 3600) // 60
        level, last_daily, streak = result
        
        
        if last_daily is None or now >= reset_daily:
            if last_daily is None or (now - last_daily <= datetime.timedelta(days=1)):
                # Nếu last_daily là None hoặc khoảng thời gian từ lần cuối dùng lệnh ngắn hơn hoặc bằng 1 ngày, cập nhật thời gian và tăng streak
                streak += 1
            else:
                # Nếu lớn hơn một ngày từ lần cuối nhận, reset streak về 0
                streak = 0
            
            await random_luck(user_id, 2, 1) #random luck
            await random_luck(user_id, 2, -1) #reset và random daily luck
            luck, temp_luck = await load_luck(user_id) #load luck mới random
            
            streak_bonus = round(streak * 0.05, 1) #5% trên mỗi streak
            luck_bonus = round(luck * 0.01, 1) 
            temp_luck_bonus = round(temp_luck * 0.01, 1)
            
            if level < 10:
                x = level * 100
            else:
                x = level * (100 * round(level / 10, 1))
            
            formula = x + (streak_bonus * x) + ((luck_bonus * x) + (temp_luck_bonus * x))
            
            raw_reward = round(x,1)
            reward_streak_bonus = round(streak_bonus * x, 1)
            reward_luck_bonus = round(luck_bonus * x, 1)
            reward_temp_luck_bonus = round(temp_luck_bonus * x, 1)
            
            reward = round(formula)
            
            main_cursor.execute("UPDATE global_user_data SET db_last_daily = NOW(), db_wallet = %s, db_streak_daily = %s WHERE db_g_user_id = %s", (reward, streak, user_id))
            main_connection.commit()
            
            await ctx.send(f"Xin chào **{display_name}**, Bạn đã dùng daily của hôm nay! \n"
                        f"Daily luck hôm nay của bạn là **{temp_luck}**\n"
                        f"Luck của bạn là **{luck}** \n"
                        f"Chuỗi streak của bạn hiện tại là **{streak} ngày**! \n"
                        f"\n"
                        f"Quà cơ bản của bạn là **{raw_reward}**<:cash:1151558754614116413> \n"
                        f"Bonus daily luck của bạn là **{round(temp_luck_bonus*100)}%**, bạn được nhận thêm **{reward_temp_luck_bonus}**<:cash:1151558754614116413> \n"
                        f"Bonus luck của bạn là **{round(luck_bonus*100)}%**, bạn được nhận thêm **{reward_luck_bonus}**<:cash:1151558754614116413> \n"
                        f"Bonus streak hiện tại của bạn là **{round(streak_bonus*100)}%**, bạn được nhận thêm **{reward_streak_bonus}**<:cash:1151558754614116413>  \n" 
                        f"Tổng cộng bạn nhận được **{reward}**<:cash:1151558754614116413> quà hàng ngày! \n"
                        f"\n"
                        f"Lần daily kế tiếp là **{time_until_reset_hours} giờ {time_until_reset_minutes} phút** sau(12h hàng ngày).")
        else:
            # Nếu chưa đến lúc reset_daily, thông báo cho người dùng thời gian còn lại
            await ctx.send(f"Bạn đã nhận daily hôm nay và có thể nhận lại sau **{time_until_reset_hours} giờ {time_until_reset_minutes} phút**(12h hàng ngày).")
        
        if main_connection:
            main_cursor.close()
            main_connection.close()

def setup(bot):
    bot.add_cog(Luck(bot))