import discord, asyncio, os, json
import praw, instaloader, random
import requests
import re
import threading

from discord.ext import commands, tasks
from datetime import datetime

from commands.translate_command import add_translate_command
from commands.deathroll_command import add_deathroll_command
from commands.helpcommand import CustomHelpCommand

import moviepy.editor as mp
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

reddit = praw.Reddit(
    client_id="hgXRT4GQb_GZYdFEJbynJw",
    client_secret="KsiI1DyMIC9J2t-Oaz79kt6nswq96g",
    user_agent="ipad bot v1 by /u/level2isbetter"
)

GLOBE_ID = 157322236796207104
CLR_ID = 124385522196938752

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

def input_thread(bot):
    while True:
        msg = input('Enter a message to send: ')
        channel_id = int(input('Enter the channel id: '))
        channel = bot.get_channel(channel_id)
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(msg), bot.loop)
        else:
            print(f'No channel found with id {channel_id}')

url_mappings = {
    'https://x.com': 'https://stupidpenisx.com',
    'https://twitter.com': 'https://fxtwitter.com',
    'https://www.tiktok.com': 'https://www.vxtiktok.com',
    'https://www.reddit.com': 'https://www.vxreddit.com'
}

instagram2 = 'https://www.instagramez.com'

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

    
    await bot.load_extension("commands.cog_management")

    print('Loaded cogs: ')
    for cog in bot.extensions:
        print(cog)
    print(f'We have logged in as {bot.user}')

    threading.Thread(target=input_thread, args=(bot,), daemon=True).start()

deafened_start_time = {}

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == GLOBE_ID:
        if before.channel is None and after.channel is not None:
            print(f"{member.name} has joined {after.channel.name}")

            count_file = "./ipadbot/files/globecount.txt"
            if os.path.exists(count_file):
                with open(count_file, "r") as file:
                    count = int(file.read().strip())
            else:
                count = 0
            
            count += 1
            
            with open(count_file, "w") as file:
                file.write(str(count))

            if not before.self_deaf and after.self_deaf:
                deafened_start_time[member.id] = datetime.now()
                print(f"{member.name} has deafened themselves")

            if before.self_deaf and not after.self_deaf:
                if member.id in deafened_start_time:
                    deafened_duration = datetime.now() - deafened_start_time[member.id]
                    del deafened_start_time[member.id]
                    
                    duration_file = ".ipadbot/files/deafened.txt"
                    with open(duration_file, "a") as file:
                        file.write(f"{member.name} deafened for {deafened_duration}\n")

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

@bot.command()
#@commands.cooldown(1, 86400, commands.BucketType.guild)
async def backshotmode(ctx):
    brand = random.randint(1, 100)
    if ctx.guild.id == 557040114967248897:
        if brand < 20:
            absid = '612354895973974018'
            await ctx.send(f'Backshot mode ON. Todays target: <@{absid}>')
        else:
            members = [m for m in ctx.guild.members if not m.bot]
            if not members:
                await ctx.send("No members to target.")
                return
            member = random.choice(members)
            await ctx.send(f'Backshot mode ON. Todays target: {member.mention}')
    else:  
        members = [m for m in ctx.channel.members if not m.bot]
        if not members:
            await ctx.send("No members to target.")
            return
        member = random.choice(members)
        await ctx.send(f'Backshot mode ON. Todays target: {member.mention}')

# A mod command to batch clear messages
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <0 or amount > 100:
        await ctx.send('Please provide a number between 1 and 100')
    else:
        await ctx.channel.purge(limit=amount+1)

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
        kreact = random.randint(1,100)
        if kreact == 1:
            for emoji in emojis:
                await message.add_reaction(emoji)
    
    for original_url, new_url in url_mappings.items():
        if original_url in message.content:
            new_link = message.content.replace(original_url, new_url)
            await message.delete()
            sent_message = await message.channel.send(f"{new_link} fixed link from {message.author.mention}")
        elif 'https://www.instagram.com' in message.content:
            new_link = message.content.replace('https://www.instagram.com', 'https://www.ddinstagram.com')
            await message.delete()
            sent_message = await message.channel.send(f"{new_link} fixed link from {message.author.mention}")
            await asyncio.sleep(3)

            try:
                sent_message = await message.channel.fetch_message(sent_message.id)
                if not sent_message.embeds:
                    final_link = message.content.replace('https://www.instagram.com', 'https://www.instagramez.com')
                    await sent_message.delete()
                    await message.channel.send(f"{final_link} fixed link from {message.author.mention}")
            except discord.errors.NotFound:
                await message.channel.send("message not found")
    """else:
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

    # Process commands after checking for the mention"""
    await bot.process_commands(message)

# Read the token from a file
with open('token.txt', 'r') as file:
    token = file.read().strip()

# Run the bot
bot.run(token)
