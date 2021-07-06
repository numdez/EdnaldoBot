import asyncio
import functools
import itertools
import random
import math
import os
import discord
import re
import urllib.request
import youtube_dl
import tweepy
import json
import sys
import pyttsx3
import time
import audioread
import pytesseract
import io
import requests
import yaml
import numpy

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from googletrans import Translator
from PIL import Image
from googlesearch import search as googleSearch
from tinytag import TinyTag
from random import choice
from discord.ext.commands import check
from discord.ext import commands
from async_timeout import timeout
from discord.ext import commands, tasks
from random import randint
from os import system
from discord.utils import get
from discord.ext.commands import CommandNotFound

youtube_dl.utils.bug_reports_message = lambda: ''

member = discord.Member

client = discord.Client

f = open('text/banidos.txt', 'w+')
f.close()

idioma = ''

safeConf = yaml.safe_load(open('conf/application.yml'))

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

translator = Translator()

bugado = False

def tasuave():
    x = 10

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def escreve(arquivo, conteudo):
    arq = open(arquivo, "a", encoding='utf-8')
    arq.write(conteudo)

def aleatorios(tamanho, quantdenumeros,minimo):
    devolver = []
    devolver = random.sample(range(int(minimo),tamanho), quantdenumeros)
    return list(devolver)

def in_voice_channel():  # check to make sure ctx.author.voice.channel exists
    def predicate(ctx):
        return ctx.author.voice and ctx.author.voice.channel
    return check(predicate)

def bagunca_lista(lista, vezesprabaguncar):
    for i in range(1,vezesprabaguncar):
        random.shuffle(lista)
    return lista

def is_bot(seraqbot):
    if seraqbot.bot:
        return True
    if not seraqbot.bot:
        return False
    
engine = pyttsx3.init()
engine.setProperty('volume', 1)

auth = tweepy.OAuthHandler(safeConf['twitter']['consumer_key'], safeConf['twitter']['consumer_secret'])
auth.set_access_token(safeConf['twitter']['access_token'], safeConf['twitter']['access_token_secret'])
api = tweepy.API(auth)

BRAZIL_WOE_ID = 23424768

try:
    api.verify_credentials()
    print("tudo ok com o tweepy")
except:
    print("nada ok com o tweepy")


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass

