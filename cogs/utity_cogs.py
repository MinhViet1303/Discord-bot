import nextcord
import nextcord.ui
from nextcord.ext import commands
import random
import datetime
import pytz

from cogs.g_def import connect_db, connect_main_db
from cogs. gamebal_cogs import update_wallet

random.seed()

# Define một hàm để lấy thời gian reset_daily
def get_reset_daily_time():
    # Tạo múi giờ +7
    tz = pytz.timezone('Asia/Ho_Chi_Minh')  # Điều chỉnh múi giờ tùy theo vị trí của bạn
    
    # Lấy thời gian hiện tại và đặt giờ thành 12:00 trưa
    now = datetime.datetime.now(tz)
    reset_daily = now.replace(hour=12, minute=0, second=0, microsecond=0)
    
    # Nếu thời gian hiện tại đã vượt qua thời gian reset_daily, thì cộng thêm 1 ngày
    if now >= reset_daily:
        reset_daily += datetime.timedelta(days=1)
    
    return now, reset_daily



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

        main_cursor.execute("SELECT db_level, db_last_daily, db_streak_daily FROM user_data WHERE db_user_id = %s", (user_id,))
        result = main_cursor.fetchone()

        # Lấy thời gian reset_daily
        now, reset_daily = get_reset_daily_time() 
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
            
            main_cursor.execute("UPDATE user_data SET db_last_daily = NOW(), db_wallet = %s, db_streak_daily = %s WHERE db_user_id = %s", (reward, streak, user_id))
            main_connection.commit()
            await ctx.send(f"**{display_name}**, Bạn đã nhận được **{int(reward)}**<:cash:1151558754614116413> quà hàng ngày! \n"
                        f"Chuỗi streak của bạn hiện tại là **{streak} ngày**! \n"
                        f"Bonus streak hiện tại của bạn là **{round(streak_bonus*100)}%**! \n"  
                        f"Lần daily kế tiếp là **{time_until_reset_hours} giờ {time_until_reset_minutes} phút** sau(12h hàng ngày).")
        else:
            # Nếu chưa đến lúc reset_daily, thông báo cho người dùng thời gian còn lại
            await ctx.send(f"Bạn đã nhận daily hôm nay và có thể nhận lại sau **{time_until_reset_hours} giờ {time_until_reset_minutes} phút**(12h hàng ngày).")

    class Confirm_send(nextcord.ui.View):
        def __init__(self, ctx, member, amount):
            super().__init__()
            self.value = None    
            self.ctx = ctx
            self.member = member
            self.amount = amount
            
            self.user_display_name = self.ctx.author.nick if self.ctx.author.nick is not None else self.ctx.author.display_name
            self.member_display_name = self.member.author.nick if self.member.author.nick is not None else self.member.author.display_name

        @nextcord.ui.button(label= "Đồng ý✅", style=nextcord.ButtonStyle.green)
        async def button1(self, button: nextcord.ui.button, interaction: nextcord.Integration):
            await interaction.response.edit_message(content=f"{self.user_display_name} đã gửi **{self.amount}**<:cash:1151558754614116413> cho {self.member_display_name}")
            await update_wallet(self.ctx.author.id, -int(self.amount))
            await update_wallet(self.member.id, self.amount)

        @nextcord.ui.button(label= "Từ chối❌", style=nextcord.ButtonStyle.red)
        async def button2(self, button: nextcord.ui.button, interaction: nextcord.Integration):
            await interaction.response.edit_message(content=f"Đã hủy!")

    @commands.command()
    async def send(self, ctx, member: nextcord.Member, amount):
        user_id = ctx.author.id

        # amount = await get_amount(ctx, user_id, amount)
        view = self.Confirm_send(ctx, member, amount)
        # Kiểm tra nếu người gửi là bot hoặc người gửi chính mình
        if member.bot or member.id == user_id:
            await ctx.send("Bạn không thể gửi tiền cho bot hoặc chính mình.")
            return

        await ctx.send(f"{ctx.author.mention}, bạn có chắc chắn muốn gửi {amount} tiền đến {member.mention}? Để xác nhận, hãy ấn ✅. Để hủy, hãy ấn ❌.", view = view)
        await view.wait()






def setup(bot):
    bot.add_cog(Utity(bot))