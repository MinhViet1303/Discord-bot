from nextcord.ext import commands
import random
import asyncio
import mysql.connector

from cogs.g_def import connect_db, connect_main_db, update_global_data
from cogs.luck_cogs import load_luck
from cogs.gamebal_cogs import get_wallet

random.seed()


async def calculate_exp_need(user_id, lv, luck, temp_luck):
    luck_buff = luck / 2
    temp_luck_buff = temp_luck / 2
    
    luck_bonus = luck
    temp_luck_bonus = temp_luck
    
    x = random.uniform(0.8,1.2)
    
    if lv <= 5:
        lv += 5
    
    raw = (lv**2) * (lv ** 2)
    buff = (lv / 1000) * (luck_buff + temp_luck_buff)
    bonus = lv * (-luck_bonus + -temp_luck_bonus)
    
    exp_needed = (raw * x) + round(buff * bonus, 2)
    limit_max = raw * 1.25
    limit_min = raw * 0.75
    
    # Số lần kiểm tra tối đa
    max_attempts = 10
    attempts = 0
    
    while not (limit_min <= exp_needed <= limit_max) and attempts < max_attempts:
        exp_needed = (raw * x) + round(buff * bonus, 2)
        attempts += 1
    
    # Nếu vẫn không nằm trong giới hạn, sử dụng min và max
    if exp_needed < limit_min:
        exp_needed = limit_min * x
    elif exp_needed > limit_max:
        exp_needed = limit_max * x
    
    exp_needed = round(exp_needed, 2)
    
    if exp_needed.is_integer():
        exp_needed = int(exp_needed)
    
    return exp_needed

async def calculate_exp(lv, luck, temp_luck, exp_need):
    luck_buff = luck / 10
    temp_luck_buff = temp_luck / 10
    
    luck_bonus = luck
    temp_luck_bonus = temp_luck
    
    x = random.uniform(0.8,1.2)
    
    if lv <= 5:
        lv += 5
    
    a = round(random.uniform(-0.5, 1), 1)
    b = round(random.uniform(1, 2), 1)
    c = random.randint(-9, 9)
    
    raw = abs(round(((a * lv) * (lv ** 2)) + (b * lv) + c, 2))
    buff =  (luck_buff + temp_luck_buff)
    bonus = lv * (luck_bonus + temp_luck_bonus)
    
    exp = ((raw * x) * buff) + bonus
    
    limit_max = exp_need * 0.025
    limit_min = exp_need * 0.01
    
    # Số lần kiểm tra tối đa
    max_attempts = 10
    attempts = 0
    
    while not (limit_min <= exp <= limit_max) and attempts < max_attempts:
        exp = (raw * x) + round(buff * bonus, 2)
        attempts += 1
    
    # Nếu vẫn không nằm trong giới hạn, sử dụng min và max
    if exp < limit_min:
        exp = limit_min * x
    elif exp > limit_max:
        exp = limit_max * x
    
    exp = round(exp, 2)
    
    if exp.is_integer():
        exp = int(exp)
    
    return exp


# Hàm tăng cấp người dùng
async def level_up(message, user_id):
    display_name = message.author.nick if message.author.nick is not None else message.author.display_name
    main_connection = await connect_main_db()
    main_cursor = main_connection.cursor()
    
    try:
        main_cursor.execute('SELECT db_exp, db_user_level, db_exp_need FROM global_user_data WHERE db_g_user_id = %s', (user_id,))
        user_data = main_cursor.fetchone()
        
        exp = user_data[0]
        lv = user_data[1]
        exp_need = float(user_data[2])
        
        luck, temp_luck = await load_luck(user_id)
        wallet = await get_wallet(user_id)
        
        if exp_need == 0:
            exp_need = await calculate_exp_need(user_id, lv, luck, temp_luck)
        
        exp_new = await calculate_exp(lv, luck, temp_luck, exp_need)
        exp += exp_new
        
        while exp >= exp_need:
            lv += 1
            exp -= exp_need
            exp_need = await calculate_exp_need(user_id, lv, luck, temp_luck)
            
            temp_luck_bonus = round(temp_luck * 0.01, 2)
            luck_bonus = round(luck * 0.01, 2) 
            
            if lv < 10:
                raw_reward = lv * 100
            else:
                raw_reward = lv * (500 * round(lv / 20, 1))
            
            bonus = (luck_bonus  + temp_luck_bonus) 
            reward_bonus = bonus * (raw_reward/2)
            reward = raw_reward + reward_bonus
            
            if reward.is_integer():
                reward = int(reward)
            else:
                reward = round(reward,2)
            wallet += reward
            
            if message.channel.id != 879185402404143144:
                await message.channel.send(f"Xin chào **{display_name}**, chúc mừng bạn đã lên level, level hiện tại của bạn là **{lv}**! \n"
                            f"Daily luck hôm nay của bạn là **{temp_luck}**\n"
                            f"Luck của bạn là **{luck}** \n"
                            f"\n"
                            f"Quà cơ bản của bạn là **{raw_reward}**<:cash:1151558754614116413> \n"
                            f"Bonus luck của bạn là **{round(bonus*100)}%**, bạn {'không nhận được bonus' if luck_bonus == 0 else '**nhận thêm**' if luck_bonus > 0 else '**mất**'} **{round(reward_bonus)}**<:cash:1151558754614116413> \n"
                            f"Tổng cộng bạn nhận được **{reward}**<:cash:1151558754614116413> quà lên cấp! \n")
            
        main_cursor.execute('UPDATE global_user_data SET db_exp = %s, db_exp_need = %s, db_user_level = %s, db_wallet = %s WHERE db_g_user_id = %s', (exp, exp_need, lv, wallet, user_id))
        main_connection.commit()
    except mysql.connector.Error as err:
        print(f"Lỗi: {err} user_level_cogs.py")
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

def setup(bot):
    bot.add_cog(User_Levelling(bot))
