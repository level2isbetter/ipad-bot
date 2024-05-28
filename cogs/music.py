import discord
import asyncio
import os
import tempfile, yt_dlp
import youtube_dl

from discord.ext import commands
from pytube import YouTube
from yt_dlp import YoutubeDL

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_stream = {'options': '-vn'}
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnected_streamed 1 -reconnect_delay_max 5' , 'options': '-vn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_stream), data=data)

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio',
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192',
                            }],
                            'outtmpl': 'music.mp3',
                            'noplaylist': 'True'}
        #self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnected_streamed 1 -reconnect_delay_max 5' , 'options': '-vn'}

        self.vc = None

    def search_yt(self, song_url, filename):
        youtube = YouTube(song_url)
        song = youtube.streams.get_highest_resolution()
        song.download(output_path='.', filename=filename)
    
    def play_next(self, ctx):
        try:
            if self.vc is None or not self.vc.is_connected():
                self.vc.is_playing = False
                return
            
            if len(self.music_queue) > 0:
                #if self.music_queue[0][0] == None:
                    #self.music_queue.pop(0)
                    #return
                self.vc.is_playing = True
                #self.current_player = self.music_queue.pop(0)
                self.vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=self.music_queue[0][0]), after=lambda e: self.play_next())
            else:
                self.vc.is_playing = False
                self.current_player = None
        except Exception as e:
            print(f"An error occurred while trying to play: {e}")
    
    def after_playing(self, ctx, error):
        if error:
            print(f'Player error: {error}')
        self.vc.is_playing = False
        self.play_next(ctx)

    async def play_music(self, ctx):
        if len(self.music_queue) > 0 and not self.vc.is_playing:
            self.vc.is_playing = True

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
            self.vc.is_playing = False

    @commands.command()
    async def yt(self, ctx, *, url):
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            self.vc = await voice_channel.connect()
            if self.vc is None:
                await ctx.send("Failed to join the voice channel")
                return
    
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            async with ctx.typing():
                song_info = ydl.extract_info(url, download=False)
                self.player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                self.is_playing = True
                await ctx.send(f'Now playing: {self.player.title}')
        ctx.voice_client.play(discord.FFmpegPCMAudio(song_info["url"], **ffmpeg_stream))

        #if self.is_playing:
            #await ctx.send("Song added to queue")
            #self.music_queue.append((self.player, url))
        #else:
            #ctx.voice_client.play(discord.FFmpegPCMAudio(song_info["url"], **ffmpeg_stream))
            #self.is_playing = True

    @commands.command(name="play", aliases=["p", "playing"], help="Play music from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("You are not in a voice channel")
        #elif self.ispaused:
            #self.vc.resume()
        else:
            # need to generate unique name because I store song locally
            filename = f'song{len(self.music_queue)}.mp3'
            song = self.search_yt(query, filename)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword")
            else:
                await ctx.send("Song added to queue")
                self.music_queue.append([filename, voice_channel])

                if not self.vc.is_playing:
                    await self.play_music(ctx)

    @commands.command(name="skip", help="Skip the current song")
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await ctx.send("Skipped")
            await self.play_music(ctx)

    @commands.command(name="queue", help="Display the current queue")
    async def queue(self, ctx):
        retval = ""

        if len(self.music_queue) == 0:
            await ctx.send("Queue is empty")
        else:
            for i in range(0, len(self.music_queue)):
                retval += f"{i+1}: {self.music_queue[i][0].title}\n"
            await ctx.send(retval)

    @commands.command(name="qclear", help="Clear the queue")
    async def qclear(self, ctx, *args):
        if self.vc != None and self.vc.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Queue cleared")

    @commands.command(name="leave", help="Leave the voice channel")
    async def leave(self, ctx):
        if self.vc and self.vc.is_connected():
            await self.vc.disconnect()
        self.vc.is_playing = False
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