import discord
import requests, os
import random, asyncio

from discord import Embed
from discord.ext import commands

class pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pokemon(self, ctx, pokemon_name):
        data = self.get_pokemon_info(pokemon_name)
        if data is not None:
            name = data['name']
            abilities = [ability['ability']['name'] for ability in data['abilities']]
            sprite = data['sprites']['front_default']

            embed = Embed(title=name.capitalize(), description=f'Abilities: {abilities}', color=0x3498db)
            embed.set_thumbnail(url=sprite)

            self.add_item(discord.ui.Button(label='Abilities', style=discord.ButtonStyle.primary), embed, abilities)

            await ctx.send(embed=embed)
        else:
            await ctx.send('Could not find information for that pokemon')

    @commands.command()
    async def who(self, ctx):
        pokeid = random.randint(1, 898)
        data = self.get_pokemon_info(pokeid)

        if data is not None:
            name = data['name']
            abilities = [ability['ability']['name'] for ability in data['abilities']]
            sprite = data['sprites']['front_default']

            embed = Embed(title='guess who', color=0x3498db)
            embed.set_thumbnail(url=sprite)

            await ctx.send(embed=embed)

            def check(m):
                return m.content.lower() == name.lower()
            
            try: 
                guess = await self.bot.wait_for('message', check=check, timeout=10.0)
            except asyncio.TimeoutError:
                await ctx.send(f'Out of time! The pokemon is {name.capitalize()}')
            else:
                await ctx.send(f'congrats {guess.author.mention} you got it right :)')

        else:
            await ctx.send('Could not find information for that pokemon')

    def get_pokemon_info(self, pokemon_name):
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}')

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
            
async def setup(bot):
    await bot.add_cog(pokemon(bot))