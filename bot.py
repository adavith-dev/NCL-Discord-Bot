import discord
from discord.ext import commands
from datetime import timedelta
import os
import random

# ---------- CONFIG ----------
PREFIX = "ncl"
TOKEN = os.getenv("TOKEN")

BOOST_CHANNEL_ID = 1460708408343658672
INVITE_CHANNEL_ID = 1457800213250179104

# ---------- ROLE NAMES ----------
ROLE_FOUNDER = "★Founder★"
ROLE_COOWNER = "★ CO-OWNER ★"
ROLE_HEAD_MOD = "👑 Head Moderator"
ROLE_MOD = "🛡️ Moderator"
ROLE_TRIAL_MOD = "🧪 Trial Mod"
ROLE_STAFF = "🛠️ Staff"
ROLE_SENIOR_STAFF = "⭐ Senior Staff"
ROLE_HEAD_STAFF = "👑 Head Staff"

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------- DATA ----------
invites = {}
warnings = {}

# ---------- UTIL ----------
def has_any_role(ctx, roles):
    return any(role.name in roles for role in ctx.author.roles)

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    for guild in bot.guilds:
        invites[guild.id] = await guild.invites()
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower().strip()

    # Fun response for 'ncl' only
    if content == "ncl":
        fun_responses = [
            "💀 Bro you forgot the rest! Try `ncl help` 😭",
            "🤨 You just typed `ncl` and vanished… Commands went missing!",
            "👀 Psst! I need more than `ncl`… try `ncl help` 😉"
        ]
        await message.channel.send(random.choice(fun_responses))

    # Fun response for malformed 'ncl help'
    elif content.startswith("ncl") and "help" in content and content != "ncl help":
        funny_fix = [
            "😂 Close! Just type `ncl help` without extra spaces.",
            "🙃 Hmm… Did you mean `ncl help`? Try that!",
            "🤔 Almost! `ncl help` is the magic phrase."
        ]
        await message.channel.send(random.choice(funny_fix))

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    before = invites.get(member.guild.id, [])
    after = await member.guild.invites()

    for invite in after:
        old = next((i for i in before if i.code == invite.code), None)
        if old and invite.uses > old.uses:
            channel = member.guild.get_channel(INVITE_CHANNEL_ID)
            if channel:
                await channel.send(
                    f"🎉 {member.mention} joined using **{invite.inviter}** invite!"
                )
    invites[member.guild.id] = after

@bot.event
async def on_member_update(before, after):
    if not before.premium_since and after.premium_since:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            await channel.send(
                f"🚀 **THANK YOU {after.mention} FOR BOOSTING THE SERVER!**"
            )

# ---------- HELP ----------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 NCL BOT COMMANDS",
        description="Prefix: **ncl**",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎮 Member Commands",
        value="""
nclslap @user
nclkiss @user
nclhug @user
nclpat @user
nclship @user1 @user2
nclmembers
""",
        inline=False
    )

    embed.add_field(
        name="🛡️ Staff & Mod Commands",
        value="""
🛠️ Staff+
• nclclear <amount>

🧪 Trial Mod+
• nclwarn @user reason
• nclwarnings @user
• nclunwarn @user
• ncltimeout @user minutes
• ncluntimeout @user

👑 Head Moderator+
• nclkick @user
• nclban @user
• nclunban user_id
""",
        inline=False
    )

    embed.add_field(
        name="👑 Founder / Co-Owner",
        value="All commands",
        inline=False
    )

    embed.add_field(
        name="📊 Server Stats / Invites",
        value="""
nclinviteboard → Show top inviters
""",
        inline=False
    )

    await ctx.send(embed=embed)

# ---------- FUN ----------
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
    await ctx.send(f"❤️ {user1.mention} x {user2.mention} — **SHIPPED!**")

@bot.command()
async def members(ctx):
    await ctx.send(f"👥 Total members: **{ctx.guild.member_count}**")

# ---------- WARN SYSTEM ----------
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not has_any_role(ctx, [
        ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER
    ]):
        return await ctx.send("❌ You cannot warn members.")

    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned.\nReason: **{reason}**")

@bot.command()
async def warnings(ctx, member: discord.Member):
    user_warnings = warnings.get(member.id, [])
    if not user_warnings:
        return await ctx.send(f"✅ {member.mention} has no warnings.")

    text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(user_warnings))
    await ctx.send(f"⚠️ **Warnings for {member}:**\n{text}")

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if not has_any_role(ctx, [
        ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER
    ]):
        return await ctx.send("❌ No permission.")

    warnings.pop(member.id, None)
    await ctx.send(f"✅ All warnings cleared for {member}")

# ---------- MODERATION ----------
@bot.command()
async def clear(ctx, amount: int):
    if not has_any_role(ctx, [
        ROLE_STAFF, ROLE_SENIOR_STAFF, ROLE_HEAD_STAFF,
        ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD,
        ROLE_FOUNDER, ROLE_COOWNER
    ]):
        return await ctx.send("❌ No permission.")

    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {len(deleted)-1} messages!", delete_after=5)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if not has_any_role(ctx, [ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kicked | {reason}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if not has_any_role(ctx, [ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned | {reason}")

@bot.command()
async def unban(ctx, user_id: int):
    if not has_any_role(ctx, [ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="No reason"):
    if not has_any_role(ctx, [
        ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER
    ]):
        return await ctx.send("❌ No permission.")
    await member.timeout(timedelta(minutes=minutes), reason=reason)
    await ctx.send(f"⏳ {member} timed out for {minutes} minutes | {reason}")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not has_any_role(ctx, [
        ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER
    ]):
        return await ctx.send("❌ No permission.")
    await member.timeout(None)
    await ctx.send(f"✅ Timeout removed for {member}")

# ---------- INVITE LEADERBOARD ----------
@bot.command()
async def nclinviteboard(ctx):
    guild = ctx.guild
    invite_data = {}
    for inv in await guild.invites():
        invite_data[inv.inviter] = invite_data.get(inv.inviter, 0) + inv.uses
    if not invite_data:
        return await ctx.send("No invites yet!")

    sorted_invites = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(
        title="📊 Top Inviters",
        description="Who brought the most members!",
        color=discord.Color.gold()
    )

    for i, (user, uses) in enumerate(sorted_invites[:10], start=1):
        embed.add_field(name=f"{i}. {user}", value=f"{uses} invite(s)", inline=False)

    await ctx.send(embed=embed)

# ---------- RUN ----------
bot.run(TOKEN)
