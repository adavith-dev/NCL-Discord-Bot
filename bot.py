import discord
from discord.ext import commands
from datetime import datetime, timedelta
import os
import random

# ================= CONFIG =================
PREFIX = "ncl"
TOKEN = os.getenv("TOKEN")

# ================= ROLE IDS =================
FOUNDER_ID = 1457168593123803222
COOWNER_ID = 1457168593123803221
HEAD_MOD_ID = 1458041286006276267
MOD_ID = 1458040204781948938
TRIAL_MOD_ID = 1458040060472459488

# ================= POWER LEVELS =================
ROLE_POWER = {
    FOUNDER_ID: 100,
    COOWNER_ID: 95,
    HEAD_MOD_ID: 80,
    MOD_ID: 60,
    TRIAL_MOD_ID: 40
}

def get_power(member: discord.Member):
    power = 0
    for role in member.roles:
        power = max(power, ROLE_POWER.get(role.id, 0))
    return power

# ================= INTENTS =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ================= STORAGE =================
user_warnings = {}
user_afk = {}
user_coins = {}
user_xp = {}
user_levels = {}
user_marriages = {}

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = message.author.id
    # XP gain
    user_xp[uid] = user_xp.get(uid, 0) + random.randint(5,10)
    if user_xp[uid] >= (user_levels.get(uid,0)+1) * 100:
        user_levels[uid] = user_levels.get(uid,0) + 1
        await message.channel.send(f"🔥 {message.author.mention} leveled up to **Level {user_levels[uid]}**!")

    # AFK removal
    if uid in user_afk:
        user_afk.pop(uid)
        await message.channel.send(f"👋 Welcome back {message.author.mention}")

    # AFK mentions
    for m in message.mentions:
        if m.id in user_afk:
            await message.channel.send(f"😴 {m.display_name} is AFK — {user_afk[m.id]}")

    # Funny correction
    if message.content.lower().strip() in ["ncl","ncl help","nclhelp"]:
        await message.channel.send(random.choice([
            "🤡 Almost… try **nclhelp**",
            "😭 That ain’t it chief → **nclhelp**",
            "Skill issue detected. Use **nclhelp**"
        ]))

    await bot.process_commands(message)

# ================= HELP =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 NCL BOT COMMAND GUIDE",
        description="Here’s a guide to all the awesome commands you can use!\n**Prefix:** `ncl`",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🎉 Fun & Social Commands",
        value="""
`nclslap @user` — Slap someone 👋  
`nclkiss @user` — Send a smooch 💋  
`nclhug @user` — Hug your friends 🤗  
`nclpat @user` — Pat someone ✨  
`nclship @user1 @user2` — Ship two people ❤️  
`nclmembers` — Check total members 👥  
`ncljoke [@user]` — Get a random joke or roast 😎  
`nclbeg` — Beg for fun 🍀  
`nclroast @user` — Roast someone 🔥  
`nclrate @user` — Rate a user ⭐  
`ncl8ball <question>` — Ask the magic 8-ball 🎱  
`nclafk <reason>` — Set AFK status 😴
""", inline=False
    )

    embed.add_field(
        name="📩 Invites & Profile",
        value="""
`nclprofile [@user]` — View profile 📊  
`nclinvites [@user]` — Check invites 📩  
`nclinviteboard` — Invite leaderboard 🏆  
`ncldaily` — Daily reward 💸  
`nclbalance` — Check coins 💰
""", inline=False
    )

    embed.add_field(
        name="🎁 Events",
        value="""
`nclgiveaway <minutes>` — Start giveaway 🎁  
`nclconfess <message>` — Anonymous confession 😶‍🌫️
""", inline=False
    )

    embed.add_field(
        name="🛡️ Staff & Moderator Commands",
        value="""
`nclclear <amount>` — Clear messages 🧹  
`nclpurge @user <amount>` — Purge user messages 🗑️  
`nclwarn @user <reason>` — Warn a user ⚠️  
`nclwarnings @user` — View warnings 📝  
`nclunwarn @user` — Clear warnings ✅  
`ncltimeout @user <minutes>` — Timeout ⏳  
`ncluntimeout @user` — Remove timeout ⏱️  
`nclmute @user` — Mute user 🔇  
`nclunmute @user` — Unmute user 🔊  
`nclslowmode <seconds>` — Set slowmode 🐢  
`ncllock` — Lock channel 🔒  
`nclunlock` — Unlock channel 🔓  
`nclkick @user` — Kick member 👢  
`nclban @user <reason>` — Ban member 🔨  
`nclunban <user_id>` — Unban member 🎉
""", inline=False
    )

    embed.add_field(
        name="👑 Founder / Co-Owner",
        value="Has access to all commands, basically the boss 💎", inline=False
    )

    embed.set_footer(text="Tip: Use commands wisely… or hilariously 😏")
    await ctx.send(embed=embed)

# ================= FUN COMMANDS =================
@bot.command()
async def slap(ctx, member: discord.Member):
    await ctx.send(f"👋 {ctx.author.mention} slapped {member.mention}")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention} kissed {member.mention}")

@bot.command()
async def hug(ctx, member: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention} hugged {member.mention}")

@bot.command()
async def pat(ctx, member: discord.Member):
    await ctx.send(f"✨ {ctx.author.mention} patted {member.mention}")

@bot.command()
async def ship(ctx, user1: discord.Member, user2: discord.Member):
    await ctx.send(f"❤️ {user1.mention} x {user2.mention} — **SHIPPED**")

@bot.command()
async def members(ctx):
    await ctx.send(f"👥 Total members: **{ctx.guild.member_count}**")

@bot.command()
async def beg(ctx):
    coins = random.randint(0,5)
    user_coins[ctx.author.id] = user_coins.get(ctx.author.id,0)+coins
    await ctx.send(random.choice([
        f"💰 You begged and got {coins} coins",
        "💀 You begged… and got nothing" if coins==0 else "",
        "😭 The bot laughed at your begging" if coins>0 else ""
    ]))

@bot.command()
async def joke(ctx, member: discord.Member = None):
    jokes = [
        "This server runs better than my life 💀",
        "Mods don’t sleep, they just timeout 😭",
        "Why do programmers hate nature? Too many bugs 🐛",
        "Discord mods when someone types @everyone 😡",
        "Skill issue detected 🤡"
    ]
    if member:
        jokes += [
            f"{member.mention} lagged so hard even Discord felt it 💀",
            f"{member.mention} has more confidence than skill 😭",
            f"{member.mention} tried… that’s what matters 🤡"
        ]
    await ctx.send(random.choice(jokes))

# ================= PROFILE / COINS =================
@bot.command()
async def profile(ctx, member: discord.Member=None):
    member = member or ctx.author
    await ctx.send(
        f"👤 **{member}**\n"
        f"📊 Level: {user_levels.get(member.id,0)}\n"
        f"✨ XP: {user_xp.get(member.id,0)}\n"
        f"💰 Coins: {user_coins.get(member.id,0)}"
    )

@bot.command()
async def balance(ctx, member: discord.Member=None):
    member = member or ctx.author
    await ctx.send(f"💰 {member.mention} has {user_coins.get(member.id,0)} coins")

# ================= RUN =================
bot.run(TOKEN)
