import discord
import asyncio
import os
import tempfile

from discord.ext import commands
from pytube import YouTube
from yt_dlp import YoutubeDL

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.isplaying = False
        self.ispaused = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio',
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192',
                            }],
                            'outtmpl': 'music.mp3',
                            'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnected_streamed 1 -reconnect_delay_max 5' , 'options': '-vn'}

        self.vc = None

    def search_yt(self, song_url, filename):
        youtube = YouTube(song_url)
        song = youtube.streams.get_highest_resolution()
        song.download(output_path='.', filename=filename)
    
    def play_next(self):
        try:
            if self.vc is None or not self.vc.is_connected():
                self.isplaying = False
                return
            
            if len(self.music_queue) > 0:
                self.isplaying = True

                self.vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=self.music_queue[0][0]), after=lambda e: self.play_next())
                self.music_queue.pop(0)
            else:
                self.isplaying = False
        except Exception as e:
            print(f"An error occurred while trying to play: {e}")

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.isplaying = True

            if self.vc == None or not self.vc.is_connected() or self.vc.channel != ctx.author.voice.channel:
                if self.vc and self.vc.is_connected():
                    await self.vc.disconnect()
                try:
                    self.vc = await ctx.author.voice.channel.connect()
                except discord.errors.ClientException:
                    pass
                
                if self.vc == None:
                    await ctx.send("Failed to join the voice channel")
                    return

            self.play_next()
        else:
            self.isplaying = False

    @commands.command(name="play", aliases=["p", "playing"], help="Play music from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("You are not in a voice channel")
        elif self.ispaused:
            self.vc.resume()
        else:
            # need to generate unique name because I store song locally
            filename = f'song{len(self.music_queue)}.mp3'
            song = self.search_yt(query, filename)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword")
            else:
                await ctx.send("Song added to queue")
                self.music_queue.append([filename, voice_channel])

                if not self.isplaying:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pause the currently playing song")
    async def pause(self, ctx, *args):
        if self.vc.isplaying():
            self.isplaying = False
            self.ispaused = True
            self.vc.pause()
            await ctx.send("Paused")
        elif self.ispaused:
            self.isplaying = True
            self.ispaused = False
            self.vc.resume()

    @commands.command(name="resume", help="Resume the currently paused song")
    async def resume(self, ctx, *args):
        if self.ispaused:
            self.isplaying = True
            self.ispaused = False
            self.vc.resume()
            await ctx.send("Resumed")

    @commands.command(name="skip", help="Skip the current song")
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await ctx.send("Skipped")
            self.vc.play_music(ctx)

    @commands.command(name="queue", help="Display the current queue")
    async def queue(self, ctx):
        retval = ""

        for i in range(0, len(self.music_queue)):
            if i > 4: break
            retval += f"{i+1}: {self.music_queue[i][0]['title']}\n"
        
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("Queue is empty")

    @commands.command(name="qclear", help="Clear the queue")
    async def qclear(self, ctx, *args):
        if self.vc != None and self.isplaying:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Queue cleared")

    @commands.command(name="leave", help="Leave the voice channel")
    async def leave(self, ctx):
        if self.vc and self.vc.is_connected():
            await self.vc.disconnect()
        self.isplaying = False
        self.ispaused = False

    @commands.command(name="join", help="Join the voice channel")
    async def join(self, ctx, *args):
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            if ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to()
            else:
                return
        try:
            await channel.connect()
        except discord.errors.ConnectionClosed:
            if ctx.voice_client is not None:
                await ctx.voice_client.disconnect()
            await channel.connect()

async def setup(bot):
    await bot.add_cog(music(bot))