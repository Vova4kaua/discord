import discord
from discord.ext import commands, tasks
import asyncio
import os
from flask import Flask
from threading import Thread

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

OWNER_ID = 123456789012345678  # замените на свой ID

# Flask keep-alive
app = Flask('')

@app.route('/')
def home():
    return "✅ Бот працює!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.event
async def on_ready():
    print(f'Бот запущен как {bot.user}')

def is_owner():
    def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

@bot.command()
@is_owner()
async def mute(ctx):
    vc = ctx.author.voice.channel if ctx.author.voice else None
    if vc:
        for member in vc.members:
            if member.id != OWNER_ID:
                await member.edit(mute=True)
        await ctx.send("🔇 Все, кого можно, замучены.")
    else:
        await ctx.send("❗ Вы не находитесь в голосовом канале.")

@bot.command()
@is_owner()
async def open(ctx):
    vc = ctx.author.voice.channel if ctx.author.voice else None
    if vc:
        overwrite = vc.overwrites_for(ctx.guild.default_role)
        overwrite.connect = True
        await vc.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔓 Комната открыта.")
    else:
        await ctx.send("❗ Вы не находитесь в голосовом канале.")

@bot.command()
@is_owner()
async def close(ctx):
    vc = ctx.author.voice.channel if ctx.author.voice else None
    if vc:
        overwrite = vc.overwrites_for(ctx.guild.default_role)
        overwrite.connect = False
        await vc.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 Комната закрыта.")
    else:
        await ctx.send("❗ Вы не находитесь в голосовом канале.")

@bot.command()
@is_owner()
async def timer(ctx, seconds: int):
    await ctx.send(f"⏳ Таймер на {seconds} секунд запущен.")
    await asyncio.sleep(seconds)
    await ctx.send(f"⏰ Таймер завершен!")

@bot.command()
@is_owner()
async def unmute(ctx):
    vc = ctx.author.voice.channel if ctx.author.voice else None
    if vc:
        for member in vc.members:
            await member.edit(mute=False)
        await ctx.send("🔊 Все размучены.")
    else:
        await ctx.send("❗ Вы не находитесь в голосовом канале.")

@bot.command()
@is_owner()
async def kickall(ctx):
    vc = ctx.author.voice.channel if ctx.author.voice else None
    if vc:
        for member in vc.members:
            if member.id != OWNER_ID:
                await member.move_to(None)
        await ctx.send("👢 Все исключены из голосового канала.")
    else:
        await ctx.send("❗ Вы не находитесь в голосовом канале.")

@bot.command()
@is_owner()
async def locktext(ctx):
    channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Чат заблокирован.")

@bot.command()
@is_owner()
async def unlocktext(ctx):
    channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Чат разблокирован.")

@bot.command()
@is_owner()
async def say(ctx, *, text):
    await ctx.send(f"📣 {text}")

@bot.command()
@is_owner()
async def ping(ctx):
    await ctx.send(f"🏓 Пинг: {round(bot.latency * 1000)}мс")

@bot.command()
@is_owner()
async def purge(ctx, limit: int = 10):
    await ctx.channel.purge(limit=limit + 1)
    await ctx.send(f"🧹 Удалено {limit} сообщений.", delete_after=3)

@bot.command()
@is_owner()
async def rename(ctx, *, name):
    vc = ctx.author.voice.channel if ctx.author.voice else None
    if vc:
        await vc.edit(name=name)
        await ctx.send(f"✏️ Комната переименована в: {name}")
    else:
        await ctx.send("❗ Вы не находитесь в голосовом канале.")

@bot.command()
@is_owner()
async def users(ctx):
    vc = ctx.author.voice.channel if ctx.author.voice else None
    if vc:
        members = ", ".join([m.name for m in vc.members])
        await ctx.send(f"👥 Сейчас в канале: {members if members else 'Никого нет'}")
    else:
        await ctx.send("❗ Вы не находитесь в голосовом канале.")

@bot.command()
@is_owner()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
