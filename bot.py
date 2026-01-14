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
SENIOR_MOD_ID = 1458041286006276267
HEAD_MOD_ID = 1458041286006276267
MOD_ID = 1458040204781948938
TRIAL_MOD_ID = 1458040060472459488

# ================= POWER LEVELS =================
ROLE_POWER = {
    FOUNDER_ID: 100,
    COOWNER_ID: 100,
    SENIOR_MOD_ID: 90,
    HEAD_MOD_ID: 80,
    MOD_ID: 60,
    TRIAL_MOD_ID: 40
}

def get_power(member: discord.Member):
    return max((ROLE_POWER.get(r.id, 0) for r in member.roles), default=0)

def is_boss(member: discord.Member):
    return get_power(member) >= 100

# ================= INTENTS =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

warnings = {}

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.lower().strip() == "ncl":
        await message.channel.send(
            "😂 Bro just typed `ncl` and vanished...\n"
            "Use `nclhelp` properly next time 💀"
        )
    await bot.process_commands(message)

# ================= HELP =================
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="📚 NCL BOT – Help Center",
        description="Here’s a guide to all the awesome commands you can use!\nPrefix: **ncl**",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🎉 Fun & Social Commands",
        value="""
nclslap @user  
nclkiss @user  
nclhug @user  
nclpat @user  
nclship @user1 @user2  
nclmembers  
ncljoke [@user]  
nclbeg
""",
        inline=False
    )

    embed.add_field(
        name="🛡️ Staff & Moderator Commands",
        value="""
nclclear <amount>  
nclwarn @user <reason>  
nclwarnings @user  
nclunwarn @user  
ncltimeout @user <minutes>  
ncluntimeout @user  
nclkick @user  
nclban @user <reason>  
nclunban <user_id>
""",
        inline=False
    )

    embed.add_field(
        name="👑 Founder / Co-Owner",
        value="Has access to **ALL commands**. Basically the boss 😎",
        inline=False
    )

    embed.set_footer(text="💡 Use commands wisely… or hilariously!")
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
    await ctx.send(f"❤️ {u1.mention} x {u2.mention} — **SHIPPED**")

@bot.command()
async def beg(ctx):
    await ctx.send(random.choice([
        "Begging detected… dignity not found 💀",
        "You begged so hard the bot felt bad 😭",
        "Begging won’t help… or will it? 😏"
    ]))

@bot.command()
async def joke(ctx, member: discord.Member = None):
    cooked = [
        "This server is more cooked than my sleep schedule 💀",
        "Mods don’t sleep, they just timeout 😈",
        "Discord runs better than my life 😭",
        "Light mode users scare me 👁️"
    ]
    if member:
        cooked += [
            f"{member.mention} lagged so hard even Discord gave up 💀",
            f"{member.mention} got cooked, fried, and served 🍗",
            f"{member.mention} tried to escape the roast but failed 🤡"
        ]
    await ctx.send(random.choice(cooked))

@bot.command()
async def members(ctx):
    await ctx.send(f"👥 Total members: **{ctx.guild.member_count}**")

# ================= WARN =================
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not is_boss(ctx.author):
        if get_power(ctx.author) < 40:
            return await ctx.send("❌ You cannot warn members.")
        if get_power(ctx.author) < get_power(member):
            return await ctx.send("🚫 Cannot warn higher staff.")

    warnings.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} warned | **{reason}**")

@bot.command()
async def warnings(ctx, member: discord.Member):
    ws = warnings.get(member.id, [])
    if not ws:
        return await ctx.send(f"✅ {member.mention} has no warnings.")
    await ctx.send("\n".join(f"{i+1}. {w}" for i, w in enumerate(ws)))

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if not is_boss(ctx.author):
        return await ctx.send("❌ Only Founder / Co-Owner")
    warnings.pop(member.id, None)
    await ctx.send(f"✅ Warnings cleared for {member.mention}")

# ================= MODERATION =================
@bot.command()
async def clear(ctx, amount: int):
    if not is_boss(ctx.author) and get_power(ctx.author) < 60:
        return await ctx.send("❌ No permission.")
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=3)

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    if not is_boss(ctx.author) and get_power(ctx.author) < get_power(member):
        return await ctx.send("🚫 Cannot timeout higher staff.")
    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"⏳ {member.mention} timed out for {minutes} minutes")

@bot.command()
async def untimeout(ctx, member: discord.Member):
    if not is_boss(ctx.author):
        return await ctx.send("❌ Only Founder / Co-Owner")
    await member.timeout(None)
    await ctx.send("✅ Timeout removed")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if not is_boss(ctx.author) and get_power(ctx.author) < get_power(member):
        return await ctx.send("🚫 Cannot kick higher staff.")
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kicked")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if not is_boss(ctx.author) and get_power(ctx.author) < get_power(member):
        return await ctx.send("🚫 Cannot ban higher staff.")
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banned")

@bot.command()
async def unban(ctx, user_id: int):
    if not is_boss(ctx.author):
        return await ctx.send("❌ Only Founder / Co-Owner")
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned {user}")

# ================= SLASH COMMANDS =================
@bot.tree.command(name="clear")
async def slash_clear(interaction: discord.Interaction, amount: int):
    if not is_boss(interaction.user):
        return await interaction.response.send_message("❌ No permission", ephemeral=True)
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("🧹 Messages cleared", ephemeral=True)

@bot.tree.command(name="timeout")
async def slash_timeout(interaction: discord.Interaction, member: discord.Member, minutes: int):
    if not is_boss(interaction.user):
        return await interaction.response.send_message("❌ No permission", ephemeral=True)
    await member.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message("⏳ User timed out")

@bot.tree.command(name="ban")
async def slash_ban(interaction: discord.Interaction, member: discord.Member):
    if not is_boss(interaction.user):
        return await interaction.response.send_message("❌ No permission", ephemeral=True)
    await member.ban()
    await interaction.response.send_message("🔨 User banned")

# ================= RUN =================
bot.run(TOKEN)
