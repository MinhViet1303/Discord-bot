from nextcord.ext import commands
import json

from config import *

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(prefix_path, 'r') as f:
            self.prefixes = json.load(f)['prefixes']
    
    def save_prefixes(self):
        with open(prefix_path, 'w') as f:
            json.dump({'prefixes': self.prefixes}, f)
        self.bot.command_prefix = self.prefixes

    @commands.command(name="prefix", aliases=["Prefix", None])
    async def prefix(self, ctx, action: str = None, *, args = None):
        if action is not None:
            args = ctx.message.content[len(ctx.prefix + action):].split(" ")
            args = args[-2:]

        if action is None:
            prefix_list = ', '.join(self.prefixes)
            await ctx.send(f'Danh sách prefix hiện tại: **{prefix_list}**')
        elif action in ['change', 'c']:
            old_prefix, new_prefix = args
            if old_prefix not in self.prefixes:
                await ctx.send(f'Không thể tìm thấy prefix: `{old_prefix}`.')
                return
            self.prefixes.remove(old_prefix)
            self.prefixes.append(new_prefix)
            await ctx.send(f'Đã đổi prefix từ `{old_prefix}` thành `{new_prefix}`')
        elif action in ['add', 'a', '+']:
            new_prefix = args[-1]
            if new_prefix in self.prefixes:
                await ctx.send('Prefix đã tồn tại!')
            else:
                self.prefixes.append(new_prefix)
                await ctx.send(f'Prefix `{new_prefix}` added')
        elif action in ['remove', 'r', '-']:
            prefix_to_remove = args[-1]
            if prefix_to_remove in ['all', 'clear']:
                self.prefixes = ["EP ", "!"]
                await ctx.send('Tất cả các prefix đã bị xóa. Prefix mặc định được đặt thành `EP ` và `!`')
            elif prefix_to_remove in self.prefixes:
                self.prefixes.remove(prefix_to_remove)
                await ctx.send(f'Đã xóa prefix: `{prefix_to_remove}`!')
            else:
                await ctx.send(f'Không thể tìm thấy prefix: `{prefix_to_remove}`')
        elif action == "clear":
            self.prefixes = ["EP ", "!"]
            await ctx.send('Tất cả các prefix đã bị xóa. Prefix mặc định được đặt thành `EP ` và `!`')
        else:
            await ctx.send('Sai cú pháp câu lệnh!')
        self.save_prefixes()

def setup(bot):
    bot.add_cog(Prefix(bot))

