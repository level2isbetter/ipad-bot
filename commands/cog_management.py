import os
import json

from discord.ext import commands
from discord import Embed

with open('active_cogs.json', 'r') as f:
    active_cogs = json.load(f)

class CogManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('active_cogs.json', 'r') as f:
            active_cogs = json.load(f)

    @commands.command()
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def loaded(self, ctx):
        guild_id = str(ctx.guild.id)
        if guild_id not in active_cogs:
            await ctx.send("No cogs loaded.")
            return
        
        all_cogs = [file[:-3] for file in os.listdir("./ipadbot/cogs") if file.endswith(".py")]
        unloaded_cogs = list(set(all_cogs) - set(active_cogs[guild_id]))

        embed = Embed(title="Loaded cogs", description="\n".join(active_cogs[guild_id]), color=0x00ff00)
        embed.add_field(name="Unloaded cogs", value="\n".join(unloaded_cogs), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def gloaded(self, ctx):
        if 'global' not in active_cogs:
            await ctx.send("No cogs are currently loaded globally")
            return
        
        embed = Embed(title="Globally loaded cogs", description="\n".join(active_cogs['global']), color=0x00ff00)
        await ctx.send(embed=embed)
            
    @commands.command()
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def load(self, ctx, cog: str):
        guild_id = str(ctx.guild.id)
        if not os.path.exists(f"./ipadbot/cogs/{cog}.py"):
            await ctx.send(f"cog {cog} does not exist.")
            return
        
        if guild_id in active_cogs and cog in active_cogs[guild_id]:
            await ctx.send(f"cog {cog} is already loaded.")
            return

        if guild_id not in active_cogs:
            active_cogs[guild_id] = []
        active_cogs[guild_id].append(cog)
        await self.bot.load_extension(f"cogs.{cog}")
        with open('active_cogs.json', 'w') as f:
            json.dump(active_cogs, f)

    @commands.command()
    @commands.is_owner()
    async def gload(self, ctx, cog: str):
        active_cogs['global'].append(cog)
        await self.bot.load_extension(f"cogs.{cog}")
        with open('active_cogs.json', 'w') as f:
            json.dump(active_cogs, f)

    @commands.command()
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def unload(self, ctx, cog: str):
        guild_id = str(ctx.guild.id)

        if guild_id not in active_cogs or cog not in active_cogs[guild_id]:
            await ctx.send(f"cog {cog} is already unloaded.")
            return
        
        if guild_id in active_cogs and cog in active_cogs[guild_id]:
            active_cogs[guild_id].remove(cog)
        await self.bot.unload_extension(f"cogs.{cog}")
        with open('active_cogs.json', 'w') as f:
            json.dump(active_cogs, f)

    @commands.command()
    @commands.is_owner()
    async def gunload(self, ctx, cog: str):
        active_cogs['global'].remove(cog)
        await self.bot.unload_extension(f"cogs.{cog}")
        with open('active_cogs.json', 'w') as f:
            json.dump(active_cogs, f)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"reloaded {cog}.")
        except Exception as e:
            await ctx.send(f"could not reload {cog}. error: {e}")

    @commands.Cog.listener()
    async def on_guild_join(guild):
        guild_id = str(guild.id)
        
        if str(guild.id) not in active_cogs:
            active_cogs[guild_id] = []
            with open('active_cogs.json', 'w') as f:
                json.dump(active_cogs, f)

async def setup(bot):
    await bot.add_cog(CogManagement(bot))