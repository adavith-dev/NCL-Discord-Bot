import discord
from discord.ext import commands
from datetime import timedelta
import os
import random
import asyncio

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

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------- DATA ----------
invites = {}
warnings = {}

# ---------- UTILS ----------
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

    msg = message.content.lower().strip()
    if msg == "ncl" or msg.startswith("ncl help"):
        fun_responses = [
            "😂 Brooo… you forgot the rest, try `nclhelp`",
            "💀 Oops! Missing command? Use `nclhelp` before I vanish!",
            "😎 Hey, you need help? Type `nclhelp` for magic!"
        ]
        await message.channel.send(random.choice(fun_responses))

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
                    f"🎉 {member.mention} joined using **{invite.inviter}**'s invite!"
                )
    invites[member.guild.id] = after

@bot.event
async def on_member_update(before, after):
    if not before.premium_since and after.premium_since:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            await channel.send(f"🚀 **THANK YOU {after.mention} FOR BOOSTING THE SERVER!**")

# ---------- HELP ----------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📚 Welcome to **NCL BOT Help Center**!",
        description="Here’s a guide to all the awesome commands you can use!\nPrefix: **ncl**",
        color=discord.Color.purple()
    )

    # FUN / MEMBER COMMANDS
    embed.add_field(
        name="🎉 Fun & Social Commands",
        value="""
**nclslap @user** — Slap someone 👋  
**nclkiss @user** — Send a smooch 💋  
**nclhug @user** — Hug your friends 🤗  
**nclpat @user** — Pat someone ✨  
**nclship @user1 @user2** — Ship two people ❤️  
**nclmembers** — Check total members 👥  
**ncljoke [@user]** — Get a random joke or roast a friend 😎  
**nclbeg** — Beg for fun (luck might strike!) 🍀
""",
        inline=False
    )

    # STAFF / MOD COMMANDS
    embed.add_field(
        name="🛡️ Staff & Moderator Commands",
        value="""
**nclclear <amount>** — Clears messages 🧹  
**nclwarn @user <reason>** — Warn a user ⚠️  
**nclwarnings @user** — See all warnings 📝  
**nclunwarn @user** — Remove all warnings ✅  
**ncltimeout @user <minutes>** — Timeout a user ⏳  
**ncluntimeout @user** — Remove timeout ⏱️  
**nclkick @user** — Kick a member 👢  
**nclban @user <reason>** — Ban a member 🔨  
**nclunban <user_id>** — Unban someone 🎉
""",
        inline=False
    )

    # INVITE / LEADERBOARD COMMANDS
    embed.add_field(
        name="📈 Invite & Leaderboard Commands",
        value="""
**nclinvites @user** — Check how many people a user has invited 👫  
**nclinviteboard** — See the top inviters leaderboard 🏆  
*Note:* Funny comments appear if someone has 0 invites 😜
""",
        inline=False
    )

    # FOUNDER / CO-OWNER
    embed.add_field(
        name="👑 Founder / Co-Owner",
        value="Has access to **all commands**, basically the boss 💎",
        inline=False
    )

    embed.set_footer(
        text="💡 Tip: Use commands wisely… or hilariously! 😏",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )

    await ctx.send(embed=embed)

# ---------- FUN COMMANDS ----------
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
async def joke(ctx, member: discord.Member = None):
    jokes = [
        "Why did Discord break up? Too many servers 😭",
        "Mods don’t sleep, they just timeout 😈",
        "ncl > all prefixes 😎",
        "I told my PC I needed a break… it froze 🖥️",
        "Why do programmers prefer dark mode? Because light attracts bugs 🐛"
    ]
    if member:
        jokes.append(f"{member.mention}, did you forget to code today? 🤣")
    await ctx.send(random.choice(jokes))

@bot.command()
async def beg(ctx):
    messages = [
        "Begging doesn’t work here… or does it? 😜",
        "You begged so hard, even the bot felt sorry 😏",
        "Coins? Likes? A hug? Begging intensifies… 💀"
    ]
    await ctx.send(random.choice(messages))

# ---------- WARN SYSTEM ----------
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not has_any_role(ctx, [ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
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
    if not has_any_role(ctx, [ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    warnings.pop(member.id, None)
    await ctx.send(f"✅ All warnings cleared for {member}")

# ---------- MODERATION ----------
@bot.command()
async def clear(ctx, amount: int):
    if not has_any_role(ctx, [ROLE_STAFF, ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
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
async def timeout(ctx, member: discord.Member, minutes: int):
    if not has_any_role(ctx, [ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"⏳ {member} timed out for {minutes} minutes")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not has_any_role(ctx, [ROLE_TRIAL_MOD, ROLE_MOD, ROLE_HEAD_MOD, ROLE_FOUNDER, ROLE_COOWNER]):
        return await ctx.send("❌ No permission.")
    await member.timeout(None)
    await ctx.send(f"✅ Timeout removed for {member}")

# ---------- INVITE / LEADERBOARD ----------
@bot.command()
async def nclinvites(ctx, member: discord.Member = None):
    member = member or ctx.author
    guild_invites = await ctx.guild.invites()
    total = sum(i.uses for i in guild_invites if i.inviter == member)
    funny_comment = {
        0: "😢 No invites… maybe next time!",
        1: "🙂 Just started, keep going!",
        2: "😎 Getting there, keep inviting!",
        3: "🔥 Wow, 3 invites already!",
        4: "🚀 4 invites, you’re on fire!",
        5: "💎 5 invites, legend!"
    }
    await ctx.send(f"👥 {member.mention} has **{total} invites**! {funny_comment.get(total, '💪 Keep going!')}")

@bot.command()
async def nclinviteboard(ctx):
    guild_invites = await ctx.guild.invites()
    leaderboard = {}
    for inv in guild_invites:
        leaderboard[inv.inviter] = leaderboard.get(inv.inviter, 0) + inv.uses
    top = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:10]
    if not top:
        return await ctx.send("No invites yet 😭")
    text = "\n".join(f"{i+1}. {u.mention} — {c} invites" for i, (u, c) in enumerate(top))
    await ctx.send(f"🏆 **Top Inviters Leaderboard**:\n{text}")

# ---------- RUN ----------
bot.run(TOKEN)
