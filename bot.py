import discord
from discord.ext import commands
import os
import random

# -------------------------
# Intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")  # Remove default help

# -------------------------
# Invite tracker
invite_tracker = {}

# Server & channel IDs
GUILD_ID = 1457168592763355148           # Your server ID
INVITE_CHANNEL_ID = 1457800213250179104  # Invite messages
BOOST_CHANNEL_ID = 1460708408343658672   # Boost alerts

# Fun action messages
slap_messages = [
    "{} slaps {}! 😲",
    "{} gave {} a big slap! 👋",
    "{} just smacked {}! 🔨"
]

kiss_messages = [
    "{} kisses {}! 😘",
    "{} gave {} a sweet kiss! 💋",
    "{} plants a kiss on {}! ❤️"
]

# -------------------------
# Events
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        invites = await guild.invites()
        invite_tracker[guild.id] = {invite.code: invite.uses for invite in invites}
        print("Invite tracker initialized.")

# Member join -> invite tracker
@bot.event
async def on_member_join(member):
    guild = bot.get_guild(GUILD_ID)
    if guild.id != GUILD_ID:
        return

    invites = await guild.invites()
    old_invites = invite_tracker.get(guild.id, {})

    used_invite = None
    for invite in invites:
        if invite.uses > old_invites.get(invite.code, 0):
            used_invite = invite
            break

    # Update tracker
    invite_tracker[guild.id] = {invite.code: invite.uses for invite in invites}

    # Send message
    channel = guild.get_channel(INVITE_CHANNEL_ID)
    if channel:
        if used_invite:
            await channel.send(
                f"Welcome {member.mention}! Invited by {used_invite.inviter.mention}\n"
                f"Total invites by {used_invite.inviter.mention}: {used_invite.uses}"
            )
        else:
            await channel.send(f"Welcome {member.mention} to the server!")

# Boost alerts
@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        guild = after.guild
        channel = guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            messages = [
                f"Wow! {after.mention} just boosted the server! 💎 You're awesome!",
                f"Thank you {after.mention} for the boost! 🚀 The server shines brighter now!",
                f"{after.mention} is a legend for boosting the server! ⭐ Keep it up!",
                f"Amazing! {after.mention} has boosted us! 🎉 Much appreciated!",
            ]
            await channel.send(random.choice(messages))

# -------------------------
# Commands

# Ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# Members count
@bot.command()
async def members(ctx):
    guild = bot.get_guild(GUILD_ID)
    if guild:
        await ctx.send(f"Total members in the server: {guild.member_count}")

# Who invited a member
@bot.command()
async def invitedby(ctx, member: discord.Member):
    guild = bot.get_guild(GUILD_ID)
    invites = await guild.invites()
    inviter = None
    for invite in invites:
        if invite.uses > invite_tracker[guild.id].get(invite.code, 0):
            inviter = invite.inviter
            break
    if inviter:
        await ctx.send(f"{member.mention} was invited by {inviter.mention}")
    else:
        await ctx.send(f"Could not detect who invited {member.mention}")
    # Update tracker
    invite_tracker[guild.id] = {invite.code: invite.uses for invite in invites}

# Count how many a member has invited
@bot.command()
async def invites(ctx, member: discord.Member = None):
    guild = bot.get_guild(GUILD_ID)
    if not member:
        member = ctx.author

    invites = await guild.invites()
    total = sum(invite.uses for invite in invites if invite.inviter == member)
    await ctx.send(f"{member.mention} has invited **{total}** member(s)!")

# Top inviters leaderboard
@bot.command()
async def leaderboard(ctx):
    guild = bot.get_guild(GUILD_ID)
    invites = await guild.invites()
    leaderboard = {}
    for invite in invites:
        leaderboard[invite.inviter] = leaderboard.get(invite.inviter, 0) + invite.uses

    top = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]

    embed = discord.Embed(title="Top Inviters", color=discord.Color.gold())
    for i, (user, count) in enumerate(top, 1):
        embed.add_field(name=f"{i}. {user}", value=f"Invites: {count}", inline=False)

    await ctx.send(embed=embed)

# Slap command
@bot.command()
async def slap(ctx, member: discord.Member):
    await ctx.send(random.choice(slap_messages).format(ctx.author.mention, member.mention))

# Kiss command
@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(random.choice(kiss_messages).format(ctx.author.mention, member.mention))

# Custom help
@bot.command(name="bothelp")
async def bothelp(ctx):
    if ctx.author.bot:
        return
    embed = discord.Embed(
        title="Server Bot Commands & Fun Features",
        description="All commands available in this server:",
        color=discord.Color.green()
    )
    embed.add_field(name="!ping", value="Check if the bot is online.", inline=False)
    embed.add_field(name="!members", value="Shows total members in the server.", inline=False)
    embed.add_field(name="!invitedby @member", value="Shows who invited a member.", inline=False)
    embed.add_field(name="!invites @member", value="Shows how many members a person has invited.", inline=False)
    embed.add_field(name="!leaderboard", value="Shows the top inviters in the server.", inline=False)
    embed.add_field(name="Invite Tracking", value="Tracks who invited new members automatically.", inline=False)
    embed.add_field(name="Boost Alerts", value="Thanks boosters automatically in a separate channel.", inline=False)
    embed.add_field(name="Fun Commands", value="!slap @member → Slap someone\n!kiss @member → Kiss someone!", inline=False)
    embed.set_footer(text="Use !bothelp to see this message anytime!")
    await ctx.send(embed=embed)

# -------------------------
# Run bot
bot.run(os.environ["TOKEN"])
