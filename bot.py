import discord
from discord.ext import commands
import os, random, re
from datetime import datetime, timedelta
import psycopg2

# ================= BOT SETUP =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="ncl", intents=intents, help_command=None)

# ================= ROLE IDS =================
FOUNDER_ID   = 1457168593123803222
COOWNER_ID   = 1457168593123803221
HEAD_MOD_ID  = 1458041286006276267
MOD_ID       = 1458040204781948938
TRIAL_MOD_ID = 1458040060472459488

VIP_ROLE_ID  = 1460000000000000000  # CHANGE THIS

ROLE_POWER = {
    FOUNDER_ID: 100,
    COOWNER_ID: 95,
    HEAD_MOD_ID: 80,
    MOD_ID: 60,
    TRIAL_MOD_ID: 40
}

def get_power(member):
    return max((ROLE_POWER.get(r.id, 0) for r in member.roles), default=0)

def can_punish(ctx, target):
    return get_power(ctx.author) > get_power(target)

# ================= DATABASE =================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

def execute(query, params=(), fetch=False):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                conn.commit()
    except Exception as e:
        print(f"DB ERROR: {e}")
        return None

# ================= TABLES =================
execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    invites INTEGER DEFAULT 0
)
""")

execute("""
CREATE TABLE IF NOT EXISTS warnings (
    user_id BIGINT,
    reason TEXT
)
""")

execute("""
CREATE TABLE IF NOT EXISTS profiles (
    user_id BIGINT PRIMARY KEY,
    nickname TEXT,
    emoji TEXT,
    bio TEXT,
    color TEXT
)
""")

def get_user(uid):
    execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (uid,))

# ================= READY =================
invites_cache = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    for g in bot.guilds:
        try:
            invites_cache[g.id] = await g.invites()
        except:
            invites_cache[g.id] = []

# ================= INVITES =================
@bot.event
async def on_member_join(member):
    before = invites_cache.get(member.guild.id, [])
    try:
        after = await member.guild.invites()
    except:
        after = []

    for i in after:
        for b in before:
            if i.code == b.code and i.uses > b.uses:
                get_user(i.inviter.id)
                execute(
                    "UPDATE users SET invites = invites + 1, coins = coins + 25 WHERE user_id=%s",
                    (i.inviter.id,)
                )
                break
    invites_cache[member.guild.id] = after

# ================= ECONOMY =================
daily_cooldowns = {}

@bot.command(aliases=["bal"])
async def nclbalance(ctx):
    get_user(ctx.author.id)
    coins = execute("SELECT coins FROM users WHERE user_id=%s", (ctx.author.id,), fetch=True)
    coins = coins[0][0] if coins else 0
    await ctx.send(f"💰 You have **{coins} coins**")

@bot.command(aliases=["daily"])
async def ncldaily(ctx):
    uid = ctx.author.id
    now = datetime.utcnow()
    if uid in daily_cooldowns and now - daily_cooldowns[uid] < timedelta(hours=24):
        remaining = timedelta(hours=24) - (now - daily_cooldowns[uid])
        h, r = divmod(int(remaining.total_seconds()), 3600)
        m, s = divmod(r, 60)
        return await ctx.send(f"⏳ Wait {h}h {m}m {s}s")

    get_user(uid)
    execute("UPDATE users SET coins = coins + 50 WHERE user_id=%s", (uid,))
    daily_cooldowns[uid] = now
    await ctx.send("💸 You got **50 daily coins**")

# ================= HELP COMMAND =================
@bot.command(name="help", aliases=["nclhelp"])
async def help_command(ctx):
    embed = discord.Embed(
        title="📘 NCL MOD BOT HELP",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🛠 Admin Commands",
        value=(
            "`nclban @user reason`\n"
            "`nclunban user_id`\n"
            "`nclmute @user`\n"
            "`nclunmute @user`\n"
            "`nclwarn @user reason`\n"
            "`nclunwarn @user`\n"
        ),
        inline=False
    )

    embed.add_field(
        name="⚙ Utility",
        value="`nclping` - bot latency",
        inline=False
    )

    embed.set_footer(text="NCL MOD BOT • clean & stable")
    await ctx.send(embed=embed)

# ================= WARN =================
@bot.command(aliases=["warn"])
async def nclwarn(ctx, member: discord.Member, *, reason="No reason"):
    if not can_punish(ctx, member):
        return await ctx.send("🚫 Cannot warn higher role")
    get_user(member.id)
    execute("INSERT INTO warnings VALUES (%s,%s)", (member.id, reason))
    count = execute("SELECT COUNT(*) FROM warnings WHERE user_id=%s", (member.id,), fetch=True)
    count = count[0][0] if count else 0

    if count >= 5:
        try:
            await member.ban(reason="Auto-ban: 5 warnings")
        except:
            pass
        await ctx.send("🔨 AUTO-BANNED (5 WARNINGS)")
    else:
        await ctx.send(f"⚠️ Warning added ({count}/5)")

@bot.command(aliases=["unwarn"])
async def nclunwarn(ctx, member: discord.Member):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Head Mod+ only")
    execute("DELETE FROM warnings WHERE user_id=%s", (member.id,))
    await ctx.send("✅ Warnings cleared")

# ================= MODERATION =================
@bot.command(aliases=["kick"])
async def nclkick(ctx, member: discord.Member):
    if not can_punish(ctx, member):
        return await ctx.send("🚫 Cannot kick higher role")
    try:
        await member.kick()
    except:
        pass
    await ctx.send("👢 User kicked")

@bot.command(aliases=["ban"])
async def nclban(ctx, member: discord.Member):
    if not can_punish(ctx, member):
        return await ctx.send("🚫 Cannot ban higher role")
    try:
        await member.ban()
    except:
        pass
    await ctx.send("🔨 User banned")

@bot.command(aliases=["unban"])
async def nclunban(ctx, user: str):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Head Mod+ only")

    try:
        user_id = int(re.sub(r"[<@!>]", "", user))
        banned = await ctx.guild.bans()
        for ban_entry in banned:
            if ban_entry.user.id == user_id:
                await ctx.guild.unban(ban_entry.user)
                return await ctx.send("🎉 User unbanned")
        await ctx.send("❌ User not banned")
    except Exception as e:
        await ctx.send(f"❌ Failed to unban: {e}")

# ================= RUN =================
bot.run(os.getenv("TOKEN"))
