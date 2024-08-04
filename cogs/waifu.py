import discord
from discord.ext import commands
import requests

WAIFU_SEARCH = 'https://api.waifu.im/search'
headers = {'Accept-Version': 'v5'}

class waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def waifu(self, ctx, *args):
        args = list(args)
        taglist = []
        for arg in args:
            if arg == '--segs':
                segs = True
            else: taglist.append(arg)
        url =  WAIFU_SEARCH
        params = {
                'included_tags': taglist,
                'height': '>=600'
            }
        
        tags = ' '.join(taglist)
        
        print(params)
        output = {}
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
                
            output['link'] = data['images'][0]['url']
            output['sauce'] = data['images'][0]['source']

            image_url = output['link']
            
            await ctx.send(image_url)

        else:
            print('Statsu code: ', response.status_code)

            #response = requests.get('https://api.waifu.im/search')
        #else:
            #response = requests.get(f'https://api.waifu.im/sfw/waifu/{name}')
async def setup(bot):
    await bot.add_cog(waifu(bot))