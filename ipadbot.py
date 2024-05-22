import discord
import asyncio
import os
import praw
import requests

from discord.ext import commands, tasks

from commands.translate_command import add_translate_command
from commands.deathroll_command import add_deathroll_command
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

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

# Create a bot instance
bot = commands.Bot(command_prefix='.', intents=intents)

add_translate_command(bot) # Importing the translation command
add_deathroll_command(bot) # Importing the deathroll command

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@tasks.loop(seconds=300)
async def change_status():
    await bot.change_presence(activity=discord.Game(name=random.choice(status)))


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
    elif 'https://x.com/' in message.content:

        new_link = message.content.replace('https://x.com/', 'https://fixupx.com/')
        await message.delete()

        await message.channel.send(new_link + " fixed link from " + message.author.mention)
    elif 'reddit.com' in message.content:
        video_url, audio_url = get_media_url(message.content)

        if video_url is not None and audio_url is not None:
            video_response = requests.get(video_url)
            audio_response = requests.get(audio_url)

            video_path = 'video.mp4'
            audio_path = 'audio.mp4'
            with open(video_path, 'wb') as f:
                f.write(video_response.content)
            with open(audio_path, 'wb') as f:
                f.write(audio_response.content)

            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile("final.mp4")

            await message.delete()
            await message.channel.send(content=f"embedding reddit video from " + message.author.mention, file=discord.File("final.mp4"))

    # Process commands after checking for the mention
    await bot.process_commands(message)

# Read the token from a file
with open('token.txt', 'r') as file:
    token = file.read().strip()

# Run the bot
bot.run(token)
