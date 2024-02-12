import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None
#----------------search from youtube --------------
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False
        return {'source': info['formats'][0]['url'], 'title': info['title']}
#----------------play music functions--------------------    
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
    
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc == None:
                    await ctx.send("dumbass!! could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.is_playing = False
#----------------play function--------------
    @commands.command(name="play", aliases=["p", "playing"], help="Play the selected song from youtube :D")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel, Dumbass!!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type (song) == type(True):
                await ctx.send("Could not download the song. Incorrect format, try a different keyword, Dumbass!!")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music(ctx)
#---------------pause function--------------------
        @commands.command(name="pause", help="Pauses the current song being played")
        async def pause(self, ctx, *args):
            if self.is_playing:
                self.is_playing = False
                self.is_paused = True
                self.vc.paused()
            elif self.is_paused:
                self.is_playing = True
                self.is_paused = False
                self.vc.resume()
#---------------resume function-------------------
        @commands.command(name="resume", aliases=["r"], help="Resumes playing the current song, you deaf?")
        async def resume(self, ctx, *args):
            if self.is_paused:
                self.is_playing = True
                self.is_paused = False
                self.vc.resume()
#--------------skip function-----------------------
        @commands.command(name="skip", aliases=["s"], help="Skips the currently played song, you blind?")
        async def resume(self, ctx, *args):
            if self.vc != None and self.vc:
                self.vc.stop()
                await self.play_music(ctx)
#--------------queue function------------------------
        @commands.command(name="queue", aliases=["q"], help="Displays all the songs currently in the queue dumbass!!")
        async def queue(self, ctx,):
            retval = ""

            for i in range(0, len(self.music_queue)):
                if i > 4: break
                retval += self.music_queue[i][0]['title'] + '\n'

            if retval != "":
                await ctx.send(retval)
            else:
                await ctx.send("No music in the queue ma nigga!!")