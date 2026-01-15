import discord
from discord.ext import commands
from datetime import datetime, timedelta
import os
import random
import asyncio

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
user_warnings = {}  # Warnings storage
afk_users = {}      # AFK storage
daily_claim = {}    # Daily rewards
coins = {}          # Coins storage
guild_invites = {}  # Guild invites
user_invites = {}   # User invite counts

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # Fetch invites for all guilds
    for guild in bot.guilds:
        invs = await guild.invites()
        guild_invites[guild.id] = {i.code: i.uses for i in invs}

@bot.event
async def on_member_join(member):
    invites = await member.guild.invites()
    for i in invites:
        previous_uses = guild_invites[member.guild.id].get(i.code, 0)
        if i.uses > previous_uses:
            inviter_id = i.inviter.id
            user_invites[inviter_id] = user_invites.get(inviter_id, 0) + 1
            guild_invites[member.guild.id][i.code] = i.uses
            break

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # AFK removal
    if message.author.id in afk_users:
        afk_users.pop(message.author.id)
        await message.channel.send(f"👋 Welcome back {message.author.mention}")

    # AFK mention
    for m in message.mentions:
        if m.id in afk_users:
            await message.channel.send(f"😴 {m.display_name} is AFK — {afk_users[m.id]}")

    # Funny corrections
    if message.content.lower().strip() in ["ncl", "ncl help", "nclinvite"]:
        await message.channel.send(random.choice([
            "🤡 Almost… try `nclhelp`",
            "😭 That ain’t it chief → `nclhelp`",
            "Skill issue detected. Use `nclhelp`"
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
        value="""\
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
""",
        inline=False
    )

    embed.add_field(
        name="📩 Invites & Profile",
        value="""\
`nclprofile [@user]` — View profile 📊  
`nclinvites [@user]` — Check invites 📩  
`nclinviteboard` — Invite leaderboard 🏆  
`ncldaily` — Daily reward 💸
""",
        inline=False
    )

    embed.add_field(
        name="🎁 Events",
        value="""\
`nclgiveaway <minutes>` — Start giveaway 🎁  
`nclconfess <message>` — Anonymous confession 😶‍🌫️
""",
        inline=False
    )

    embed.add_field(
        name="🛡️ Staff & Moderator Commands",
        value="""\
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
""",
        inline=False
    )

    embed.add_field(
        name="👑 Founder / Co-Owner",
        value="Has access to all commands, basically the boss 💎",
        inline=False
    )

    embed.set_footer(text="💡 Tip: Use commands wisely… or hilariously 😏")
    await ctx.send(embed=embed)

# ================= FUN =================
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
    reward = random.choice([0, 5])
    coins[ctx.author.id] = coins.get(ctx.author.id, 0) + reward
    if reward == 0:
        await ctx.send("💀 You begged but got nothing.")
    else:
        await ctx.send(f"💸 Luck strikes! You got {reward} coins!")

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

# ================= AFK =================
@bot.command()
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = reason
    await ctx.send(f"😴 {ctx.author.mention} is now AFK — {reason}")

# ================= PROFILE =================
@bot.command()
async def profile(ctx, member: discord.Member=None):
    member = member or ctx.author
    await ctx.send(
        f"👤 **{member.display_name}**\n"
        f"💰 Coins: {coins.get(member.id,0)}\n"
        f"📩 Invites: {user_invites.get(member.id,0)}\n"
        f"⚠️ Warnings: {len(user_warnings.get(member.id,[]))}"
    )

@bot.command()
async def daily(ctx):
    now = datetime.utcnow()
    last = daily_claim.get(ctx.author.id)
    if last and (now - last).seconds < 86400:
        await ctx.send("⏳ You have already claimed your daily reward today.")
    else:
        reward = random.randint(10,50)
        coins[ctx.author.id] = coins.get(ctx.author.id,0) + reward
        daily_claim[ctx.author.id] = now
        await ctx.send(f"💸 Daily reward claimed! You got {reward} coins.")

# ================= INVITES =================
@bot.command()
async def invites(ctx, member: discord.Member=None):
    member = member or ctx.author
    count = user_invites.get(member.id, 0)
    if count == 0:
        await ctx.send(f"💀 {member.display_name} has invited 0 people. Sad!")
    else:
        await ctx.send(f"📩 {member.display_name} has invited {count} people!")

@bot.command()
async def inviteboard(ctx):
    if not user_invites:
        return await ctx.send("😶 No invites yet.")
    top = sorted(user_invites.items(), key=lambda x:x[1], reverse=True)[:5]
    text = ""
    for i, (uid, count) in enumerate(top,1):
        user = await bot.fetch_user(uid)
        text += f"{i}. {user} — {count} invites\n"
    await ctx.send(f"🏆 **Invite Leaderboard**\n{text}")

# ================= RUN =================
bot.run(TOKEN)

