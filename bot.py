import discord
from discord.ext import commands
from datetime import timedelta
import os
import random

# ================= BASIC CONFIG =================
PREFIX = "ncl"
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ================= ROLE IDS =================
FOUNDER_ID    = 1457168593123803222
COOWNER_ID    = 1457168593123803221
HEAD_MOD_ID   = 1458041286006276267
MOD_ID        = 1458040204781948938
TRIAL_MOD_ID  = 1458040060472459488

# ================= WARN STORAGE =================
warnings_db = {}

# ================= POWER SYSTEM =================
def get_power(member: discord.Member):
    if any(r.id == FOUNDER_ID for r in member.roles):
        return 100
    if any(r.id == COOWNER_ID for r in member.roles):
        return 95
    if any(r.id == HEAD_MOD_ID for r in member.roles):
        return 80
    if any(r.id == MOD_ID for r in member.roles):
        return 60
    if any(r.id == TRIAL_MOD_ID for r in member.roles):
        return 40
    return 0

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= HELP =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 NCL BOT COMMANDS",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🎉 Fun",
        value="""
ncljoke [@user]  
nclmembers
""",
        inline=False
    )

    embed.add_field(
        name="🛡️ Moderation",
        value="""
nclclear <amount>  
nclwarn @user <reason>  
nclwarnings @user  
nclunwarn @user  
ncltimeout @user <minutes>  
ncluntimeout @user  
nclkick @user  
nclban @user  
nclunban <id>
""",
        inline=False
    )

    embed.add_field(
        name="👑 Rule",
        value="You **cannot** punish equal or higher staff.",
        inline=False
    )

    await ctx.send(embed=embed)

# ================= CLEAR =================
@bot.command()
async def clear(ctx, amount: int):
    if get_power(ctx.author) < 60:
        return await ctx.send("❌ No permission.")

    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=3)

# ================= WARN SYSTEM =================
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if get_power(ctx.author) < 60:
        return await ctx.send("❌ You can't warn members.")

    if get_power(ctx.author) <= get_power(member):
        return await ctx.send("🚫 You cannot warn higher or equal staff.")

    warnings_db.setdefault(member.id, []).append(reason)
    await ctx.send(
        f"⚠️ **WARNED**\nUser: {member.mention}\nReason: **{reason}**"
    )

@bot.command()
async def warnings(ctx, member: discord.Member):
    warns = warnings_db.get(member.id, [])
    if not warns:
        return await ctx.send(f"✅ {member.mention} has no warnings.")

    text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(warns))
    await ctx.send(f"📋 **Warnings for {member.mention}:**\n{text}")

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Head Mod+ only.")

    warnings_db.pop(member.id, None)
    await ctx.send(f"✅ Warnings cleared for {member.mention}")

# ================= TIMEOUT =================
@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Head Mod+ only.")

    if get_power(ctx.author) <= get_power(member):
        return await ctx.send("🚫 Cannot timeout higher staff.")

    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"⏳ {member.mention} timed out for {minutes} minutes")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Head Mod+ only.")

    await member.timeout(None)
    await ctx.send(f"✅ Timeout removed for {member.mention}")

# ================= KICK / BAN =================
@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Head Mod+ only.")

    if get_power(ctx.author) <= get_power(member):
        return await ctx.send("🚫 Cannot kick higher staff.")

    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kicked")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if get_power(ctx.author) < 95:
        return await ctx.send("❌ Admin+ only.")

    if get_power(ctx.author) <= get_power(member):
        return await ctx.send("🚫 Cannot ban higher staff.")

    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned")

@bot.command()
async def unban(ctx, user_id: int):
    if get_power(ctx.author) < 95:
        return await ctx.send("❌ Admin+ only.")

    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

# ================= FUN =================
@bot.command()
async def joke(ctx, member: discord.Member = None):
    jokes = [
        "Bro lagged harder than server restart 💀",
        "This bot works better than my sleep schedule 😭",
        "Mods watching chat like 👁️👄👁️"
    ]

    if member:
        await ctx.send(f"{member.mention} {random.choice(jokes)}")
    else:
        await ctx.send(random.choice(jokes))

@bot.command()
async def members(ctx):
    await ctx.send(f"👥 Total members: **{ctx.guild.member_count}**")

# ================= RUN =================
bot.run(TOKEN)
