import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="ncl", intents=intents)

DATA_FILE = "data.json"

# ----------------- DATA HANDLING -----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user(data, user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "coins": 0,
            "warnings": [],
            "last_daily": "",
            "invites": 0
        }
    return data[user_id]

# ----------------- BOT READY -----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ----------------- INVITE TRACKER -----------------
invites_cache = {}

@bot.event
async def on_guild_join(guild):
    invites_cache[guild.id] = await guild.invites()

@bot.event
async def on_ready():
    for guild in bot.guilds:
        invites_cache[guild.id] = await guild.invites()
    print("✅ Invite tracker ready")

@bot.event
async def on_member_join(member):
    data = load_data()
    before = invites_cache[member.guild.id]
    after = await member.guild.invites()

    for invite in after:
        for old in before:
            if invite.code == old.code and invite.uses > old.uses:
                user = get_user(data, invite.inviter.id)
                user["invites"] += 1
                save_data(data)
                break

    invites_cache[member.guild.id] = after

# ----------------- FUN COMMANDS -----------------
@bot.command()
async def beg(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)
    if random.choice([True, False]):
        user["coins"] += 5
        await ctx.send("🍀 Someone felt bad and gave you **5 coins**!")
    else:
        await ctx.send("🥲 You begged… and got ignored.")
    save_data(data)

@bot.command()
async def slap(ctx, member: discord.Member):
    await ctx.send(f"👋 {ctx.author.mention} slapped {member.mention}!")

@bot.command()
async def hug(ctx, member: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention} hugged {member.mention}!")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention} kissed {member.mention}!")

@bot.command()
async def pat(ctx, member: discord.Member):
    await ctx.send(f"✨ {ctx.author.mention} patted {member.mention}!")

@bot.command()
async def ship(ctx, user1: discord.Member, user2: discord.Member):
    percent = random.randint(1, 100)
    await ctx.send(f"❤️ **{user1.name} x {user2.name}** = `{percent}%` love!")

# ----------------- ECONOMY -----------------
@bot.command()
async def daily(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)
    today = str(datetime.date.today())

    if user["last_daily"] == today:
        await ctx.send("⏰ You already claimed your daily today!")
        return

    user["coins"] += 50
    user["last_daily"] = today
    save_data(data)
    await ctx.send("💸 You claimed **50 daily coins**!")

# ----------------- PROFILE -----------------
@bot.command()
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    user = get_user(data, member.id)

    embed = discord.Embed(title=f"📊 {member.name}'s Profile", color=discord.Color.blue())
    embed.add_field(name="💰 Coins", value=user["coins"])
    embed.add_field(name="⚠️ Warnings", value=len(user["warnings"]))
    embed.add_field(
        name="📩 Invites",
        value=(
            "💀 Zero invites… touch grass 😭"
            if user["invites"] == 0
            else f"🔥 {user['invites']} people joined because of you!"
        ),
        inline=False
    )
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

# ----------------- INVITES -----------------
@bot.command()
async def invites(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    user = get_user(data, member.id)

    if user["invites"] == 0:
        await ctx.send("📩 You have **0 invites**… invite your pet bro 😭")
    else:
        await ctx.send(f"📩 {member.name} has **{user['invites']} invites** 🔥")

@bot.command()
async def inviteboard(ctx):
    data = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1]["invites"], reverse=True)

    embed = discord.Embed(title="🏆 Invite Leaderboard", color=discord.Color.gold())
    rank = 1
    for user_id, info in sorted_users[:10]:
        user = await bot.fetch_user(int(user_id))
        embed.add_field(
            name=f"#{rank} {user.name}",
            value=f"📩 {info['invites']} invites",
            inline=False
        )
        rank += 1

    await ctx.send(embed=embed)

# ----------------- MODERATION -----------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send("👢 User kicked.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send("🔨 User banned.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send("🎉 User unbanned.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int):
    await member.timeout(datetime.timedelta(minutes=minutes))
    await ctx.send("🔇 User muted.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send("🔊 User unmuted.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason):
    data = load_data()
    user = get_user(data, member.id)
    user["warnings"].append(reason)
    save_data(data)
    await ctx.send("⚠️ Warning added.")

@bot.command()
async def warnings(ctx, member: discord.Member):
    data = load_data()
    user = get_user(data, member.id)
    await ctx.send(f"📝 Warnings: {len(user['warnings'])}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def unwarn(ctx, member: discord.Member):
    data = load_data()
    user = get_user(data, member.id)
    user["warnings"] = []
    save_data(data)
    await ctx.send("✅ All warnings cleared.")

# ----------------- HELP (YOUR EXACT VERSION) -----------------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🚀 NCL BOT — Command Guide",
        description=(
            "**Prefix:** `ncl`\n\n"
            "NCL Bot is packed with fun, economy, profile, and moderation features.\n"
            "Here’s everything you can use 👇"
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎉 Fun & Social Commands",
        value=(
            "`nclslap @user` 👋 — Slap someone for fun\n"
            "`nclkiss @user` 💋 — Send a kiss\n"
            "`nclhug @user` 🤗 — Hug a member\n"
            "`nclpat @user` ✨ — Pat someone\n"
            "`nclship @user1 @user2` ❤️ — Ship two users\n"
            "`nclbeg` 🍀 — Beg for coins (5 coins or nothing)"
        ),
        inline=False
    )

    embed.add_field(
        name="📊 Profile & Economy",
        value=(
            "`nclprofile [@user]` 📊 — View profile stats\n"
            "`ncldaily` 💸 — Claim daily coins (once every 24h)\n"
            "`nclinvites [@user]` 📩 — Check invite count\n"
            "`nclinviteboard` 🏆 — Server invite leaderboard"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Moderation Commands",
        value=(
            "`nclclear <amount>` 🧹 — Delete messages\n"
            "`nclwarn @user <reason>` ⚠️ — Warn a member\n"
            "`nclwarnings @user` 📝 — View warnings\n"
            "`nclunwarn @user` ✅ — Clear all warnings\n"
            "`nclmute @user <minutes>` 🔇 — Timeout a member\n"
            "`nclunmute @user` 🔊 — Remove timeout\n"
            "`nclkick @user` 👢 — Kick a member\n"
            "`nclban @user <reason>` 🔨 — Ban a member\n"
            "`nclunban <user_id>` 🎉 — Unban using user ID"
        ),
        inline=False
    )

    embed.set_footer(text="💡 Tip: Use commands wisely… or hilariously 😏")
    await ctx.send(embed=embed)

# ----------------- RUN -----------------
bot.run(os.getenv("TOKEN"))
