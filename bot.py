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
user_warnings = {}  # FIXED (no name conflict)

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower().strip() == "ncl":
        await message.channel.send(
            "🤨 Bro typed `ncl` and dipped...\n"
            "Try `nclhelp` before embarrassing yourself 😭"
        )

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
`nclbeg` — Beg for fun (luck might strike!) 🍀
""",
        inline=False
    )

    embed.add_field(
        name="🛡️ Staff & Moderator Commands",
        value="""
`nclclear <amount>` — Clears messages 🧹  
`nclwarn @user <reason>` — Warn a user ⚠️  
`nclwarnings @user` — See all warnings 📝  
`nclunwarn @user` — Remove all warnings ✅  
`ncltimeout @user <minutes>` — Timeout a user ⏳  
`ncluntimeout @user` — Remove timeout ⏱️  
`nclkick @user` — Kick a member 👢  
`nclban @user <reason>` — Ban a member 🔨  
`nclunban <user_id>` — Unban someone 🎉
""",
        inline=False
    )

    embed.add_field(
        name="👑 Founder / Co-Owner",
        value="Has access to **all commands**, basically the boss 💎",
        inline=False
    )

    embed.set_footer(text="💡 Tip: Use commands wisely… or hilariously! 😏")
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
    await ctx.send(random.choice([
        "You begged… and got nothing 💀",
        "Begging detected. Dignity lost 😭",
        "The bot felt bad… but still said no 😈"
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

# ================= WARN SYSTEM =================
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if get_power(ctx.author) < 40:
        return await ctx.send("❌ You cannot warn members.")

    if get_power(ctx.author) <= get_power(member):
        return await ctx.send("🚫 You cannot warn equal or higher role.")

    user_warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned.\nReason: **{reason}**")

@bot.command()
async def warnings(ctx, member: discord.Member):
    ws = user_warnings.get(member.id, [])
    if not ws:
        return await ctx.send(f"✅ {member.mention} has no warnings.")
    text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(ws))
    await ctx.send(f"⚠️ **Warnings for {member}:**\n{text}")

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Only Head Mod+ can clear warnings.")
    user_warnings.pop(member.id, None)
    await ctx.send(f"✅ Warnings cleared for {member.mention}")

# ================= MODERATION =================
@bot.command()
async def clear(ctx, amount: int):
    if get_power(ctx.author) < 40:
        return await ctx.send("❌ No permission.")
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=5)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if get_power(ctx.author) <= get_power(member):
        return await ctx.send("🚫 Cannot kick higher/equal role.")
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kicked | {reason}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if get_power(ctx.author) <= get_power(member):
        return await ctx.send("🚫 Cannot ban higher/equal role.")
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned | {reason}")

@bot.command()
async def unban(ctx, user_id: int):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ No permission.")
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    if get_power(ctx.author) <= get_power(member):
        return await ctx.send("🚫 Cannot timeout higher/equal role.")
    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"⏳ {member} timed out for {minutes} minutes")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if get_power(ctx.author) < 40:
        return await ctx.send("❌ No permission.")
    await member.timeout(None)
    await ctx.send(f"✅ Timeout removed for {member}")

# ================= RUN =================
bot.run(TOKEN)
