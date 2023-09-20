import nextcord
from nextcord.ext import commands
import random
import asyncio
import datetime
import pytz

from cogs.g_def import *
from config import *

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=["!"], intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await connect_db()

@bot.slash_command(name='avatar', description="show avatar", guild_ids=bot.default_guild_ids)
async def show_avatar(interaction: nextcord.Interaction, member: nextcord.Member = None):
    if member is None:
        member = interaction.user 
    
    nickname = member.nick or member.display_name
    avatar_url = member.display_avatar.url if member.display_avatar else member.default_avatar.url
    
    embed = nextcord.Embed(
        title=f"Info {nickname}:",
        description=f"**`Avatar: {nickname}`**\n ",
        color=member.top_role.color
    )
    embed.set_author(name=nickname, icon_url=bot.user.display_avatar.url)
    embed.set_image(url=avatar_url)
    
    await interaction.response.send_message(embed=embed)


@bot.command(name='avatar', aliases=['avt'])
async def show_avatar(ctx, member: nextcord.Member = None):
    if member is None:
        member = ctx.author 
    
    nickname=member.nick
    if nickname is None:
        nickname=member.display_name

    avatar_url = member.display_avatar.url if member.display_avatar else member.default_avatar.url
    
    embed = nextcord.Embed(title="Info {}:".format(member.nick),
                        description="**`Avatar: {0}`**\n ".format(nickname),
                        color = member.top_role.color)
    embed.set_author(name=nickname, icon_url=bot.user.display_avatar)
    embed.set_image(url=avatar_url)
    await ctx.channel.send(embed=embed)



# Chạy bot
bot.run(TOKEN)
