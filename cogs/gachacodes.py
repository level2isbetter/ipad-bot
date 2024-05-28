import requests
import discord

from bs4 import BeautifulSoup
from discord.ext import commands

def fetch_codes(game: str):
    if game.lower() == "genshin":
        url = "https://www.gamesradar.com/genshin-impact-codes-redeem/"
    elif game.lower() == "honkai":
        url = "https://www.gamesradar.com/honkai-star-rail-codes-redeem/"
    elif game.lower() == "wuwa":
        url = "https://wutheringwaves.gg/codes/"
    else:
        return "invalid game"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    if game.lower() == "genshin":
        codes = [li.strong.text for li in soup.find_all('li') if li.strong]
    elif game.lower() == "honkai":
        codes = [li.strong.text for li in soup.find_all('li') if li.strong and ' ' not in li.strong.text]
    elif game.lower() == "wuwa":
        codes = [td.strong.text for td in soup.find_all('td') if td.strong and ' ' not in td.strong.text]
    return codes

class get(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get(self, ctx, game: str):
        codes = fetch_codes(game)
        if codes == "invalid game":
            await ctx.send("Invalid game")
        else:
            await ctx.send("\n".join(codes))

async def setup(bot):
    await bot.add_cog(get(bot))