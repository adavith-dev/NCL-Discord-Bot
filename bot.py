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
user_warnings = {}

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

# ================= HELP (UPDATED ONLY) =================
@bot.command()
async def help(ctx):
    await ctx.send(
        "**NCL BOT COMMAND GUIDE**\n"
        "Here’s a guide to all the awesome commands you can use!\n"
        "**Prefix:** `ncl`\n\n"

        "🎉 **Fun & Social Commands**\n"
        "`nclslap @user` — Slap someone 👋\n"
        "`nclkiss @user` — Send a smooch 💋\n"
        "`nclhug @user` — Hug your friends 🤗\n"
        "`nclpat @user` — Pat someone ✨\n"
        "`nclship @user1 @user2` — Ship two people ❤️\n"
        "`nclmembers` — Check total members 👥\n"
        "`ncljoke [@user]` — Get a random joke or roast 😎\n"
        "`nclbeg` — Beg for fun 🍀\n"
        "`nclroast @user` — Roast someone 🔥\n"
        "`nclrate @user` — Rate a user ⭐\n"
        "`ncl8ball <question>` — Ask the magic 8-ball 🎱\n"
        "`nclafk <reason>` — Set AFK status 😴\n\n"

        "📩 **Invites & Profile**\n"
        "`nclprofile [@user]` — View profile 📊\n"
        "`nclinvites [@user]` — Check invites 📩\n"
        "`nclinviteboard` — Invite leaderboard 🏆\n"
        "`ncldaily` — Daily reward 💸\n\n"

        "🎁 **Events**\n"
        "`nclgiveaway <minutes>` — Start giveaway 🎁\n"
        "`nclconfess <message>` — Anonymous confession 😶‍🌫️\n\n"

        "🛡️ **Staff & Moderator Commands**\n"
        "`nclclear <amount>` — Clear messages 🧹\n"
        "`nclpurge @user <amount>` — Purge user messages 🗑️\n"
        "`nclwarn @user <reason>` — Warn a user ⚠️\n"
        "`nclwarnings @user` — View warnings 📝\n"
        "`nclunwarn @user` — Clear warnings ✅\n"
        "`ncltimeout @user <minutes>` — Timeout ⏳\n"
        "`ncluntimeout @user` — Remove timeout ⏱️\n"
        "`nclmute @user` — Mute user 🔇\n"
        "`nclunmute @user` — Unmute user 🔊\n"
        "`nclslowmode <seconds>` — Set slowmode 🐢\n"
        "`ncllock` — Lock channel 🔒\n"
        "`nclunlock` — Unlock channel 🔓\n"
        "`nclkick @user` — Kick member 👢\n"
        "`nclban @user <reason>` — Ban member 🔨\n"
        "`nclunban <user_id>` — Unban member 🎉\n\n"

        "👑 **Founder / Co-Owner**\n"
        "Has access to all commands, basically the boss 💎\n\n"
        "_Tip: Use commands wisely… or hilariously 😏_"
    )

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
