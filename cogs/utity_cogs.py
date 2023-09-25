import nextcord
import nextcord.ui
from nextcord.ext import commands
import random
import datetime
import os

from cogs.g_def import connect_db, connect_main_db, get_reset_daily_time
from cogs.gamebal_cogs import update_wallet

random.seed()

#auto load cogs
async def auto_load_cogs(bot, ctx = None, action = None):
    print("================================")
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
    print("================================")


async def load_prefix(new_prefixes=None):
    main_connection = await connect_main_db()
    main_cursor = main_connection.cursor()

    default_data = ["EP", "!"]

    if new_prefixes is None:
        main_cursor.execute("SELECT db_utity_value FROM utity WHERE db_utity_name = 'prefix'")
        result = main_cursor.fetchone()

        if result is None:
            # Nếu không có giá trị nào trong cơ sở dữ liệu, sử dụng giá trị mặc định
            main_cursor.execute("INSERT INTO utity (db_utity_name, db_utity_value) VALUES (%s, %s)", ('prefix', ','.join(default_data)))
            main_connection.commit()
            return default_data
        else:
            # Chuyển chuỗi giá trị thành danh sách
            return [value.strip() for value in result[0].split(",")]
    else:
        # Chuyển danh sách giá trị thành chuỗi
        new_prefixes = ','.join(new_prefixes)
        main_cursor.execute("UPDATE utity SET db_utity_value = %s WHERE db_utity_name = 'prefix'", (new_prefixes,))
        main_connection.commit()

    if main_connection:
        main_cursor.close()
        main_connection.close()


