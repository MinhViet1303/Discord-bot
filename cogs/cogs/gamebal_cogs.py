from nextcord.ext import commands
import random
import asyncio

from cogs.g_def import *


async def get_wallet(user_id):
    main_connection = await connect_main_db()
    
    main_cursor = main_connection.cursor()
    main_cursor.execute("SELECT db_wallet FROM user_data WHERE db_user_id = %s", (user_id,))
    result = main_cursor.fetchall()
    
    if main_connection:
        main_cursor.close()
        main_connection.close()
    
    if result != None:
        return int(result[0][0])
    return 0


async def update_wallet(user_id, amount):
    main_connection = await connect_main_db()

    main_cursor = main_connection.cursor()
    main_cursor.execute("UPDATE user_data SET db_wallet = db_wallet + %s WHERE db_user_id = %s", (amount, user_id))
    main_connection.commit()

    if main_connection:
        main_cursor.close()
        main_connection.close()


async def get_amount(ctx, user_id, amount):
    max_count = 10000
    wallet = await get_wallet(user_id)

    if isinstance(amount, str):
        if amount.lower() == "all":
            # Lấy toàn bộ số cash trong wallet
            amount = min(wallet, max_count)
            if wallet < 1:
                await ctx.send("Số dư của bạn thấp hơn **1**<:cash:1151558754614116413>.")
                return None
        else:
            try:
                # Kiểm tra xem amount có phải là số hay không
                if not amount.isdigit():
                    await ctx.send("Số tiền nhập không hợp lệ!")
                    return None
                amount = int(amount)
                if amount <= max_count and amount > 1:
                    amount = int(min(amount, max_count))
                    if amount > wallet:
                        await ctx.send(f"Số tiền bạn nhập: **{amount}**<:cash:1151558754614116413> lớn hơn số dư trong wallet(**{wallet}**<:cash:1151558754614116413>).")
                        return None
                else:
                    await ctx.send(f"Số tiền nhập tối thiểu là 1<:cash:1151558754614116413> và tối đa không quá **{max_count}**<:cash:1151558754614116413>")
                    return None
            except ValueError:
                await ctx.send("Lỗi ngoại lệ!")
                return None
    else:
        await ctx.send("Số tiền nhập không hợp lệ!")
        return None

    return amount


class GameBal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wallet", aliases=["w"])
    async def wallet(self, ctx):
        user_id = ctx.author.id
        wallet = await get_wallet(user_id)
        await ctx.send(f"Số tiền trong wallet của bạn là **{wallet}**<:cash:1151558754614116413>.")

    @commands.command(name="coinflip", aliases=["cf", "CF"])
    async def coinflip(self, ctx, amount, *sides):
        user_id = ctx.author.id
        display_name = ctx.author.nick if ctx.author.nick is not None else ctx.author.display_name

        amount = await get_amount(ctx, user_id, amount)
        if amount is None:
            return

        if any(side.lower() in ["u", "up"] for side in sides) and any(side.lower() in ["d", "down"] for side in sides):
            await ctx.send("Vui lòng chỉ chọn một trong 'u' (ngửa) hoặc 'd' (úp) khi đặt cược.")
        else:
            if not sides:
                side = "up" 
            else:
                side = sides[0] 
            message = await ctx.send(f"**{display_name}** đã chọn **{'Ngửa' if side.lower() in ['u', 'up'] else 'Úp'}** và đặt cược **{amount}**<:cash:1151558754614116413>. \n"
                        f"Đồng xu đang quay...<a:coin_flip:1151550525838467192>")
            await asyncio.sleep(1.5)
            
            coin_heads = random.randint(0,1)
            
            if (side.lower() in ["u", "up"] and coin_heads == 1) or (side.lower() in ["d", "down"] and coin_heads == 0):
                # Người chơi thắng
                await update_wallet(user_id, amount)
                await message.edit(f"**{display_name}** đã chọn **{'Ngửa' if side.lower() in ['u', 'up'] else 'Úp'}** và đặt cược **{amount}**<:cash:1151558754614116413>.\n"
                        f"Đồng xu ra mặt **{'Ngửa<:CoinUp:1151819782937653258>' if coin_heads == 1 else 'Úp<:CoinDown:1151805929390616638>'}**, bạn đã thắng và nhận **{amount}**<:cash:1151558754614116413>.")
            else:
                # Người chơi thua
                amount = -amount
                await update_wallet(user_id, amount)
                await message.edit(f"**{display_name}** đã chọn **{'Ngửa' if side.lower() in ['u', 'up'] else 'Úp'}** và đặt cược **{-amount}**<:cash:1151558754614116413>.\n"
                        f"Đồng xu ra mặt **{'Ngửa<:CoinUp:1151819782937653258>' if coin_heads == 1 else 'Úp<:CoinDown:1151805929390616638>'}**, bạn đã thua và mất **{-amount}**<:cash:1151558754614116413>.")

    @commands.command(name="set", aliases=["s"])
    async def set(self, ctx, amount):
        user_id = ctx.author.id
        
        main_connection = await connect_main_db()
        
        main_cursor = main_connection.cursor()
        main_cursor.execute("UPDATE user_data SET db_wallet = %s WHERE db_user_id = %s", (amount, user_id))
        main_connection.commit()
        
        await ctx.send(f"Số tiền được set thành {amount}")
        
        if main_connection:
            main_cursor.close()
            main_connection.close()

def setup(bot):
    bot.add_cog(GameBal(bot))