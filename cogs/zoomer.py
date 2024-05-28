import requests
import discord
import yt_dlp
import os, time

from pytube import YouTube

from discord.ext import commands
from moviepy.video.fx.all import speedx
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

def compress_video(video_path, output_path, target_size):
    clip = VideoFileClip(video_path)
    target_bitrate = (target_size * 1024 * 8) / clip.duration

    clip.write_videofile(output_path, bitrate=f"{int(target_bitrate)}k")

# For fun command - reply to a video, bot will speed up a video by 1.5x and add subway surfers to make it watchable
class zoomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Downloads the video from the given URL, youtube or discord for now
    async def download_video(self, video_url):
        timestamp = str(int(time.time()))
        youtube = YouTube(video_url)
        video = youtube.streams.get_highest_resolution()
        video.download(output_path='./ipadbot/media/', filename=f'zoomer_{timestamp}.mp4')

    async def download_tiktok_video(self, tiktok_url):
        timestamp = str(int(time.time()))
        tiktok_url = tiktok_url.replace('vxtiktok.com', 'tiktok.com')
        ydl_opts = {'outtmpl': f'./ipadbot/media/zoomer_{timestamp}.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tiktok_url])

    async def download_twitter_video(self, twitter_url):
        timestamp = str(int(time.time()))
        twitter_url = twitter_url.replace('fixupx.com', 'twitter.com')
        ydl_opts = {'outtmpl': f'./ipadbot/media/zoomer_{timestamp}.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([twitter_url])

    @commands.command(name="zoom")
    async def zoom(self, ctx, vertical: str = "bottom", horizontal: str = "right", vspeed: float = 1.5):
        # Preventing the file from being overwritten if the command is used at the same time in multiple servers
        timestamp = str(int(time.time()))
        if vertical not in ["top", "bottom"] or horizontal not in ["left", "right"]:
            await ctx.send("Invalid position")
            return
        
        # Checks if the message is a reply
        if ctx.message.reference is not None:
            replied_message = await ctx.fetch_message(ctx.message.reference.message_id)

            # Checks if the original message has attachments
            if replied_message.attachments:
                video_url = replied_message.attachments[0].url
                video_path = f'./ipadbot/media/zoomer_{timestamp}.mp4'
                with requests.get(video_url, stream=True) as r:
                    r.raise_for_status()
                    with open(video_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            elif 'https://www.youtube.com/' in replied_message.content or 'https://youtu.be/' in replied_message.content:
                video_url = replied_message.content
                await self.download_video(video_url)
            elif 'https://www.vxtiktok.com/' in replied_message.content:
                video_url = replied_message.content
                await self.download_tiktok_video(video_url)
            elif 'https://fixupx.com/' in replied_message.content:
                video_url = replied_message.content
                await self.download_twitter_video(video_url)
            else:
                await ctx.send("No video found in specified message")
                return
            
            video_path = f'./ipadbot/media/zoomer_{timestamp}.mp4'
            final_path = f'./ipadbot/media/finalzoom_{timestamp}.mp4'

            video_clip = VideoFileClip(video_path)

            # Speeds up the clip by vspeed, which is default 1.5x
            sped_clip = speedx(video_clip, factor=vspeed)

            # Adds a subway surfers clip to the video
            small_clip = VideoFileClip('./ipadbot/media/zoomervid2.mp4')
            small_clip = small_clip.resize(height=sped_clip.size[1] // 2)
            small_clip = small_clip.subclip(0, sped_clip.duration)

            # Loop small clip if sped clip is longer
            if small_clip.duration < video_clip.duration:
                small_clip = small_clip.loop(duration=sped_clip.duration)

            sped_clip = sped_clip.subclip(0, small_clip.duration)

            final_clip = CompositeVideoClip([sped_clip, small_clip.set_position((horizontal, vertical))])
            final_clip.write_videofile(final_path)

            if os.path.getsize(final_path) > 8 * 1024 * 1024:
                compressed_path = f'./ipadbot/media/compressed_{timestamp}.mp4'
                compress_video(final_path, compressed_path, 8)
                await ctx.send(f"fixed video for {ctx.author.mention}: ", file=discord.File(compressed_path))
            else:
                await ctx.send(f"fixed video for {ctx.author.mention}: ", file=discord.File(final_path))
        else:
            await ctx.send("Please reply to a message that has a video")

async def setup(bot):
    await bot.add_cog(zoomer(bot))