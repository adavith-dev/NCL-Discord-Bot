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

# ---------- ROLE IDS ----------
OWNER_ID = 1457168593123803222
COOWNER_ID = 1457168593123803221

ROLE_SENIOR_MOD = 1458041286006276267
ROLE_HEAD_MOD = 1458041286006276267
ROLE_MOD = 1458040204781948938
ROLE_TRIAL_MOD = 1458040060472459488

ROLE_HEAD_STAFF = 1458041729486950543
ROLE_SENIOR_STAFF = 1458041716123766850
ROLE_STAFF = 1458041490809950381
ROLE_TRIAL_STAFF = 1458041443107995881

MOD_ROLES = {
    ROLE_SENIOR_MOD,
    ROLE_HEAD_MOD,
    ROLE_MOD,
    ROLE_TRIAL_MOD
}

STAFF_ROLES = {
    ROLE_HEAD_STAFF,
    ROLE_SENIOR_STAFF,
    ROLE_STAFF,
    ROLE_TRIAL_STAFF
}

# ---------- INTENTS ----------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------- DATA ----------
invites = {}
warnings = {}

# ---------- PERMISSION CHECK ----------
def is_owner(ctx):
    return ctx.author.id in (OWNER_ID, COOWNER_ID)

def has_role(ctx, role_set):
    return any(role.id in role_set for role in ctx.author.roles)

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    for g in bot.guilds:
        invites[g.id] = await g.invites()
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower().strip() == "ncl":
        await message.channel.send(
            "🤡 You typed **ncl** and stopped.\n"
            "Bro finish the sentence 💀\n"
            "Try `ncl help`"
        )

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    before = invites.get(member.guild.id, [])
    after = await member.guild.invites()

    for inv in after:
        old = next((i for i in before if i.code == inv.code), None)
        if old and inv.uses > old.uses:
            ch = member.guild.get_channel(INVITE_CHANNEL_ID)
            if ch:
                await ch.send(
                    f"🎉 {member.mention} joined using **{inv.inviter.mention}**'s invite!"
                )
    invites[member.guild.id] = after

@bot.event
async def on_member_update(before, after):
    if not before.premium_since and after.premium_since:
        ch = after.guild.get_channel(BOOST_CHANNEL_ID)
        if ch:
            await ch.send(
                f"🚀 **{after.mention} JUST BOOSTED THE SERVER!**\n"
                "Absolute legend 💎"
            )

# ---------- HELP ----------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 NCL BOT COMMANDS",
        description="Prefix: **ncl**",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🎉 Member Commands",
        value="""
`ncl slap @user`
`ncl kiss @user`
`ncl hug @user`
`ncl joke [@user]`
`ncl members`
""",
        inline=False
    )

    embed.add_field(
        name="🛡️ Staff / Mod",
        value="""
`ncl warn @user <reason>`
`ncl warnings @user`
`ncl unwarn @user`
`ncl timeout @user <min>`
`ncl untimeout @user`
`ncl clear <amount>`
`ncl kick @user`
`ncl ban @user`
`ncl unban <id>`
""",
        inline=False
    )

    embed.add_field(
        name="👑 Owner / Co-owner",
        value="Full access to everything",
        inline=False
    )

    await ctx.send(embed=embed)

# ---------- FUN ----------
@bot.command()
async def slap(ctx, member: discord.Member):
    await ctx.send(f"👋 {ctx.author.mention} slapped {member.mention} HARD 😭")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention} kissed {member.mention} 😳")

@bot.command()
async def hug(ctx, member: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention} hugged {member.mention}")

@bot.command()
async def joke(ctx, member: discord.Member = None):
    general = [
        "I tried to be productive… Discord said no 💀",
        "Why do mods love timeout? Power trip 😈",
        "This server runs on chaos and ping"
    ]

    roasts = [
        "{u} built like a typo",
        "{u} types faster than they think",
        "{u} got brain lag but internet speed 💀",
        "{u} thinks they're scary but uses light mode"
    ]

    if member:
        await ctx.send(random.choice(roasts).format(u=member.mention))
    else:
        await ctx.send(random.choice(general))

@bot.command()
async def members(ctx):
    await ctx.send(f"👥 Total members: **{ctx.guild.member_count}**")

# ---------- WARN SYSTEM ----------
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not (is_owner(ctx) or has_role(ctx, MOD_ROLES)):
        return await ctx.send("❌ No permission.")
    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned\nReason: **{reason}**")

@bot.command()
async def warnings(ctx, member: discord.Member):
    ws = warnings.get(member.id, [])
    if not ws:
        return await ctx.send("✅ No warnings.")
    await ctx.send("\n".join(f"{i+1}. {w}" for i, w in enumerate(ws)))

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if not (is_owner(ctx) or has_role(ctx, {ROLE_HEAD_MOD, ROLE_SENIOR_MOD})):
        return await ctx.send("❌ No permission.")
    warnings.pop(member.id, None)
    await ctx.send("✅ Warnings cleared")

# ---------- MODERATION ----------
@bot.command()
async def clear(ctx, amount: int):
    if not (is_owner(ctx) or has_role(ctx, STAFF_ROLES | MOD_ROLES)):
        return await ctx.send("❌ No permission.")
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=4)

@bot.command()
async def kick(ctx, member: discord.Member):
    if not (is_owner(ctx) or has_role(ctx, {ROLE_HEAD_MOD, ROLE_SENIOR_MOD})):
        return await ctx.send("❌ No permission.")
    await member.kick()
    await ctx.send(f"👢 {member} kicked")

@bot.command()
async def ban(ctx, member: discord.Member):
    if not (is_owner(ctx) or has_role(ctx, {ROLE_HEAD_MOD, ROLE_SENIOR_MOD})):
        return await ctx.send("❌ No permission.")
    await member.ban()
    await ctx.send(f"🔨 {member} banned")

@bot.command()
async def unban(ctx, user_id: int):
    if not is_owner(ctx):
        return await ctx.send("❌ Owner only.")
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    if not (is_owner(ctx) or has_role(ctx, MOD_ROLES)):
        return await ctx.send("❌ No permission.")
    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"⏳ {member} timed out")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not (is_owner(ctx) or has_role(ctx, MOD_ROLES)):
        return await ctx.send("❌ No permission.")
    await member.timeout(None)
    await ctx.send("✅ Timeout removed")

# ---------- RUN ----------
bot.run(TOKEN)