class Utity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pick(self, ctx, *args):
        
        if not args:
            await ctx.send("Vui lòng cung cấp ít nhất hai lựa chọn.")
            return

        choices_str = ' '.join(args)
        choices_list = [choice.strip() for choice in choices_str.split(',')]

        if len(choices_list) < 2:
            await ctx.send("Vui lòng cung cấp ít nhất hai lựa chọn.")
        else:
            chosen_item = random.choice(choices_list)
            await ctx.send(f"{chosen_item}")

    @commands.command()
    async def daily(self, ctx):
        # Kiểm tra xem người dùng đã nhận daily chưa
        user_id = ctx.author.id
        display_name = ctx.author.nick if ctx.author.nick is not None else ctx.author.display_name

        main_connection = await connect_main_db() 
        main_cursor = main_connection.cursor()

        main_cursor.execute("SELECT db_level, db_last_daily, db_streak_daily FROM global_user_data WHERE db_g_user_id = %s", (user_id,))
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
            
            streak_bonus = 0.05 * streak
            if level < 10:
                x = level * 100
                reward = x + (streak_bonus * x)
            else:
                x = level * (100 * (level // 10))
                reward = x + (streak_bonus * x)
            
            main_cursor.execute("UPDATE global_user_data SET db_last_daily = NOW(), db_wallet = %s, db_streak_daily = %s WHERE db_g_user_id = %s", (reward, streak, user_id))
            main_connection.commit()
            await ctx.send(f"**{display_name}**, Bạn đã nhận được **{int(reward)}**<:cash:1151558754614116413> quà hàng ngày! \n"
                        f"Chuỗi streak của bạn hiện tại là **{streak} ngày**! \n"
                        f"Bonus streak hiện tại của bạn là **{round(streak_bonus*100)}%**! \n"  
                        f"Lần daily kế tiếp là **{time_until_reset_hours} giờ {time_until_reset_minutes} phút** sau(12h hàng ngày).")
        else:
            # Nếu chưa đến lúc reset_daily, thông báo cho người dùng thời gian còn lại
            await ctx.send(f"Bạn đã nhận daily hôm nay và có thể nhận lại sau **{time_until_reset_hours} giờ {time_until_reset_minutes} phút**(12h hàng ngày).")

    class Confirm_send(nextcord.ui.View):
        def __init__(self, ctx, member, amount, user_display, member_display):
            super().__init__()
            self.value = None    
            self.ctx = ctx
            self.member = member
            self.amount = amount
            
            self.user_display = user_display
            self.member_display = member_display

        @nextcord.ui.button(label= "Đồng ý✅", style=nextcord.ButtonStyle.green)
        async def button1(self, button: nextcord.ui.button, interaction: nextcord.Integration):
            await interaction.response.edit_message(content=f"**{self.user_display}** đã gửi **{self.amount}**<:cash:1151558754614116413> cho **{self.member_display}**")
            await update_wallet(self.ctx.author.id, -int(self.amount))
            await update_wallet(self.member.id, self.amount)
            await interaction.edit(view=None)

        @nextcord.ui.button(label= "Từ chối❌", style=nextcord.ButtonStyle.red)
        async def button2(self, button: nextcord.ui.button, interaction: nextcord.Integration):
            await interaction.response.edit_message(content=f"Đã hủy!")
            await interaction.edit(view=None)

    @commands.command()
    async def send(self, ctx, member: nextcord.Member, amount, hiden = None):
        user_id = ctx.author.id
        user_display = ctx.author.mention
        member_display = member.mention

        if hiden in ["hiden", "h"]:
            user_display = ctx.author.nick if ctx.author.nick is not None else ctx.author.display_name
            member_display = member.nick if member.nick is not None else member.display_name

        # amount = await get_amount(ctx, user_id, amount)
        view = self.Confirm_send(ctx, member, amount, user_display, member_display)
        # Kiểm tra nếu người gửi là bot hoặc người gửi chính mình
        if member.bot or member.id == user_id:
            await ctx.send("Bạn không thể gửi tiền cho bot hoặc chính mình.")
            return

        await ctx.send(f"**{user_display}**, bạn có chắc chắn muốn gửi {amount} tiền đến **{member_display}**? Để xác nhận, hãy ấn ✅. Để hủy, hãy ấn ❌.", view = view)
        await view.wait()


    @commands.command()
    async def cogs(self, ctx, action, cog_name = None):
        if cog_name is not None:
            cog_name = cog_name.lower()  

            if cog_name.endswith("cogs"):
                cog_name1 = f'cogs.{cog_name}'
            else:
                cog_name1 = f'cogs.{cog_name}_cogs'
            
            cog_name2 = cog_name1.replace("cogs.", "")
        
        if cog_name is None and action in ["reloadall", "reload_all", "rall", "r_all"]:
            await auto_load_cogs(self.bot, ctx, action)
        
        elif action in ["load", "+", "l"]:
            if cog_name1 not in self.self.bot.extensions:
                self.bot.load_extension(cog_name1)
                await ctx.send(f'Loaded cog: **{cog_name2}**')
                print (f'Loaded cog: {cog_name2}.py')
                print("============================")
            else:
                await ctx.send(f'Cog **{cog_name2}** đã đang load!')
        
        elif action in ["unload", "-", "unl"]:
            if cog_name1 in self.bot.extensions:
                self.bot.unload_extension(cog_name1)
                await ctx.send(f'Unloaded cog: **{cog_name2}**')
                print (f'Unloaded cog: {cog_name2}.py')
                print("==============================")
            else:
                await ctx.send(f'Không có cog nào tên **{cog_name2}** đang load!')
        
        elif action in ["reload", "r"]:
            if cog_name1 in self.bot.extensions:
                self.bot.unload_extension(cog_name1)
                self.bot.load_extension(cog_name1)
                await ctx.send(f'Reload cog: **{cog_name2}**')
                print (f'Reload cog: {cog_name2}.py')
                print("============================")
            else:
                self.bot.load_extension(cog_name1)
                await ctx.send(f'Loaded cog: **{cog_name2}**')
                print (f'Loaded cog: {cog_name2}.py')
                print("============================")
        
        else:
            await ctx.send("Lỗi cú pháp lệnh!")

    @commands.command(name="prefix", aliases=["Prefix"])
    async def prefix(self, ctx, action: str = None, prefix_1=None, prefix_2=None):
        if action is None:
            # Đọc giá trị prefix từ cơ sở dữ liệu MariaDB
            prefixes = await load_prefix()
            prefix_list = ', '.join(prefixes)
            await ctx.send(f'Danh sách prefix hiện tại: **{prefix_list}**')
        elif action in ['change', 'c']:
            if prefix_1 and prefix_2:
                # Đọc giá trị prefix từ cơ sở dữ liệu MariaDB
                prefixes = await load_prefix()
                if prefix_1 not in prefixes:
                    await ctx.send(f'Không thể tìm thấy prefix: `{prefix_1}`.')
                else:
                    prefix_1_index = prefixes.index(prefix_1)
                    if prefix_2 in prefixes:
                        await ctx.send(f'Prefix `{prefix_2}` đã tồn tại và sẽ thay thế prefix `{prefix_1}`.')
                        prefixes.remove(prefix_1)
                    else:
                        await ctx.send(f'Đã đổi prefix từ `{prefix_1}` thành `{prefix_2}`')
                    prefixes[prefix_1_index] = prefix_2
                    # Lưu giá trị prefix mới vào cơ sở dữ liệu MariaDB
                    await load_prefix(prefixes)
            else:
                await ctx.send('Hãy cung cấp cả "old_prefix" và "new_prefix" để thực hiện thay đổi.')
        elif action in ['add', 'a', '+']:
            new_prefix = prefix_1
            # Đọc giá trị prefix từ cơ sở dữ liệu MariaDB
            prefixes = await load_prefix()
            if new_prefix in prefixes:
                await ctx.send('Prefix đã tồn tại!')
            else:
                prefixes.append(new_prefix)
                await ctx.send(f'Prefix `{new_prefix}` đã được thêm.')
                # Lưu giá trị prefix mới vào cơ sở dữ liệu MariaDB
                await load_prefix(prefixes)
        elif action in ['remove', 'r', '-']:
            prefix_to_remove = prefix_1
            if prefix_to_remove in ['all', 'clear']:
                prefixes = ["EP ", "!"]
                await ctx.send('Tất cả các prefix đã bị xóa. Prefix mặc định được đặt thành `EP ` và `!`')
                # Lưu giá trị prefix mới vào cơ sở dữ liệu MariaDB
                await load_prefix(prefixes)
            elif prefix_to_remove in prefixes:
                prefixes.remove(prefix_to_remove)
                await ctx.send(f'Đã xóa prefix: `{prefix_to_remove}`!')
                # Lưu giá trị prefix mới vào cơ sở dữ liệu MariaDB
                await load_prefix(prefixes)
            else:
                await ctx.send(f'Không thể tìm thấy prefix: `{prefix_to_remove}`')
        elif action == "clear":
            prefixes = ["EP ", "!"]
            await ctx.send('Tất cả các prefix đã bị xóa. Prefix mặc định được đặt thành `EP ` và `!`')
            # Lưu giá trị prefix mới vào cơ sở dữ liệu MariaDB
            await load_prefix(prefixes)
        else:
            await ctx.send('Sai cú pháp câu lệnh!')


def setup(bot):
    bot.add_cog(Utity(bot))