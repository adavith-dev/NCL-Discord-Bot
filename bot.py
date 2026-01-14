import discord
from discord.ext import commands
from datetime import timedelta
import os
import random

# ================= CONFIG =================
PREFIX = "ncl"
TOKEN = os.getenv("TOKEN")

# ================= ROLE IDS =================
FOUNDER_ID = 1457168593123803222
COOWNER_ID = 1457168593123803221
SENIOR_MOD_ID = 1458041286006276267
HEAD_MOD_ID = 1458041286006276267
MOD_ID = 1458040204781948938
TRIAL_MOD_ID = 1458040060472459488

# ================= POWER LEVELS =================
ROLE_POWER = {
    FOUNDER_ID: 100,
    COOWNER_ID: 100,
    SENIOR_MOD_ID: 100,   # SAME AS FOUNDER
    HEAD_MOD_ID: 80,
    MOD_ID: 60,
    TRIAL_MOD_ID: 40
}

def get_power(member: discord.Member):
    return max((ROLE_POWER.get(r.id, 0) for r in member.roles), default=0)

def is_god(member: discord.Member):
    return get_power(member) >= 100

# ================= INTENTS =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

warnings = {}

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

# ================= HELP =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 NCL MOD BOT COMMANDS",
        color=discord.Color.red()
    )

    embed.add_field(
        name="🎉 Fun (Everyone)",
        value="ncljoke\nnclmembers",
        inline=False
    )

    embed.add_field(
        name="🛡️ Admin (Staff)",
        value="""
nclwarn
nclunwarn
ncltimeout
ncluntimeout
nclkick
nclban
nclunban
nclclear
""",
        inline=False
    )

    embed.add_field(
        name="👑 Power System",
        value="Founder & Senior Mod have **FULL OVERRIDE**",
        inline=False
    )

    await ctx.send(embed=embed)

# ================= WARN =================
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not is_god(ctx.author):
        if get_power(ctx.author) < 40:
            return await ctx.send("❌ No permission.")
        if get_power(ctx.author) <= get_power(member):
            return await ctx.send("🚫 Cannot warn higher staff.")

    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned | {reason}")

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if not is_god(ctx.author):
        return await ctx.send("❌ Only Founder/Senior Mod")

    warnings.pop(member.id, None)
    await ctx.send(f"✅ Warnings cleared for {member.mention}")

# ================= TIMEOUT =================
@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    if not is_god(ctx.author):
        if get_power(ctx.author) <= get_power(member):
            return await ctx.send("🚫 Cannot timeout higher staff")

    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"⏳ {member.mention} timed out for {minutes} minutes")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not is_god(ctx.author):
        return await ctx.send("❌ Only Founder/Senior Mod")

    await member.timeout(None)
    await ctx.send(f"✅ Timeout removed")

# ================= BAN / KICK =================
@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if not is_god(ctx.author):
        if get_power(ctx.author) <= get_power(member):
            return await ctx.send("🚫 Cannot kick higher staff")

    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kicked")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if not is_god(ctx.author):
        if get_power(ctx.author) <= get_power(member):
            return await ctx.send("🚫 Cannot ban higher staff")

    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned")

@bot.command()
async def unban(ctx, user_id: int):
    if not is_god(ctx.author):
        return await ctx.send("❌ Only Founder/Senior Mod")

    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

# ================= CLEAR MESSAGES =================
@bot.command()
async def clear(ctx, amount: int):
    if not is_god(ctx.author) and get_power(ctx.author) < 60:
        return await ctx.send("❌ No permission")

    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Cleared {amount} messages")
    await msg.delete(delay=3)

# ================= SLASH COMMANDS =================
@bot.tree.command(name="timeout")
async def slash_timeout(interaction: discord.Interaction, member: discord.Member, minutes: int):
    if not is_god(interaction.user):
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    await member.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message(f"⏳ {member} timed out")

@bot.tree.command(name="ban")
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not is_god(interaction.user):
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member} banned")

@bot.tree.command(name="clear")
async def slash_clear(interaction: discord.Interaction, amount: int):
    if not is_god(interaction.user):
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Cleared {amount} messages", ephemeral=True)

# ================= FUN =================
@bot.command()
async def joke(ctx):
    await ctx.send("💀 This server is more cooked than my sleep schedule")

@bot.command()
async def members(ctx):
    await ctx.send(f"👥 Members: {ctx.guild.member_count}")

# ================= RUN =================
bot.run(TOKEN)
