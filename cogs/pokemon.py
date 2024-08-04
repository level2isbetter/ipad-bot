import discord
import requests, os
import random, asyncio
import json

from discord import Embed
from discord.ext import commands

class pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.points_file = './ipadbot/data/points.json'
        try:
            with open(self.points_file, 'r') as f:
                self.points = json.load(f)
        except FileNotFoundError:
            self.points = {}

    @commands.command()
    async def pokemon(self, ctx, pokemon_name):
        data = self.get_pokemon_info(pokemon_name)
        if data is not None:
            name = data['name']
            abilities = [ability['ability']['name'] for ability in data['abilities']]
            sprite = data['sprites']['front_default']

            embed = Embed(title=name.capitalize(), description=f'Abilities: {abilities}', color=0x3498db)
            embed.set_thumbnail(url=sprite)

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
                user_id = str(guess.author.id)
                if user_id in self.points:
                    self.points[user_id] += 1
                    await ctx.send(f'{guess.author.mention} now has {self.points[user_id]} points')
                else:
                    self.points[user_id] = 1
                    await ctx.send(f'{guess.author.mention} now has {self.points[user_id]} points')
                with open('./ipadbot/data/points.json', 'w') as f:
                    json.dump(self.points, f)

        else:
            await ctx.send('Could not find information for that pokemon')
        
    @commands.command()
    async def points(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.points:
            await ctx.send(f'{ctx.author.mention} you have {self.points[user_id]} points')

    def get_pokemon_info(self, pokemon_name):
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}')

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
            
async def setup(bot):
    await bot.add_cog(pokemon(bot))