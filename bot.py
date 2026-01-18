import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import os  # added to fetch TOKEN from Railway environment

# ================= BASIC SETUP =================
intents = discord.Intents.all()
TOKEN = os.environ["TOKEN"]  # fetch the token from Railway env variables
bot = commands.Bot(
    command_prefix="ncl",
    intents=intents,
    help_command=None  # we use custom help
)

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= CUSTOM HELP =================
@bot.command(name="help", aliases=["nclhelp"])
async def help_command(ctx):
    embed = discord.Embed(
        title="📘 NCL MOD BOT HELP",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🛠 Admin Commands",
        value=(
            "`nclban @user reason`\n"
            "`nclunban user_id`\n"
            "`nclmute @user`\n"
            "`nclunmute @user`\n"
            "`nclwarn @user reason`\n"
            "`nclunwarn @user`\n"
        ),
        inline=False
    )

    embed.add_field(
        name="⚙ Utility",
        value="`nclping` - bot latency",
        inline=False
    )

    embed.set_footer(text="NCL MOD BOT • clean & stable")
    await ctx.send(embed=embed)

# ================= UTILITY =================
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

# ================= ADMIN CHECK =================
def admin_only():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# ================= MODERATION =================
@bot.command(aliases=["b"])
@admin_only()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 **Banned** {member} | {reason}")

@bot.command()
@admin_only()
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ **Unbanned** {user}")

@bot.command(aliases=["m"])
@admin_only()
async def mute(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f"🔇 **Muted** {member}")

@bot.command()
@admin_only()
async def unmute(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"🔊 **Unmuted** {member}")
    else:
        await ctx.send("❌ User is not muted")

# ================= WARN SYSTEM =================
warns = {}

@bot.command()
@admin_only()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    warns.setdefault(member.id, []).append(reason)
    await ctx.send(f"⚠ **Warned** {member}\nReason: {reason}")

@bot.command()
@admin_only()
async def unwarn(ctx, member: discord.Member):
    if member.id in warns and warns[member.id]:
        warns[member.id].pop()
        await ctx.send(f"✅ Removed **one warn** from {member}")
    else:
        await ctx.send("❌ User has no warns")

# ================= ERROR HANDLING =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission")
    else:
        await ctx.send("⚠ Something went wrong")
        print(error)

# ================= START BOT =================
bot.run(TOKEN)
