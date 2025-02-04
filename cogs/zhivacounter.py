import discord
from discord.ext import commands

class ZhivaCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "./ipadbot/files/zhiva_count.txt"
        self.count = self.read_count()

    def read_count(self):
        try:
            with open(self.file_path, "r") as file:
                return int(file.read().strip())
        except FileNotFoundError:
            return 0

    def write_count(self):
        with open(self.file_path, "w") as file:
            file.write(str(self.count))

    @commands.command(name="zhiva")
    async def zhiva(self, ctx):
        self.count += 1
        self.write_count()
        await ctx.send(f"Zhiva has complained {self.count} times")

async def setup(bot):
    await bot.add_cog(ZhivaCounter(bot))