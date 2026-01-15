import discord
from discord.ext import commands
from datetime import timedelta
import os
import random

# ================= CONFIG =================
PREFIX = "ncl"

# ================= INTENTS =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ================= STORAGE =================
user_warnings = {}
user_points = {}
invite_cache = {}

# ================= UTIL =================
def get_points(uid):
    return user_points.get(uid, 0)

def add_points(uid, amt):
    user_points[uid] = get_points(uid) + amt

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    for g in bot.guilds:
        invites = await g.invites()
        invite_cache[g.id] = {i.code: i.uses for i in invites}

@bot.event
async def on_member_join(member):
    invites = await member.guild.invites()
    old = invite_cache.get(member.guild.id, {})
    for i in invites:
        if i.code in old and i.uses > old[i.code]:
            add_points(i.inviter.id, 10)
            break
    invite_cache[member.guild.id] = {i.code: i.uses for i in invites}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower().strip() == "ncl":
        await message.channel.send(
            random.choice([
                "🤨 You typed `ncl` and vanished?",
                "😭 Bro finish the command… try `nclhelp`",
                "💀 That’s not how commands work, chief"
            ])
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
        name="🎉 Fun & Social",
        value=(
            "`nclslap @user`\n"
            "`nclkiss @user`\n"
            "`nclhug @user`\n"
            "`nclpat @user`\n"
            "`nclship @u1 @u2`\n"
            "`ncljoke [@user]`\n"
            "`nclbeg`\n"
            "`nclroast @user`"
        ),
        inline=False
    )

    embed.add_field(
        name="📩 Profile & Invites",
        value=(
            "`nclprofile [@user]`\n"
            "`nclinvites [@user]`\n"
            "`nclinviteboard`"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Moderation",
        value=(
            "`nclclear <amount>`\n"
            "`nclwarn @user <reason>`\n"
            "`nclwarnings @user`\n"
            "`nclunwarn @user`\n"
            "`nclkick @user`\n"
            "`nclban @user`\n"
            "`ncltimeout @user <minutes>`"
        ),
        inline=False
    )

    embed.set_footer(text="Use wisely… or hilariously 😏")
    await ctx.send(embed=embed)

# ================= FUN =================
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
async def ship(ctx, u1: discord.Member, u2: discord.Member):
    await ctx.send(f"❤️ {u1.mention} × {u2.mention} — SHIPPED")

@bot.command()
async def beg(ctx):
    if random.randint(1, 3) == 1:
        add_points(ctx.author.id, 5)
        await ctx.send("🍀 You begged and got **5 points**!")
    else:
        await ctx.send("💀 You begged… and got nothing")

@bot.command()
async def joke(ctx, member: discord.Member = None):
    jokes = [
        "This server runs on chaos 💀",
        "Mods don’t sleep, they timeout 😭",
        "Skill issue detected 🤡"
    ]
    if member:
        jokes.append(f"{member.mention} lagged IRL 💀")
    await ctx.send(random.choice(jokes))

@bot.command()
async def roast(ctx, member: discord.Member):
    await ctx.send(f"🔥 {member.mention}, even your Wi-Fi left you")

# ================= PROFILE =================
@bot.command()
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(
        title=f"📊 Profile — {member}",
        color=discord.Color.gold()
    )
    embed.add_field(name="💰 Points", value=get_points(member.id))
    embed.add_field(name="📩 Invites", value=get_points(member.id) // 10)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def invites(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(
        f"📩 {member.mention} has **{get_points(member.id)//10} invites**"
    )

@bot.command()
async def inviteboard(ctx):
    if not user_points:
        return await ctx.send("😴 No invites yet")
    top = sorted(user_points.items(), key=lambda x: x[1], reverse=True)[:5]
    text = ""
    for i, (uid, pts) in enumerate(top, 1):
        user = await bot.fetch_user(uid)
        text += f"{i}. **{user}** — {pts//10} invites\n"
    await ctx.send("🏆 **Invite Leaderboard**\n" + text)

# ================= MODERATION =================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    user_warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned: {reason}")

@bot.command()
async def warnings(ctx, member: discord.Member):
    ws = user_warnings.get(member.id, [])
    if not ws:
        return await ctx.send("✅ No warnings")
    await ctx.send("\n".join(ws))

@bot.command()
@commands.has_permissions(kick_members=True)
async def unwarn(ctx, member: discord.Member):
    user_warnings.pop(member.id, None)
    await ctx.send("✅ Warnings cleared")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send("👢 Member kicked")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send("🔨 Member banned")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int):
    await member.timeout(timedelta(minutes=minutes))
    await ctx.send("⏳ Timed out")

# ================= RUN =================
bot.run(os.getenv("TOKEN"))
