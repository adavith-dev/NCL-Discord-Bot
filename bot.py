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

# ---------- ROLES ----------
FOUNDER_ROLES = ["★Founder★", "★ CO-OWNER ★"]
MOD_ROLES = FOUNDER_ROLES + ["👑 Head Moderator", "🛡️ Moderator", "🧪 Trial Mod", "👑 Head Staff", "⭐ Senior Staff", "🛠️ Staff"]

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------- DATA ----------
invites = {}
user_invites_count = {}
warnings = {}

# ---------- HELPER ----------
def has_any_role(ctx, roles):
    return any(role.name in roles for role in ctx.author.roles)

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    for guild in bot.guilds:
        invites[guild.id] = await guild.invites()
        user_invites_count[guild.id] = {}
        for invite in invites[guild.id]:
            user_invites_count[guild.id][invite.inviter.id] = invite.uses
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    before = invites.get(member.guild.id, [])
    after = await member.guild.invites()
    for invite in after:
        old = next((i for i in before if i.code == invite.code), None)
        if old and invite.uses > old.uses:
            channel = member.guild.get_channel(INVITE_CHANNEL_ID)
            if channel:
                await channel.send(f"🎉 {member.mention} joined using **{invite.inviter}**'s invite!")
            user_invites_count[member.guild.id][invite.inviter.id] = user_invites_count[member.guild.id].get(invite.inviter.id, 0) + 1
    invites[member.guild.id] = after

@bot.event
async def on_member_update(before, after):
    if not before.premium_since and after.premium_since:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            await channel.send(f"🚀 **THANK YOU {after.mention} FOR BOOSTING THE SERVER!**")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content.lower().strip()
    if content == "ncl" or content.startswith("ncl "):
        fun_responses = [
            "💀 Bro you forgot the command! Try `ncl help`",
            "😂 Oops! `ncl` needs a command buddy!",
            "🤨 Did you mean `ncl help`? 😅",
            "😎 `ncl` alone? You need friends… like commands!"
        ]
        await message.channel.send(random.choice(fun_responses))
    await bot.process_commands(message)

# ---------- HELP ----------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 NCL BOT COMMANDS",
        description=f"Prefix: **{PREFIX}**",
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
ncljoke
nclping
nclinvites @user
nclinviteboard
""",
        inline=False
    )
    embed.add_field(
        name="🛡️ Staff Commands",
        value="""
nclclear <amount>
nclwarn @user reason
nclwarnings @user
nclunwarn @user
ncltimeout @user minutes
ncluntimeout @user
nclkick @user
nclban @user reason
nclunban user_id
""",
        inline=False
    )
    embed.add_field(name="👑 Founder / Co-Owner", value="All commands + undo any last action", inline=False)
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
async def joke(ctx):
    jokes = [
        "Why did Discord break up? Too many servers 😭",
        "Mods don’t sleep, they just timeout 😈",
        "ncl > all prefixes 😎",
        "Why did the chicken join Discord? To get to the other server!",
        "I would tell you a UDP joke, but you might not get it...",
        "Why do programmers prefer dark mode? Because light attracts bugs!"
    ]
    await ctx.send(random.choice(jokes))

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency*1000)}ms`")

@bot.command()
async def members(ctx):
    await ctx.send(f"👥 Total members: **{ctx.guild.member_count}**")

# ---------- INVITE SYSTEM ----------
@bot.command()
async def nclinvites(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    count = user_invites_count[guild_id].get(member.id, 0)
    if count == 0:
        funny_comments = [
            f"😂 {member.mention} hasn’t invited anyone yet. Time to start hustling!",
            f"😢 {member.mention}, zero invites? Even my cat has more friends!",
            f"🤨 {member.mention}, no invites… are you even trying?",
            f"💀 {member.mention} has 0 invites. Come on, you can do better!"
        ]
        await ctx.send(random.choice(funny_comments))
    elif count <= 5:
        await ctx.send(f"👍 {member.mention} has **{count}** invite(s). Not bad, keep going!")
    elif count <= 10:
        await ctx.send(f"🔥 {member.mention} has **{count}** invites! You’re a pro inviter!")
    else:
        await ctx.send(f"💎 {member.mention} has **{count}** invites! Invite king/queen!")

@bot.command()
async def nclinviteboard(ctx):
    guild_id = ctx.guild.id
    leaderboard = sorted(user_invites_count[guild_id].items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(
        title="📊 Invite Leaderboard",
        color=discord.Color.gold()
    )
    if not leaderboard:
        embed.description = "No invites yet!"
    else:
        text = ""
        for i, (user_id, count) in enumerate(leaderboard[:10], 1):
            member = ctx.guild.get_member(user_id)
            if member:
                text += f"**{i}. {member.display_name}** — {count} invite(s)\n"
        embed.description = text
    await ctx.send(embed=embed)

# ---------- WARN SYSTEM ----------
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not has_any_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned. Reason: **{reason}**")

@bot.command()
async def warnings(ctx, member: discord.Member):
    user_warnings = warnings.get(member.id, [])
    if not user_warnings:
        return await ctx.send(f"✅ {member.mention} has no warnings.")
    text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(user_warnings))
    await ctx.send(f"⚠️ **Warnings for {member}:**\n{text}")

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if not has_any_role(ctx, FOUNDER_ROLES + ["👑 Head Moderator"]):
        return await ctx.send("❌ No permission.")
    warnings.pop(member.id, None)
    await ctx.send(f"✅ All warnings cleared for {member}")

# ---------- MODERATION ----------
@bot.command()
async def clear(ctx, amount: int):
    if not has_any_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=5)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if not has_any_role(ctx, FOUNDER_ROLES + ["👑 Head Moderator"]):
        return await ctx.send("❌ No permission.")
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kicked | {reason}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if not has_any_role(ctx, FOUNDER_ROLES + ["👑 Head Moderator"]):
        return await ctx.send("❌ No permission.")
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned | {reason}")

@bot.command()
async def unban(ctx, user_id: int):
    if not has_any_role(ctx, FOUNDER_ROLES + ["👑 Head Moderator"]):
        return await ctx.send("❌ No permission.")
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    if not has_any_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"⏳ {member} timed out for {minutes} minutes")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not has_any_role(ctx, MOD_ROLES):
        return await ctx.send("❌ No permission.")
    await member.timeout(None)
    await ctx.send(f"✅ Timeout removed for {member}")

# ---------- RUN ----------
bot.run(TOKEN)
