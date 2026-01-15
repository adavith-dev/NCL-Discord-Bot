import discord
from discord.ext import commands
import random
import datetime
import os

# ================= SETUP =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="ncl", intents=intents, help_command=None)

# ================= DATA =================
users = {}
warnings = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {"coins": 0, "daily": None}
    return users[uid]

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.lower().strip() in ["ncl", "ncl help"]:
        await message.channel.send("🤡 Use **nclhelp** properly bro")
    await bot.process_commands(message)

# ================= HELP =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🚀 NCL BOT — Command Guide",
        description=(
            "**Prefix:** `ncl`\n\n"
            "NCL Bot is packed with fun, economy, profile, and moderation features.\n"
            "Here’s everything you can use 👇"
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎉 Fun & Social Commands",
        value=(
            "`nclslap @user` 👋 — Slap someone for fun\n"
            "`nclkiss @user` 💋 — Send a kiss\n"
            "`nclhug @user` 🤗 — Hug a member\n"
            "`nclpat @user` ✨ — Pat someone\n"
            "`nclship @user1 @user2` ❤️ — Ship two users\n"
            "`ncljoke [@user]` 😂 — Random joke or roast\n"
            "`nclbeg` 🍀 — Beg for coins (5 coins or nothing)"
        ),
        inline=False
    )

    embed.add_field(
        name="📊 Profile & Economy",
        value=(
            "`nclprofile [@user]` 📊 — View profile stats\n"
            "`ncldaily` 💸 — Claim daily coins (once every 24h)"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Moderation Commands",
        value=(
            "`nclclear <amount>` 🧹 — Delete messages\n"
            "`nclwarn @user <reason>` ⚠️ — Warn a member\n"
            "`nclwarnings @user` 📝 — View warnings\n"
            "`nclunwarn @user` ✅ — Clear all warnings\n"
            "`nclmute @user <minutes>` 🔇 — Timeout a member\n"
            "`nclunmute @user` 🔊 — Remove timeout\n"
            "`nclkick @user` 👢 — Kick a member\n"
            "`nclban @user <reason>` 🔨 — Ban a member\n"
            "`nclunban <user_id>` 🎉 — Unban using user ID"
        ),
        inline=False
    )

    embed.add_field(
        name="👑 Founder / Co-Owner",
        value="Full access to all commands — the real bosses 💎",
        inline=False
    )

    embed.set_footer(text="💡 Tip: Use commands wisely… or hilariously 😏")
    await ctx.send(embed=embed)

# ================= FUN =================
@bot.command()
async def beg(ctx):
    user = get_user(ctx.author.id)
    if random.choice([True, False]):
        user["coins"] += 5
        await ctx.send("🍀 You got **5 coins**!")
    else:
        await ctx.send("💀 You got nothing.")

@bot.command()
async def joke(ctx, member: discord.Member = None):
    jokes = ["has skill issues 🤡", "runs on 2 brain cells 💀", "forgot how to think 🧠"]
    if member:
        await ctx.send(f"{member.mention} {random.choice(jokes)}")
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
    await ctx.send(f"❤️ {u1.name} x {u2.name}")

# ================= PROFILE =================
@bot.command()
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = get_user(member.id)
    embed = discord.Embed(title=f"{member.name}'s Profile", color=discord.Color.purple())
    embed.add_field(name="💰 Coins", value=user["coins"])
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    await ctx.send(embed=embed)

# ================= DAILY =================
@bot.command()
async def daily(ctx):
    user = get_user(ctx.author.id)
    now = datetime.datetime.utcnow()
    if user["daily"] and (now - user["daily"]).seconds < 86400:
        await ctx.send("⏳ Daily already claimed.")
        return
    user["daily"] = now
    user["coins"] += 20
    await ctx.send("💸 You got **20 coins**!")

# ================= WARN SYSTEM =================
@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned: **{reason}**")

@bot.command()
async def warnings(ctx, member: discord.Member):
    w = warnings.get(member.id, [])
    if not w:
        await ctx.send("✅ No warnings.")
    else:
        await ctx.send("\n".join(w))

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unwarn(ctx, member: discord.Member):
    warnings.pop(member.id, None)
    await ctx.send("✅ Warnings cleared.")

# ================= MODERATION =================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send("🧹 Cleared.", delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send("👢 User kicked.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send("🔨 User banned.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send("🎉 User unbanned.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int):
    await member.timeout(datetime.timedelta(minutes=minutes))
    await ctx.send("🔇 User muted.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send("🔊 User unmuted.")

# ================= RUN =================
bot.run(os.getenv("TOKEN"))
