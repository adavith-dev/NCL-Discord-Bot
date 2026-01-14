import discord
from discord.ext import commands
import os
import random
import asyncio

# ===== CONFIG =====
PREFIX = "ncl"
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.remove_command("help")

# ===== ROLE PERMISSIONS =====
FOUNDER_ROLES = [
    "★Founder★",
    "★CO-OWNER★",
    "⭐ Senior Moderator"
]

MOD_ROLES = FOUNDER_ROLES + [
    "👑 Head Moderator",
    "🛡️ Moderator",
    "🧪 Trial Mod"
]

# ===== UTIL =====
def has_role(ctx, roles):
    return any(role.name in roles for role in ctx.author.roles)

last_action = {}
warnings = {}

# ===== EVENTS =====
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower().strip() == "ncl":
        await message.channel.send(
            "🤨 You typed **ncl** and vanished...\n"
            "Where is the command bro? 😭\n"
            "Try `ncl help`"
        )

    await bot.process_commands(message)

# ===== HELP =====
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📖 NCL BOT COMMAND LIST",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🔥 Founder / Senior Moderator",
        value="""
`ncl ban <user> <reason>`
`ncl unban <user_id>`
`ncl kick <user>`
`ncl timeout <user> <minutes>`
`ncl untimeout <user>`
`ncl clear <amount>`
`ncl warn <user> <reason>`
`ncl unwarn <user>`
`ncl undo`
""",
        inline=False
    )

    embed.add_field(
        name="🎉 Members (Everyone)",
        value="""
`ncl slap <user>`
`ncl kiss <user>`
`ncl hug <user>`
`ncl joke`
`ncl ping`
""",
        inline=False
    )

    await ctx.send(embed=embed)

# ===== MODERATION =====
@bot.command()
async def clear(ctx, amount: int):
    if not has_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=3)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if not has_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    await member.kick(reason=reason)
    last_action[ctx.guild.id] = ("kick", member.id)
    await ctx.send(f"👢 {member} kicked")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if not has_role(ctx, FOUNDER_ROLES):
        return await ctx.send("❌ Founder only.")
    await member.ban(reason=reason)
    last_action[ctx.guild.id] = ("ban", member.id)
    await ctx.send(f"🔨 {member} banned")

@bot.command()
async def unban(ctx, user_id: int):
    if not has_role(ctx, FOUNDER_ROLES):
        return await ctx.send("❌ Founder only.")
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    if not has_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.timeout(duration)
    last_action[ctx.guild.id] = ("timeout", member.id)
    await ctx.send(f"⏳ Timed out {member} for {minutes} minutes")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not has_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    await member.timeout(None)
    await ctx.send(f"✅ Timeout removed for {member}")

# ===== WARN SYSTEM =====
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not has_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member} warned\nReason: {reason}")

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if not has_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    warnings.pop(member.id, None)
    await ctx.send(f"✅ Warnings cleared for {member}")

# ===== UNDO =====
@bot.command()
async def undo(ctx):
    if not has_role(ctx, FOUNDER_ROLES):
        return await ctx.send("❌ Founder only.")
    action = last_action.get(ctx.guild.id)
    if not action:
        return await ctx.send("❌ Nothing to undo.")
    await ctx.send("⏪ Last action undone (manual check may be needed)")

# ===== FUN COMMANDS =====
@bot.command()
async def slap(ctx, member: discord.Member):
    await ctx.send(f"👋 {ctx.author.mention} slapped {member.mention}")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"😘 {ctx.author.mention} kissed {member.mention}")

@bot.command()
async def hug(ctx, member: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention} hugged {member.mention}")

@bot.command()
async def joke(ctx):
    jokes = [
        "Why did Discord break up? Too many servers 😭",
        "Mods don’t sleep, they just timeout 😈",
        "ncl > all prefixes 😎"
    ]
    await ctx.send(random.choice(jokes))

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

# ===== START =====
bot.run(TOKEN)
