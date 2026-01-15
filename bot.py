import discord
from discord.ext import commands
import random
import datetime
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="ncl", intents=intents, help_command=None)

# ---------------- DATA STORAGE ----------------
users = {}
warnings = {}
invites = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "coins": 0,
            "daily": None
        }
    return users[uid]

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower().strip() in ["ncl", "ncl help"]:
        await message.channel.send(
            random.choice([
                "😵 Oops! Try **nclhelp** not just staring at me",
                "🤡 Almost there! Use **nclhelp**",
                "🧠 Brain.exe stopped? Type **nclhelp**",
                "😂 You forgot the magic word: **nclhelp**"
            ])
        )
    await bot.process_commands(message)

# ---------------- HELP ----------------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🚀 NCL BOT COMMAND GUIDE",
        description="Prefix: **ncl**",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎉 Fun & Social",
        value=
        "`nclslap @user` 👋\n"
        "`nclkiss @user` 💋\n"
        "`nclhug @user` 🤗\n"
        "`nclpat @user` ✨\n"
        "`nclship @u1 @u2` ❤️\n"
        "`ncljoke [@user]` 😂\n"
        "`nclbeg` 🍀",
        inline=False
    )

    embed.add_field(
        name="📊 Profile & Invites",
        value=
        "`nclprofile [@user]` 📊\n"
        "`ncldaily` 💸\n"
        "`nclinvites [@user]` 📩\n"
        "`nclinviteboard` 🏆",
        inline=False
    )

    embed.add_field(
        name="🛡️ Moderation",
        value=
        "`nclclear <amount>` 🧹\n"
        "`nclwarn @user <reason>` ⚠️\n"
        "`nclwarnings @user` 📝\n"
        "`nclunwarn @user` ✅\n"
        "`nclkick @user` 👢\n"
        "`nclban @user <reason>` 🔨",
        inline=False
    )

    embed.set_footer(text="Use wisely… or hilariously 😏")
    await ctx.send(embed=embed)

# ---------------- FUN ----------------
@bot.command()
async def beg(ctx):
    user = get_user(ctx.author.id)
    if random.choice([True, False]):
        user["coins"] += 5
        await ctx.send("🥺 You begged… and got **5 coins**! Lucky day 🍀")
    else:
        await ctx.send("💀 You begged… but got nothing. NPC moment.")

@bot.command()
async def joke(ctx, member: discord.Member = None):
    jokes = [
        "has 2 brain cells and both are fighting 🧠⚔️",
        "is running on Windows XP 🖥️",
        "forgot how to breathe for a second 💀",
        "makes bugs feel intelligent 🐛"
    ]
    if member:
        await ctx.send(f"😂 {member.mention} {random.choice(jokes)}")
    else:
        await ctx.send(random.choice(jokes))

@bot.command()
async def slap(ctx, member: discord.Member):
    await ctx.send(f"👋 {ctx.author.mention} slapped {member.mention}")

@bot.command()
async def hug(ctx, member: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention} hugged {member.mention}")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention} kissed {member.mention}")

@bot.command()
async def pat(ctx, member: discord.Member):
    await ctx.send(f"✨ {ctx.author.mention} patted {member.mention}")

@bot.command()
async def ship(ctx, u1: discord.Member, u2: discord.Member):
    await ctx.send(f"❤️ Shipping **{u1.name} x {u2.name}** 💍")

# ---------------- PROFILE ----------------
@bot.command()
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = get_user(member.id)

    embed = discord.Embed(
        title=f"📊 {member.name}'s Profile",
        color=discord.Color.purple()
    )
    embed.add_field(name="💰 Coins", value=user["coins"])
    embed.add_field(name="📩 Invites", value=invites.get(member.id, 0))
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    await ctx.send(embed=embed)

# ---------------- DAILY ----------------
@bot.command()
async def daily(ctx):
    user = get_user(ctx.author.id)
    now = datetime.datetime.utcnow()

    if user["daily"] and (now - user["daily"]).seconds < 86400:
        await ctx.send("⏳ You already claimed daily. Come back later!")
        return

    user["daily"] = now
    user["coins"] += 20
    await ctx.send("💸 Daily claimed! You got **20 coins**")

# ---------------- INVITES ----------------
@bot.command()
async def invites_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    count = invites.get(member.id, 0)
    msg = f"📩 {member.name} has **{count} invites**"
    if count == 0:
        msg += " 💀 touch grass?"
    await ctx.send(msg)

@bot.command()
async def inviteboard(ctx):
    if not invites:
        await ctx.send("🏆 No invites yet!")
        return

    sorted_inv = sorted(invites.items(), key=lambda x: x[1], reverse=True)
    text = ""
    for i, (uid, count) in enumerate(sorted_inv[:5], start=1):
        user = await bot.fetch_user(uid)
        text += f"**{i}. {user.name}** — {count} invites\n"

    embed = discord.Embed(title="🏆 Invite Leaderboard", description=text)
    await ctx.send(embed=embed)

# ---------------- MODERATION ----------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send("🧹 Messages cleared!", delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"👢 {member} kicked")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned")

# ---------------- RUN ----------------
bot.run(os.getenv("TOKEN"))
