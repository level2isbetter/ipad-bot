import discord
import random

from discord.ext import commands

class gaydar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded cog: {__name__[5:]}')

    @commands.command()
    async def gaydar(self, ctx, member: discord.Member = None):
        ratenum = random.randint(0,100)
        if member == None:
            message = str(f'You are {ratenum}% gay')
        elif member.id == 132671044472406017:
            message = str(f'is that {member.mention}?? hes the gayest of them all.. 10000000000% gay')
        else:
            message = str(f'{member.mention} is {ratenum}% gay')
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(gaydar(bot))