import nextcord
from nextcord.ext import commands

from cogs.g_def import connect_main_db

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='avatar', aliases=['avt'])
    async def show_avatar(self, ctx, member: nextcord.Member = None):
        if member is None:
            member = ctx.author 
        
        nickname=member.nick
        if nickname is None:
            nickname=member.display_name
        
        avatar_url = member.display_avatar
        if avatar_url is None:
            avatar_url = member.default_avatar
        
        embed = nextcord.Embed(title="Info {}:".format(member.nick),
                            description="**Avatar: {0}**\n ".format(nickname),
                            color = member.top_role.color)
        embed.set_author(name=nickname, icon_url=self.bot.user.display_avatar)
        embed.set_image(url=avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.command(name='info', aliases=["Info"])
    async def info(self, ctx, member: nextcord.Member = None):
        if member is None:
            member = ctx.author
        
        user_id = member.id
        
        nickname = member.nick
        if nickname is None:
            nickname = None #member.display_name
        
        main_connection = await connect_main_db() 
        main_cursor = main_connection.cursor()
        
        main_cursor.execute("SELECT db_user_level, db_luck, db_temp_luck, db_exp, db_exp_need  FROM global_user_data WHERE db_g_user_id = %s", (user_id,))
        result = main_cursor.fetchone()
        
        lv = result[0]
        luck = result[1]
        daily_luck = result[2]
        exp = round(result[3])
        exp_need = round(result[4])
        
        created_at = member.created_at.strftime("%d/%m/%Y %H:%M:%S.%f")[:-7]
        joined_at = member.joined_at.strftime("%d/%m/%Y %H:%M:%S.%f")[:-7]
        
        listroles = [role.name for role in member.roles]
        roles = ", ".join(listroles)
        
        avatar_url = member.display_avatar
        if avatar_url is None:
            avatar_url = member.default_avatar
        # Create an embed with the user's avatar
        embed_title = f"Thông tin của {member.nick}:"
        embed_description = (f"> **Status: {member.status}**\n"
                            f"============================ \n"
                            f"**User name: {member.name}**\n"
                            f"**Nick name: {nickname}**\n"
                            f"**ID: {member.id}**\n"
                            f"============================ \n"
                            f"**Lv hiện tại của `{member.display_name}` là `{lv}`!**\n"
                            f"**Exp/Exp_need: **\n"
                            f"**`{exp}`/`{exp_need}`({round((exp/exp_need)*100)}%)**\n"
                            f"============================ \n"
                            f"**Luck hiện tại là `{luck}`!**\n"
                            f"**Daily luck hiện tại là `{daily_luck}`!**\n"
                            f"============================ \n"
                            f"**Ngày tạo tài khoản: `{created_at}`**\n"
                            f"**Ngày tham gia vào server: `{joined_at}`**\n"
                            f"============================ \n"
                            f"**Avatar của {member.display_name}: **\n")
        embed_color = member.top_role.color
        embed_thumbnail_url = avatar_url
        embed_image_url = avatar_url
        embed_author_name = member.nick
        embed_author_icon_url = self.bot.user.display_avatar
        
        embed = nextcord.Embed(title=embed_title, description=embed_description, color=embed_color)
        embed.set_thumbnail(url=embed_thumbnail_url)
        embed.set_image(url=embed_image_url)
        embed.set_author(name=embed_author_name, icon_url=embed_author_icon_url)
        
        await ctx.channel.send(embed=embed)
        
        if main_connection:
            main_cursor.close()
            main_connection.close()



def setup(bot):
    bot.add_cog(Info(bot))