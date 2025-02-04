import discord
from discord.ext import commands, tasks
import time

class akry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "./ipadbot/files/akry_count.txt"
        self.count = self.read_count()
        self.start_time = None
        self.timer_running = False

    def read_count(self):
        try:
            with open(self.file_path, "r") as file:
                content = file.read().strip()
                return int(content) if content else 0
        except FileNotFoundError:
            return 0

    def write_count(self):
        with open(self.file_path, "w") as file:
            file.write(str(self.count))

    @commands.command(name="akry")
    async def akry(self, ctx):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            await ctx.send("Started counting...")
        else:
            elapsed_time = int(time.time() - self.start_time)
            self.count += elapsed_time
            self.write_count()
            self.timer_running = False
            await ctx.send(f"akry has made us wait {self.count} total seconds")

async def setup(bot):
    await bot.add_cog(akry(bot))