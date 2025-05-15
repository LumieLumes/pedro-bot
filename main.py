import discord
from discord.ext import commands
import asyncio
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

queue = asyncio.Queue()
playing = False

async def is_playing(ctx):
    vc = ctx.voice_client
    return vc and vc.is_playing()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("🎵 Joined the voice channel.")
    else:
        await ctx.send("❌ You're not in a voice channel.")

@bot.command()
async def play(ctx, url):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ You're not in a voice channel.")
            return

    await queue.put((ctx, url))
    if not bot.loop.create_task(is_playing(ctx)):
        await play_next(ctx)

async def play_next(ctx):
    global playing
    if queue.empty():
        playing = False
        return

    ctx, url = await queue.get()
    playing = True
    await ctx.send(f"🎶 Now playing: {url}")

    vc = ctx.voice_client
    vc.stop()

    ffmpeg_options = {
        'options': '-vn'
    }

    ytdl_options = {
        'format': 'bestaudio/best',
        'noplaylist': True
    }

    import yt_dlp
    with yt_dlp.YoutubeDL(ytdl_options) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_options)
    vc.play(source, after=lambda e: bot.loop.create_task(play_next(ctx)))

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped.")
    else:
        await ctx.send("❌ Nothing is playing.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel.")
    else:
        await ctx.send("❌ I'm not in a voice channel.")

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
