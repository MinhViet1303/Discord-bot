from nextcord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("**<@!687325973309423680>**")

def setup(bot):
    bot.add_cog(Test(bot))