import discord
from discord.ext import commands
import os
import random

# -------------------------
# Intents
intents = discord.Intents.default()
intents.members = True          # for member joins
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")  # Remove default help command

# -------------------------
# Variables to store invites
invite_tracker = {}

# Your server and channel IDs
GUILD_ID = 1457168592763355148             # Your server ID
INVITE_CHANNEL_ID = 1457800213250179104    # Channel for invite messages
BOOST_CHANNEL_ID = 1460708408343658672     # Channel for boost alerts

# -------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        invites = await guild.invites()
        invite_tracker[guild.id] = {invite.code: invite.uses for invite in invites}
        print("Invite tracker initialized.")

# -------------------------
@bot.event
async def on_member_join(member):
    guild = bot.get_guild(GUILD_ID)
    if guild.id != GUILD_ID:
        return  # Ignore joins from other servers

    invites = await guild.invites()
    old_invites = invite_tracker.get(guild.id, {})

    used_invite = None
    for invite in invites:
        if invite.uses > old_invites.get(invite.code, 0):
            used_invite = invite
            break

    # Update invite tracker
    invite_tracker[guild.id] = {invite.code: invite.uses for invite in invites}

    # Send invite message to invite channel
    channel = guild.get_channel(INVITE_CHANNEL_ID)
    if channel:
        if used_invite:
            await channel.send(
                f"Welcome {member.mention}! Invited by {used_invite.inviter.mention}\n"
                f"Total invites by {used_invite.inviter.mention}: {used_invite.uses}"
            )
        else:
            await channel.send(f"Welcome {member.mention} to the server!")

# -------------------------
@bot.event
async def on_member_update(before, after):
    # Boost alert
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
# Ping command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# -------------------------
# Members count command
@bot.command()
async def members(ctx):
    guild = bot.get_guild(GUILD_ID)
    if guild:
        await ctx.send(f"Total members in the server: {guild.member_count}")

# -------------------------
# Invited by command
@bot.command()
async def invitedby(ctx, member: discord.Member):
    guild = bot.get_guild(GUILD_ID)
    if guild:
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

# -------------------------
# Custom help command
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Server Bot Help & Commands",
        description="Here are the useful commands and features:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!ping", value="Check if bot is online.", inline=False)
    embed.add_field(name="!help", value="Shows this help message.", inline=False)
    embed.add_field(name="!members", value="Shows total members in the server.", inline=False)
    embed.add_field(name="!invitedby @member", value="Shows who invited a member.", inline=False)
    embed.add_field(name="Invite Tracking", value="Bot tracks who invited new members.", inline=False)
    embed.add_field(name="Boost Alerts", value="Bot thanks boosters automatically in a separate channel.", inline=False)
    embed.set_footer(text="Server Growth & Support Bot")
    await ctx.send(embed=embed)

# -------------------------
# Run bot using environment variable
bot.run(os.environ["TOKEN"])
