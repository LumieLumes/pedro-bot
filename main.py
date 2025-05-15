from discord.ext import commands
from keep_alive import keep_alive
import os
import discord

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")

@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong!')

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
