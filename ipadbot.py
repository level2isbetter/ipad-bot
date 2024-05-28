import discord, asyncio, os, json
import praw, instaloader, random
import requests
import re

from discord.ext import commands, tasks

from commands.translate_command import add_translate_command
from commands.deathroll_command import add_deathroll_command
from commands.helpcommand import CustomHelpCommand

from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

intents = discord.Intents.default()
intents.message_content = True

reddit = praw.Reddit(
    client_id="YOUR_ID_HERE",
    client_secret="YOUR_KEY_HERE",
    user_agent="ipad bot v1 by /u/level2isbetter"
)

def get_media_url(reddit_link):
    submission = reddit.submission(url=reddit_link)
    if not submission.is_video:
        return None, None

    video_url = submission.media['reddit_video']['fallback_url']
    audio_url = video_url.split('DASH_')[0] + 'DASH_AUDIO_128.mp4'
    return video_url, audio_url

def compress_video(video_path, output_path, target_size):
    clip = VideoFileClip(video_path)
    target_bitrate = (target_size * 1024 * 8) / clip.duration

    clip.write_videofile(output_path, bitrate=f"{int(target_bitrate)}k")

url_mappings = {
    'https://x.com': 'https://fixupx.com',
    'https://twitter.com': 'https://fxtwitter.com',
    'https://www.tiktok.com': 'https://www.vxtiktok.com',
    'https://www.instagram.com': 'https://www.ddinstagram.com'
}

# Create a bot instance
bot = commands.Bot(command_prefix='.', intents=intents, case_insensitive=True)

with open('active_cogs.json', 'r') as f:
    active_cogs = json.load(f)

add_translate_command(bot) # Importing the translation command
add_deathroll_command(bot) # Importing the deathroll command
bot.help_command = CustomHelpCommand()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='.zoom'))
    for guild in bot.guilds:
        guild_id = str(guild.id)
        if guild_id in active_cogs:
            for cog in active_cogs[guild_id]:
                if os.path.exists(f"./ipadbot/cogs/{cog}.py") and f"cogs.{cog}" not in bot.extensions:
                    await bot.load_extension(f"cogs.{cog}")

    if 'global' in active_cogs:
        for cog in active_cogs['global']:
            if os.path.exists(f"./ipadbot/cogs/{cog}.py") and f"cogs.{cog}" not in bot.extensions:
                await bot.load_extension(f"cogs.{cog}")
    #for filename in os.listdir("./ipadbot/cogs"):
        #if filename.endswith(".py"):
            #await bot.load_extension(f"cogs.{filename[:-3]}")
            #print(f"cog successfully loaded: {filename[:-3]}")

    
    await bot.load_extension("commands.cog_management")

    print('Loaded cogs: ')
    for cog in bot.extensions:
        print(cog)
    print(f'We have logged in as {bot.user}')

# Logout command
@bot.command()
@commands.is_owner()
async def logout(ctx):
    await ctx.send('Logging out...')
    await bot.close()

# Simple hello command
@bot.command()
async def hello(ctx):
    await ctx.send('hi its me ipadbot')

@bot.command()
async def bust(ctx):
    await ctx.send('https://tenor.com/view/cum-gif-20534148')

# A mod command to batch clear messages
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <0 or amount > 100:
        await ctx.send('Please provide a number between 1 and 100')
    else:
        await ctx.channel.purge(limit=amount+1)

# Notifies if a user edited their message
#@bot.event
#async def on_message_edit(before, after):
#    await before.channel.send(f'{before.author} edited their message from "{before.content}" to "{after.content}"')

# Notifies if a user deleted their message
#@bot.event
#async def on_message_delete(message):
#    await message.channel.send(f'{message.author} deleted their message: "{message.content}"')

# Random react when the bot is mentioned
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.add_reaction("<a:duckass:1235423421974712402>") # You can change this to any emoji, in the same format (the a at the start means its animated)
    elif '<:akrystare:1242920601228808263>' in message.content:
        await message.add_reaction('<:stare:1242919781464543322>')
        await message.reply('<:stare:1242919781464543322>')
    if message.author.id == 132671044472406017 or message.author.id == 109914416207646720 or message.author.id == 92772792906309632:
        rreact = random.randint(1,20)
        if rreact < 3:
            await message.add_reaction("<a:duckass:1235423421974712402>")
    elif message.author.id == 120666750835490819:
        emojis = ["🇱", "🇪", "🇸", "🇧", "🇮", "🇦", "🇳"]
        kreact = random.randint(1,20)
        if kreact == 1:
            for emoji in emojis:
                await message.add_reaction(emoji)

    for original_url, new_url in url_mappings.items():
        if original_url in message.content:
            new_link = message.content.replace(original_url, new_url)
            await message.delete()
            await message.channel.send(f"{new_link} fixed link from {message.author.mention}")
            break
    else:
        if 'reddit.com' in message.content:
            video_url, audio_url = get_media_url(message.content)

            if video_url is not None and audio_url is not None:
                video_response = requests.get(video_url)
                audio_response = requests.get(audio_url)

                video_path = './ipadbot/media/video.mp4'
                audio_path = './ipadbot/media/audio.mp4'
                with open(video_path, 'wb') as f:
                    f.write(video_response.content)
                with open(audio_path, 'wb') as f:
                    f.write(audio_response.content)

                video_clip = VideoFileClip(video_path)
                audio_clip = AudioFileClip(audio_path)
                final_clip = video_clip.set_audio(audio_clip)
                final_clip.write_videofile("./ipadbot/media/final.mp4")

                await message.delete()

                if os.path.getsize("./ipadbot/media/final.mp4") > 8 * 1024 * 1024:
                    compress_video("./ipadbot/media/final.mp4", "./ipadbot/media/compressedr.mp4", 8)
                    await message.channel.send(f"fixed video for {message.author.mention}: ", file=discord.File("./ipadbot/media/compressedr.mp4"))
                else:
                    await message.channel.send(content=f"embedding reddit video from " + message.author.mention, file=discord.File("./ipadbot/media/final.mp4"))

    # Process commands after checking for the mention
    await bot.process_commands(message)

# Read the token from a file
with open('token.txt', 'r') as file:
    token = file.read().strip()

# Run the bot
bot.run(token)
