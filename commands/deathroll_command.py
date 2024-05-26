from discord.ext import commands
import random
import asyncio

active_games = set()

def add_deathroll_command(bot):
    @bot.command(name="dr")
    async def deathroll(ctx, member: commands.MemberConverter):
        if ctx.channel.id in active_games:
            await ctx.send("There is already an active game in this channel.")
            return
        
        active_games.add(ctx.channel.id)

        await ctx.send(f"{ctx.author.mention} has challenged {member.mention} to a deathroll!")

        def check(m):
            return m.author in [ctx.author, member] and m.content.lower() == 'dr'
        
        # Challenger's starting roll
        challenger_roll = random.randint(1, 999)
        await ctx.send(f"{ctx.author.mention}, rolls {challenger_roll}!")
        if challenger_roll == 1:
            await ctx.send(f"{ctx.author.mention} loses the deathroll..")
            await ctx.send(f"{member.mention} wins!")
            active_games.remove(ctx.channel.id)
        deathroll = challenger_roll

        # Loop of the game
        while True:
            # Waiting for opponent's response
            await ctx.send(f"{member.mention}, type 'dr' to roll")
            try:
                msg = await bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send(f'{member.mention} did not respond in time..')
                active_games.remove(ctx.channel.id)
                break
            else:
                challenged_roll = random.randint(1, deathroll)
                await ctx.send(f"{member.mention} rolls {challenged_roll}")
                if challenged_roll == 1:
                    await ctx.send(f"{member.mention} loses the deathroll..")
                    await ctx.send(f"{ctx.author.mention} wins!")
                    active_games.remove(ctx.channel.id)
                    break
                deathroll = challenged_roll
            
            # Waiting for challenger's response
            await ctx.send(f"{ctx.author.mention}, type 'dr' to roll")
            try:
                msg = await bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send(f'{ctx.author.mention} did not respond in time..')
                active_games.remove(ctx.channel.id)
                break
            else:
                challenger_roll = random.randint(1, deathroll)
                await ctx.send(f"{ctx.author.mention} rolls {challenger_roll}")
                if challenger_roll == 1:
                    await ctx.send(f"{ctx.author.mention} loses the deathroll..")
                    await ctx.send(f"{member.mention} wins!")
                    active_games.remove(ctx.channel.id)
                    break
                deathroll = challenger_roll