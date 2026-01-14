import discord
from discord.ext import commands
from datetime import timedelta
from collections import defaultdict
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
warnings = {}
guild_invites = {}  # {guild_id: {invite_code: uses}}
user_invites_count = defaultdict(lambda: defaultdict(int))  # {guild_id: {user_id: count}}

# ---------- UTIL ----------
def has_any_role(ctx, roles):
    return any(role.name in roles for role in ctx.author.roles)

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    for guild in bot.guilds:
        guild_invites[guild.id] = {invite.code: invite.uses for invite in await guild.invites()}
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower().strip()
    if content == "ncl":
        await message.channel.send(
            random.choice([
                "💀 You just typed `ncl` alone! Come on, try `ncl help` 😎",
                "🤨 Typing `ncl` alone won't summon me! Use `ncl help`!",
                "😏 Bro, `ncl` is not magic. Try `ncl help`!"
            ])
        )
    elif content.startswith("ncl help") and content != "ncl help":
        await message.channel.send(
            "😂 Close! But the correct is `ncl help` (no extra space at start or end)!"
        )

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    before = guild_invites.get(guild_id, {})
    after_invites = await member.guild.invites()

    used_invite = None
    for invite in after_invites:
        old_uses = before.get(invite.code, 0)
        if invite.uses > old_uses:
            used_invite = invite
            break

    guild_invites[guild_id] = {invite.code: invite.uses for invite in after_invites}

    if used_invite:
        inviter_id = used_invite.inviter.id
        user_invites_count[guild_id][inviter_id] += 1
        channel = member.guild.get_channel(INVITE_CHANNEL_ID)
        if channel:
            await channel.send(
                f"🎉 {member.mention} joined via {used_invite.inviter.mention}! "
                f"(Total invites: {user_invites_count[guild_id][inviter_id]})"
            )

@bot.event
async def on_member_update(before, after):
    if not before.premium_since and after.premium_since:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            await channel.send(
                f"🚀 THANK YOU {after.mention} FOR BOOSTING THE SERVER!"
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
nclslap @user → Slap someone
nclkiss @user → Kiss someone
nclhug @user → Hug someone
nclpat @user → Pat someone
nclship @user1 @user2 → Ship two users
nclmembers → Show total members
nclbeg → Beg for coins (funny)
ncljoke → Random joke
""",
        inline=False
    )

    embed.add_field(
        name="🛡️ Staff & Mod Commands",
        value="""
🛠️ Staff+:
• nclclear <amount> → Clear messages in channel

🧪 Trial Mod+:
• nclwarn @user reason → Warn a user
• nclwarnings @user → Show warnings
• nclunwarn @user → Remove warnings
• ncltimeout @user minutes → Timeout user
• ncluntimeout @user → Remove timeout

👑 Head Moderator+:
• nclkick @user → Kick user
• nclban @user → Ban user
• nclunban user_id → Unban user
""",
        inline=False
    )

    embed.add_field(
        name="📊 Invite Commands",
        value="""
nclinviteboard → Show top inviters
nclinvites @user → Show how many people a specific user invited
""",
        inline=False
    )

    embed.add_field(
        name="👑 Founder / Co-Owner",
        value="Access to all commands above",
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

@bot.command()
async def beg(ctx):
    coins = random.randint(1, 100)
    await ctx.send(f"🙏 {ctx.author.mention} begged and got **{coins} coins**!")

@bot.command()
async def joke(ctx):
    jokes = [
        "Why did Discord break up? Too many servers 😭",
        "Mods don’t sleep, they just timeout 😈",
        "ncl > all prefixes 😎",
        "Why don’t skeletons fight each other? They don’t have the guts 😅",
        "I told my computer I needed a break, and it said 'No problem, I'll go to sleep!' 😴"
    ]
    await ctx.send(random.choice(jokes))

# ---------- WARN SYSTEM ----------
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not has_any_role(ctx, [ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ You cannot warn members.")
    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned.\nReason: {reason}")

@bot.command()
async def warnings(ctx, member: discord.Member):
    user_warnings = warnings.get(member.id, [])
    if not user_warnings:
        return await ctx.send(f"✅ {member.mention} has no warnings.")
    text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(user_warnings))
    await ctx.send(f"⚠️ **Warnings for {member}:**\n{text}")

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if not has_any_role(ctx, [ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    warnings.pop(member.id, None)
    await ctx.send(f"✅ All warnings cleared for {member}")

# ---------- MODERATION ----------
@bot.command()
async def clear(ctx, amount: int):
    if not has_any_role(ctx, [ROLE_STAFF, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=5)

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
    if not has_any_role(ctx, [ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    await member.timeout(timedelta(minutes=minutes), reason=reason)
    await ctx.send(f"⏳ {member} timed out for {minutes} minutes | {reason}")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not has_any_role(ctx, [ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    await member.timeout(None)
    await ctx.send(f"✅ Timeout removed for {member}")

# ---------- INVITE COMMANDS ----------
@bot.command()
async def nclinviteboard(ctx):
    guild_id = ctx.guild.id
    if not user_invites_count[guild_id]:
        return await ctx.send("📊 No invites tracked yet.")
    sorted_invites = sorted(user_invites_count[guild_id].items(), key=lambda x: x[1], reverse=True)
    text = "\n".join(f"**{ctx.guild.get_member(uid)}** → {count} invite(s)" for uid, count in sorted_invites[:10])
    await ctx.send(f"📊 **Top Inviters:**\n{text}")

@bot.command()
async def nclinvites(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    count = user_invites_count[guild_id].get(member.id, 0)
    await ctx.send(f"👤 {member.mention} has invited **{count}** member(s).")

# ---------- RUN ----------
bot.run(TOKEN)