'''
class Watcher:
    """ Watches is the value of the variable changes and runs post_change method if it is """
    def __init__(self, value):
        self.value = value

    def set_value(self, new_value):
        if self.value != new_value:
            self.value = new_value
            return self.post_change()

    # Returns a list of the songs added since last check
    def post_change(self):
        # return SpotifyClient.SpotifyClient.get_last_added(self.value)
        return SpotifyClient.SpotifyClient.get_last_added(self.value)

# Create an instance of spotifyclient with client_id, client_secret and the spotify playlist uri
spotifyclient = SpotifyClient.SpotifyClient(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'], os.environ['PLAYLIST_URI'])

# Create an instance of Watcher with the initial "old" value parameter
watcher = Watcher(spotifyclient.get_playlist_tracks(spotifyclient.username, spotifyclient.playlist_id))

# instanciate the discord client
discordclient = discord.Client()
'''


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))
        
        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @classmethod
    async def search_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()

        cls.search_query = '%s%s:%s' % ('ytsearch', 10, ''.join(search))

        partial = functools.partial(cls.ytdl.extract_info, cls.search_query, download=False, process=False)
        info = await loop.run_in_executor(None, partial)

        cls.search = {}
        cls.search["title"] = f'Search results for:\n**{search}**'
        cls.search["type"] = 'rich'
        cls.search["color"] = 7506394
        cls.search["author"] = {'name': f'{ctx.author.name}', 'url': f'{ctx.author.avatar_url}', 'icon_url': f'{ctx.author.avatar_url}'}
        
        lst = []

        for e in info['entries']:
            lst.append(f'`{info["entries"].index(e) + 1}.` {e.get("title")} **[{YTDLSource.parse_duration(int(e.get("duration")))}]**\n')
            VId = e.get('id')
            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
            lst.append(f'`{info["entries"].index(e) + 1}.` [{e.get("title")}]({VUrl})\n')

        lst.append('\n**Type a number to make a choice, Type `cancel` to exit**')
        cls.search["description"] = "\n".join(lst)

        em = discord.Embed.from_dict(cls.search)
        await ctx.send(embed=em, delete_after=45.0)

        def check(msg):
            return msg.content.isdigit() == True and msg.channel == channel or msg.content == 'cancel' or msg.content == 'Cancel'
        
        try:
            m = await bot.wait_for('message', check=check, timeout=45.0)

        except asyncio.TimeoutError:
            rtrn = 'timeout'

        else:
            if m.content.isdigit() == True:
                sel = int(m.content)
                if 0 < sel <= 10:
                    for key, value in info.items():
                        if key == 'entries':
                            """data = value[sel - 1]"""
                            VId = value[sel - 1]['id']
                            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
                            partial = functools.partial(cls.ytdl.extract_info, VUrl, download=False)
                            data = await loop.run_in_executor(None, partial)
                    rtrn = cls(ctx, discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS), data=data)
                else:
                    rtrn = 'sel_invalid'
            elif m.content == 'cancel':
                rtrn = 'cancel'
            else:
                rtrn = 'sel_invalid'
        
        return rtrn

    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)

            duration = []
            if days > 0:
                duration.append('{}'.format(days))
            if hours > 0:
                duration.append('{}'.format(hours))
            if minutes > 0:
                duration.append('{}'.format(minutes))
            if seconds > 0:
                duration.append('{}'.format(seconds))
            
            value = ':'.join(duration)
        
        elif duration == 0:
            value = "LIVE"
        
        return value


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester
    
    def create_embed(self):
        embed = (discord.Embed(title='Now playing', description='```css\n{0.source.title}\n```'.format(self), color=discord.Color.blurple())
                .add_field(name='Duration', value=self.source.duration)
                .add_field(name='Requested by', value=self.requester.mention)
                .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                .set_thumbnail(url=self.source.thumbnail)
                .set_author(name=self.requester.name, icon_url=self.requester.avatar_url))
        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.exists = True

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.now = None

            if self.loop == False:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    return
                
                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                await self.current.source.channel.send(embed=self.current.create_embed())
            
            #If the song is looped
            elif self.loop == True:
                self.now = discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)
            
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    
    idioma = ''

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True
    
    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        print('An error occurred: {}'.format(str(error)))

    @commands.Cog.listener()
    async def on_message(self, message):

        ''' turn this on to get a channels' id
        with open("text/channels.txt", "w", encoding='utf-8') as file:
            escrever = f"{message.channel}/{message.author.name}> {message.channel.id}/{message.author.id}"
            file.write(escrever)
        '''
             
        if message.author.id == 789455654896009226 and message.content.lower() == "uga buga":
            await message.delete()
        
        if message.author == client.user or message.author == bot.user: #prints any message in any server the bot is in
            print(f"{message.guild}/{message.channel}/{message.author.name}>{message.content}")
        if is_bot(message.author) == False:
            print(f"{message.guild}/{message.channel}/{message.author.name}>{message.content}")
            
            if message.embeds:
                print(message.embeds[0].to_dict())
                
            if message.author.id != bot.user.id:
                emoji = bot.get_emoji(756510157441204244)
                
                if message.content.startswith('ednaldo?'):
                    await message.channel.send('pereira')

                if message.content.startswith('oi ednaldo'): #says hello back
                    await message.channel.send(f'oi <@!{message.author.id}>')

                if message.content.startswith('hmmm'): 
                    await message.channel.send("https://tenor.com/view/ednaldo-pereira-vision%c3%a1rio-peep-gif-14849212")

                if 'brabo' in message.content or 'pog' in message.content:  #adds a ednaldo pereira poggers emote reaction to a "pog" or "awesome" message
                    await message.add_reaction(emoji)
                
                        
                if '518118209073971220' in message.content or '<@!518118209073971220>' in message.content: #randomly insults a specific user whenever he is pinged
                    decisao = randint(0,9)
                    if decisao == 1:
                        await message.channel.send('esse saco de bosta')

                if 'tenor.com/view/' in message.content or '.gif' in message.content and 'media.discordapp.net' in message.content or 'giphy.com/gifs/' in message.content: #randomly judges a gif sent in any channel
                    simounao = randint(0, 10)
                    falar = randint(0,9)
                    if falar == 1 or falar == 2:
                        if (message.author.id == 518118209073971220):
                            await message.channel.send("<@!518118209073971220> O adm pede que você o mame")
                        if not (message.author.id == 518118209073971220):
                            if simounao < 5:
                                await message.channel.send('gif legal')
                            if simounao > 5:
                                await message.channel.send('gif ruim')
                            if simounao == 5:
                                await message.channel.send(':thinking:')

                if message.content.startswith.lower('pequeno dia') or message.content.startswith.lower('small day'): #adds a sad reaction to a message with "small day"
                    await message.channel.send(':cry:')

                if message.content.startswith.lower('grande dia') or message.content.startswith.lower('big day'): #adds a sunglasses reaction to a message with "big day"
                    await message.channel.send(':sunglasses:')

                if message.content.startswith('ednaldo leia'): #tries to read text in an image, doesn't always work
                    try:
                        response = requests.get(message.attachments[0].url)
                        img = Image.open(io.BytesIO(response.content))
                        text = pytesseract.image_to_string(img, lang = self.idioma)
                        await message.channel.send(text)
                    except:
                        await message.channel.send('deu n')


    @commands.command(name='text_to_speech', aliases=['tts','text-to-speech'], help = 'cria um arquivo de audio e toca ele no canal de voz') #sends a tts file if the user is not in a voice channel, otherwise joins the chanel and plays the file
    async def _tts(self, ctx, *texto: str):
        text = ' '.join(texto)
        
        randomizado = randint(0,10)
        engine.save_to_file(text, f'message{randomizado}.mp3')
        engine.runAndWait()
        with open(f'audio/message{randomizado}.mp3', 'rb') as file:
            await ctx.message.delete()
            if not ctx.author.voice:
                try:
                    await ctx.send(file=discord.File(file, 'message.mp3'))
                except:
                    await ctx.send("arquivo grande demais pra enviar")
            else:
                await asyncio.sleep(1)

                destination = ctx.author.voice.channel
                
                if ctx.voice_state.voice:
                    await ctx.voice_state.voice.move_to(destination)
                    return

                ctx.voice_state.voice = await destination.connect()
                
                ctx.voice_state.voice.play(discord.FFmpegPCMAudio(f'audio/message{randomizado}.mp3'))

                audio = audioread.audio_open(f'audio/message{randomizado}.mp3')
                
                seconds = audio.duration
                print(seconds)
                await asyncio.sleep(seconds)
                
                await ctx.voice_state.stop()
                del self.voice_states[ctx.guild.id]
                    
            
                
        #doesn't play the audio file if the bot is already in a voice channel
    
    

    @in_voice_channel()
    @commands.command(name='move', help = 'move os membros de um canal de voz para outro') 
    @commands.is_owner()
    async def _move(self, ctx, *, channel : discord.VoiceChannel): #moves all members in a voice channel to the specified voice channel
        for members in ctx.author.voice.channel.members:
            await members.move_to(channel)
        

    @commands.command(name='equipes', aliases=['times'], help = 'divide as pessoas no canal de voz em uma determinada quantidade de equipes')
    async def _equipes(self, ctx, *q: str): #divides member currently in a voice channel into teams. members need to join the voice channel after the bot starts running
        quan = ' '.join(q)
        d = {}
        try:
            times = int(quan[0])
        except:
            times = 2
        cont = 0
        memids = []
        id_final = []
        for members in ctx.author.voice.channel.members:
            if is_bot(members) == False:
                memids.append(members.id)
                cont += 1
                
        ppt = int(cont/times)
        id_final = list(bagunca_lista(memids,74))

        start = 0
        
        marcar = []
        for f in id_final:
            notificar = f'<@{f}>'
            marcar.append(notificar)
        
        for i in range(1,times+1):
            embed=discord.Embed(title=f' Time {i}',description='Time')
            cont = 0
            for x in range(start, ppt):
                cont+=1
                embed.add_field(name=f'Membro {cont}', value=marcar[x], inline=True)
                start += 1
            ppt += start
            await ctx.send(embed=embed)
            

    @commands.command(name='entrae', invoke_without_subcommand=True) #bot joins the voice channel
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
       

    @commands.command(name='apareça')
    @commands.has_permissions(manage_guild=True) 
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None): #bot joins specified voice channel
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='saia', aliases=['vaza']) #bot leaves the voice channel
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    @commands.is_owner()
    async def _volume(self, ctx: commands.Context, *, volume: int): #changes voice volume
        """Sets the volume of the player."""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        if 0 > volume > 200:
            return await ctx.send('Volume must be between 0 and 100')

        ctx.voice_state.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='agora', aliases=['current', 'playing']) #shows what video is being played on voice channel
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""
        embed = ctx.voice_state.current.create_embed()
        await ctx.send(embed=embed)

    @commands.command(name='pausa', aliases=['pa'], help = 'o q será q esse comando faz ne?') #pauses the bot
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""
        print(">>>Pause Command:")
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='bov', aliases=['resume', 'volta'], help = 'despausa') #resumes the bot
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context): 
        """Resumes a currently paused song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')
            
    @commands.command(name='para')
    @commands.has_permissions(manage_guild=True) #stops the bot
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='pula', aliases=['s']) #skips a song
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('não to tocando nada')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('mais um voto, totalizando **{}/3**'.format(total_votes))

        else:
            await ctx.send('tu já votou')

    @commands.command(name='fila')
    async def _queue(self, ctx: commands.Context, *, page: int = 1): #show the queue
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('fila vazia')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='página {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='randomiza')
    async def _shuffle(self, ctx: commands.Context): #shuffles queue
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('fila vazia')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int): #removes specified song from queue
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('fila vazia')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='repete')
    async def _loop(self, ctx: commands.Context): 
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('não to tocando nada')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(name='toca', aliases=['p'])
    async def _play(self, ctx: commands.Context, *, search: str):
        """Plays a song.
        If there are songs in the queue, this will be queued until the
        other songs finished playing.
        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """
        
        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                print('ERROR: {}'.format(str(e)))
                await ctx.send('n to afim')
            else:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)

                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send('botei na fila  {} :thumbsup:'.format(str(source)))

    @commands.command(name='lista')
    async def _search(self, ctx: commands.Context, *, search: str):
        """Searches youtube.
        It returns an imbed of the first 10 results collected from youtube.
        Then the user can choose one of the titles by typing a number
        in chat or they can cancel by typing "cancel" in chat.
        Each title in the list can be clicked as a link.
        """
        async with ctx.typing():
            try:
                source = await YTDLSource.search_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                if source == 'sel_invalid':
                    await ctx.send('qual?')
                elif source == 'cancel':
                    await ctx.send(':white_check_mark:')
                elif source == 'timeout':
                    await ctx.send(':alarm_clock: **cabo o tempo**')
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._join)

                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send('botei na fila {} :thumbsup:'.format(str(source)))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('onde?')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('já to tocando')

class Text(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command(name='traduz', aliases=['translate', 'trans'], help='traduz texto para português') #translates text
    async def _trans(self, ctx, *toTrans: str):
        junto = ' '.join(toTrans)
        traduzido = translator.translate(junto, dest='pt') #change dest to change language you want to translate to
        await ctx.send(traduzido.text)
            
    @commands.command(name='contagem', aliases=['countdown'], help='contagem regressiva') #countdown command
    async def _countdown(self, ctx, time: int):
        await ctx.send("contagem regressiva iniciada")
        def check(message):
            return message.channel == ctx.channel and message.author == ctx.author and message.content.lower() == "cancela"
        try:
            m = await bot.wait_for("message", check=check, timeout=time)
            await ctx.send("contagem cancelada")
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} contagem concluída")

    @commands.command(name='twitter', aliases=['twtr','twt'], help = 'mostra a conta do usuário especificado') #searches specified twitter user
    async def _twitter(self, ctx, usera):
        if 'ednaldo' in usera:
            user = api.get_user('oednaldopereira')
            link = 'https://twitter.com/' + user.screen_name
            embed=discord.Embed(title='Perfil', url = link, description='Perfil do twitter')
            embed.set_thumbnail(url=user.profile_image_url.replace('_normal', ''))
            embed.add_field(name='Nome', value=user.name, inline=True)
            embed.add_field(name='Descrição', value=user.description, inline=False)
            embed.add_field(name='Quantidade de seguidores', value=user.followers_count, inline=True)
            embed.add_field(name='Quantidade de tweets', value=user.statuses_count, inline=True)
            await ctx.send(embed=embed)
        else:
            try:
                user = api.get_user(usera)
                link = 'https://twitter.com/' + user.screen_name
                embed=discord.Embed(title='Perfil',url=link, description='Perfil do twitter')
                embed.set_thumbnail(url=user.profile_image_url.replace('_normal', ''))
                embed.add_field(name='Nome', value=user.name, inline=True)
                embed.add_field(name='Descrição', value=user.description, inline=False)
                embed.add_field(name='Quantidade de seguidores', value=user.followers_count, inline=True)
                embed.add_field(name='Quantidade de tweets', value=user.statuses_count, inline=True)
                await ctx.send(embed=embed)
            except:
                await ctx.send("NA usuário")

    @commands.command(name='coinflip', aliases=['caracoroa', 'caraoucoroa','cointoss'], help='cara ou coroa') #coinflip
    async def _caraoucoroa(self, ctx):
        randomlist = ["cara","coroa",]
        await ctx.send(random.choice(randomlist))
    
    @commands.command(name='trending_topics', aliases=['trending', 'topics', 'topic', 'tt'], help='mostra os assuntos em tendência no momento') #searches twitter trending topics of a certain country
    async def _trending(self, ctx, *tulipa: str):                                                                                               # in this case, brazil's trending topics
        filtro = ' '.join(tulipa).lower()
        if 'brasil' in filtro or 'brazil' in filtro or filtro == '':
            trends = []
            nome = []
            volume = []
            nomes = []
            volu = []
            final = []
            aurelio ={}

            nomez = []
            tuites = []
            nfinal = []
            vfinal = []
            lfinal = {}
            brazil_trends = api.trends_place(BRAZIL_WOE_ID)
            trends = json.loads(json.dumps(brazil_trends, indent=1))
            for trend in trends[0]["trends"]:
                nomez.append(trend['name'])
                tuites.append(trend['tweet_volume'])
            
            #might want to sort topics based on amount of tweets, although unfiltered seems (or at least, seemed at the time) to work best

            embed=discord.Embed(title="Trending Topics", url="https://twitter.com/explore/tabs/trending", description="Assuntos que estão dando o que falar")
            embed.set_thumbnail(url="https://img.pngio.com/fichiertwitter-birdsvg-wikipedia-twitter-logo-png-738_600.png")
            embed.add_field(name=nomez[0], value=tuites[0], inline=True)
            embed.add_field(name=nomez[1], value=tuites[1], inline=True)
            embed.add_field(name=nomez[2], value=tuites[2], inline=True)
            embed.add_field(name=nomez[3], value=tuites[3], inline=True)
            embed.add_field(name=nomez[4], value=tuites[4], inline=True)
            embed.add_field(name=nomez[5], value=tuites[5], inline=True)
            embed.add_field(name=nomez[6], value=tuites[6], inline=True)
            embed.add_field(name=nomez[7], value=tuites[7], inline=True)
            embed.add_field(name=nomez[8], value=tuites[8], inline=True)
            embed.add_field(name=nomez[9], value=tuites[9], inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send('sla sio, só sei as coisa do brasil')

    @commands.command(name='youtube', aliases=['yt'], help = 'pesquisa um vídeo no youtube') #searches a single specific video on youtube
    async def musica(self, ctx, *contexto: str):
        frase = ' '.join(contexto)
        pesquisa = frase.replace(' ', '+')
        html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={pesquisa}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        video = 'https://www.youtube.com/watch?v=' + video_ids[0]
        await ctx.send(video)

    @commands.command(name='caulezada', aliases=['caule', 'pica', 'caules'], help = 'responde com um caule aleatório') #sends a nsfw copypasta
    async def _caule(self, ctx):
        with open('text/caules.txt', 'r', encoding='utf-8') as frase:
            leia = randint(0,12)
            print(leia+1)
            linha = frase.readlines()
            caulez = linha[leia].replace(' ', '\n')
            await ctx.send(caulez)
            frase.close()

    @commands.command(name='ping', help='mostra a latência do bot') #latency command
    async def ping(self, ctx):
        await ctx.send(f'{round(bot.latency * 1000)}ms')
    
    @commands.command(help = 'ednaldo pereira') #ednaldo pereira, real life person the bot is "inspired" on
    async def pereira(self, ctx):
        await ctx.send('ednaldo pereira')

    @commands.command(name='champions', aliases =['champs', 'champion', 'champ'], help = 'escolhe um champ aleatório') #sends a random league of legends champion, hasn't been updated in a long time
    async def campeaos(self, ctx, *frase: str):                                                                        # and wont be updated anymore
        with open('text/champs.txt', 'r', encoding='utf-8') as bonecao:
            nome = bonecao.readlines()
            linha = randint(0,151)
            await ctx.send(nome[linha])
            bonecao.close()

    @commands.command(name='composição', aliases=['comp'], help= 'escolhe uma determinada quantidade de champs e suas lanes') #chooses champions and lanes for a league of legends team
    async def _comp(self, ctx, *quanti: str):
        author = ctx.message.author
        pfp = author.avatar_url
        try:
            quanti = tuple(map(int, quanti))
            quant = quanti[0]
            with open('text/lanes.txt', 'r', encoding='utf-8') as caminho:
                with open('text/champs.txt', 'r', encoding='utf-8') as bonecao:
                    lane = caminho.readlines()
                    nome = bonecao.readlines()
                    i = 0
                    num_champ = []
                    num_lane = []
                    jafoilane = []
                    jafoichamp = []     
                    embed=discord.Embed(title='Timão', description='Composição do time ae')
                    embed.set_author(name=author.display_name, icon_url=pfp)
                    embed.set_thumbnail(url='https://pbs.twimg.com/media/ET2jVamXYAACtN7.jpg')
                    num_champ = aleatorios(len(nome), int(quant), 0)
                    num_lane = aleatorios(len(lane), int(quant), 0)
                    repete = int(quant)
                    if repete == 0:
                        embed.add_field(name='_', value='_', inline=False)
                        embed.set_footer(text="time ficou foda né arrombado")
                    for i in range(int(repete)):
                        linha1 = num_champ[i]
                        linha2 = num_lane[i]
                        embed.add_field(name=lane[linha2], value=nome[linha1], inline=True)
                        jafoilane.append(linha2)
                        jafoichamp.append(linha1)
        except:
            embed=discord.Embed(title='Timão', description='Composição do time ae')
            embed.set_author(name=author.display_name, icon_url=pfp)
            embed.set_thumbnail(url='https://pbs.twimg.com/media/ET2jVamXYAACtN7.jpg')
            embed.add_field(name='_', value='_', inline=True)
            embed.add_field(name='_', value='_', inline=True)
            embed.add_field(name='_', value='_', inline=True)
            embed.add_field(name='_', value='_', inline=True)
            embed.add_field(name='_', value='_', inline=True)
            embed.set_footer(text="time ficou foda né arrombado")

        await ctx.send(embed=embed)


    @commands.command(name='escolha', help = 'escolhe entre duas opções') #chooses between two given options
    async def _escolha(self, ctx, *pergunta: str):
        cont = 0
        meio = 0
        cont1 = 0
        str1 = ''
        str2 = ''
        decisao = randint(0,10)
        frase = ' '.join(pergunta)
        palavras = frase.replace('?', '').split()
        for i in palavras:
            cont += 1
            if i == 'ou':
                meio = cont
                    
        for i in range(meio-1):
            str1 += palavras[i]
            str1 += ' '
            
        for i in range(meio,cont):
            str2 += palavras[i]
            str2 += ' '
            
        if decisao<5:
            await ctx.send(str2)
        if decisao>5:
            await ctx.send(str1)
        if decisao == 5:
            await ctx.send(':thinking:')

    @commands.command(name='pesquisa', help='pesquisa no google') #googles something
    async def searchzada(self, ctx, *pesq: str):
        search = ' '.join(pesq)
        pesquisa = googleSearch(str(search), num_results=1, lang="pt-br")[0]
        await ctx.send(pesquisa)

    @commands.command(name='responda', help = 'responde uma pergunta') #answers a question like a magic 8 ball, might want to change answers to preferred language
    async def magic8ball(self, ctx, pergunta):
        with open('text/boladecristal.txt', 'r', encoding='utf-8') as frase:
            leia = randint(0,19)
            linha = frase.readlines()
            await ctx.send(linha[leia])
            frase.close()

    @commands.command(name='poggers', aliases=['pog', 'pogger'], help = 'pog') #sends a random pog gif
    async def _pog(self, ctx, *txt: str):
        await ctx.message.delete()
        emoji = bot.get_emoji(756510157441204244)
        with open('text/ednaldopoggers.txt', 'r', encoding='utf-8') as pogger:
            leia = randint(0,24)
            linha = pogger.readlines()
            message = await ctx.send(linha[leia])
            await message.add_reaction(emoji)
            pogger.close()

    @commands.command(name='enquete', help = 'faz uma enquete') #poll
    async def quickpoll(self, ctx, question, *options: str):
        if len(options) <= 1:
            await ctx.send('NA opções da enquete')
            return
        if len(options) > 10:
            await ctx.send('aí tu ta querendo opção dms sio')
            return
        await ctx.channel.purge(limit=1)

        reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

        description = []
        for x, option in enumerate(options):
            description += '\n {} {}'.format(reactions[x], option)

        embed = discord.Embed(
            title=question,
            description=''.join(description),
            colour=discord.Colour.dark_purple()
        )
        embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        poll_message = await ctx.send(embed=embed)
        for reaction in reactions[:len(options)]:
            await poll_message.add_reaction(reaction)
        embed.set_footer(text='ID da enquete: {}'.format(poll_message.id))
        await poll_message.edit(embed=embed)

    @commands.command(name='resultado', help = 'mostra os resultados da enquete') #tally
    async def tally(self, ctx, msg_id):
        poll_message = await ctx.fetch_message(msg_id)
        if not poll_message.embeds:
            return
        embed = poll_message.embeds[0]
        if poll_message.author != bot.user:
            return
        if "ID da enquete:" not in embed.footer.text:
             return

        unformatted_options = [x.strip() for x in embed.description.split('\n')]
        opt_dict = {x[:2]: x[3:] for x in unformatted_options} if unformatted_options[0][0] == '1' \
            else {x[:1]: x[2:] for x in unformatted_options}
            # check if we're using numbers for the poll, or x/checkmark, parse accordingly
        voters = [bot.user.id]  # add the bot's ID to the list of voters to exclude it's votes

        tally = {x: 0 for x in opt_dict.keys()}
        for reaction in poll_message.reactions:
            if reaction.emoji in opt_dict.keys():
                reactors = await reaction.users().flatten()
                for reactor in reactors:
                    if reactor.id not in voters:
                        tally[reaction.emoji] += 1
                        voters.append(reactor.id)

        output = 'resultados da enquete "{}":\n'.format(embed.title) + \
                 '\n'.join(['{}: {}'.format(opt_dict[key], tally[key]) for key in tally.keys()])
        await ctx.channel.purge(limit=1)
        await ctx.send(output)

    @commands.command(help = 'concorda') #agrees or not
    async def concorda(self, ctx, *a:str):
        extra = ' '.join(a)
        if '?' in extra:
            variavelquenaovouusardenovo = 'n vou usar mesmo'
        else:
            simounao = randint(0,10)
            if simounao > 5:
                await message.channel.send(':thumbsdown:')
            if simounao < 5:
                await message.channel.send(':thumbsup:')
            if simounao == 5:
                await message.channel.send(':thinking: não sei')
    
    @commands.command(help = 'escolhe entre dois números') #chooses random number between two specified numbers
    async def entre(self, ctx, *numero: str):
        cont = 0
        meio = 0
        x = 0
        y = 0
        frase = ' '.join(numero)
        palavras = frase.split()
        
        for i in palavras:
            cont+=1
            if i == 'e':
                meio = cont
        if meio == 0:
            x = int(palavras[0])
            y = int(palavras[1])
        else:    
            for i in range(meio-1):
                x = int(palavras[i])
            for i in range(meio, cont):
                y = int(palavras[i])
            
        decide = aleatorios(y, 1, x)
        decisao = str(list(map(str, decide)))
        decisao = decisao.strip('[')
        decisao = decisao.strip(']')
        decisao = decisao.strip("'")
        decisao = decisao.strip("'")
        await ctx.send('escolhi ' +decisao)

class Image(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='leia', aliases=['ler'], help="lê o texto em uma foto") #tries to read text in image
    async def _ler(self, ctx, *lang:str):
        idiom = ' '.join(lang)
        if 'pt' in idiom:
            self.idioma = 'por'
        else:
            self.idioma = 'eng'

bot = commands.Bot(command_prefix='ednaldo ', case_insensitive=True, description="Ednaldo Pereira")
bot.add_cog(Music(bot))
bot.add_cog(Image(bot))
bot.add_cog(Text(bot))

@bot.event
async def on_ready():
    print('Logged in as: {0.user.name}  {0.user.id}'.format(bot))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="Ednaldo Pereira"))
    
@bot.event
async def on_command_error(ctx, error):
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        if isinstance(error, CommandNotFound):
            with open('text/ednaldo.txt', 'r', encoding='utf-8') as frase:
                leia = randint(0,29)
                linha = frase.readlines()
                await ctx.send(linha[leia])
                frase.close()
            return
        raise error

@bot.command(name='tchau', aliases=['bstop'])
@commands.is_owner()
async def botstop(ctx):
    await ctx.send('tchau')
    await bot.logout()
    return

bot.run(safeConf['discord']['token'])
