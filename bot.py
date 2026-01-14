import discord
from discord.ext import commands
import os

# -------------------------
# Intents (needed for members & invites)
intents = discord.Intents.default()
intents.members = True          # for member join events
intents.guilds = True           # for server info
intents.message_content = True  # for commands

bot = commands.Bot(command_prefix="!", intents=intents)

# Remove default help command to use custom help
bot.remove_command("help")

# -------------------------
# Invite tracking dictionary
# {guild_id: {invite_code: uses}}
invite_tracker = {}

# -------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")
    # Initialize invite tracker for each guild
    for guild in bot.guilds:
        invites = await guild.invites()
        invite_tracker[guild.id] = {invite.code: invite.uses for invite in invites}
    print("Invite tracker initialized.")

# -------------------------
# Event: Welcome new member and track invite
@bot.event
async def on_member_join(member):
    guild = member.guild
    invites = await guild.invites()
    old_invites = invite_tracker.get(guild.id, {})
    
    # Find which invite was used
    used_invite = None
    for invite in invites:
        if invite.uses > old_invites.get(invite.code, 0):
            used_invite = invite
            break
    
    # Update tracker
    invite_tracker[guild.id] = {invite.code: invite.uses for invite in invites}
    
    # Send welcome message
    channel = guild.system_channel  # default system channel for welcome
    if channel:
        if used_invite:
            await channel.send(f"Welcome {member.mention}! Invited by {used_invite.inviter.mention}")
        else:
            await channel.send(f"Welcome {member.mention} to the server!")

# -------------------------
# Event: Boost alert
@bot.event
async def on_member_update(before, after):
    # Check if a member boosted the server
    if before.premium_since is None and after.premium_since is not None:
        guild = after.guild
        channel = guild.system_channel
        if channel:
            await channel.send(f"Thank you {after.mention} for boosting the server! 💎")

# -------------------------
# Custom Help Command
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Server Help & Commands",
        description="Here are the useful commands and info:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!ping", value="Check if bot is online.", inline=False)
    embed.add_field(name="!help", value="Shows this help message.", inline=False)
    embed.add_field(name="Invite Tracking", value="Bot tracks who invited new members.", inline=False)
    embed.add_field(name="Boost Alerts", value="Bot thanks boosters automatically.", inline=False)
    embed.set_footer(text="Server Growth & Support Bot")
    
    await ctx.send(embed=embed)

# -------------------------
# Ping command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# -------------------------
# Run bot using environment variable
bot.run(os.environ["TOKEN"])
