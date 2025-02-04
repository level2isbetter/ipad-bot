import discord
from discord.ext import commands

class ClaireCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "./ipadbot/files/claire_count.txt"
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

    @commands.command(name="claire")
    async def claire(self, ctx):
        self.count += 1
        self.write_count()
        await ctx.send(f"Claire has quit {self.count} times")

async def setup(bot):
    await bot.add_cog(ClaireCounter(bot))