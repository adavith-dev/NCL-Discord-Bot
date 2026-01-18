import discord
from discord.ext import commands, tasks
import os, random, asyncio
import psycopg2
from datetime import datetime, timedelta
import openai

# ================= CONFIG =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="ncl", intents=intents, help_command=None)

TOKEN = os.environ.get("TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ================= ROLES & POWER =================
FOUNDER_ID   = 1457168593123803222
COOWNER_ID   = 1457168593123803221
HEAD_MOD_ID  = 1458041286006276267
MOD_ID       = 1458040204781948938
TRIAL_MOD_ID = 1458040060472459488

VIP_ROLE_ID  = 1460000000000000000  # CHANGE THIS

ROLE_POWER = {
    FOUNDER_ID: 100,
    COOWNER_ID: 95,
    HEAD_MOD_ID: 80,
    MOD_ID: 60,
    TRIAL_MOD_ID: 40
}

BOOST_CHANNEL_ID = 1460708408343658672
INVITE_CHANNEL_ID = 1457800213250179104
GUILD_ID = 1457168592763355148

# ================= DATABASE =================
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    coins INT DEFAULT 0,
    xp INT DEFAULT 0,
    level INT DEFAULT 1,
    last_daily TIMESTAMP
)
""")
conn.commit()

# ================= HELP COMMAND =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="NCL Bot Commands",
        description="Fun + Admin + Economy + Leveling System",
        color=discord.Color.purple()
    )
    embed.add_field(name="🎉 Fun Commands",
                    value="`ncljoke @user` - AI joke on user\n`nclslap @user`\n`nclkiss @user`\n`nclhug @user`\n`nclbeg` - earn coins",
                    inline=False)
    embed.add_field(name="💰 Economy",
                    value="`ncshop` - view shop\n`ncldaily` - claim daily coins",
                    inline=False)
    embed.add_field(name="⚡ Admin Commands",
                    value="`nclclear <num>` - clear messages\n`nclgiverole @user <role>` - give role",
                    inline=False)
    embed.set_footer(text="Powered by AI & NCL Staff")
    await ctx.send(embed=embed)

# ================= AUTO ROLE =================
@bot.event
async def on_member_join(member):
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, id=VIP_ROLE_ID)
    if role:
        await member.add_roles(role)
    await member.send(f"Welcome {member.name}! You got the VIP role!")

# ================= LEVELING =================
async def update_xp(user_id, amount=1):
    cur.execute("SELECT xp, level FROM users WHERE user_id=%s", (user_id,))
    result = cur.fetchone()
    if result:
        xp, level = result
        xp += amount
        new_level = level
        if xp >= level*10:  # simple leveling
            xp = xp - level*10
            new_level += 1
        cur.execute("UPDATE users SET xp=%s, level=%s WHERE user_id=%s", (xp, new_level, user_id))
    else:
        cur.execute("INSERT INTO users (user_id, xp) VALUES (%s, %s)", (user_id, amount))
    conn.commit()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await update_xp(message.author.id)
    await bot.process_commands(message)

# ================= DAILY COINS =================
@bot.command()
async def daily(ctx):
    cur.execute("SELECT coins, last_daily FROM users WHERE user_id=%s", (ctx.author.id,))
    result = cur.fetchone()
    now = datetime.utcnow()
    if result:
        coins, last_daily = result
        if last_daily and now - last_daily < timedelta(hours=24):
            await ctx.send(f"{ctx.author.mention}, you already claimed your daily coins!")
            return
        coins += 100
        cur.execute("UPDATE users SET coins=%s, last_daily=%s WHERE user_id=%s", (coins, now, ctx.author.id))
    else:
        cur.execute("INSERT INTO users (user_id, coins, last_daily) VALUES (%s, %s, %s)", (ctx.author.id, 100, now))
    conn.commit()
    await ctx.send(f"{ctx.author.mention} claimed 100 coins! 💰")

# ================= JOKE COMMAND =================
@bot.command()
async def ncljoke(ctx, user: discord.Member):
    try:
        prompt = f"Make a funny joke about {user.name}, family friendly."
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=60
        )
        joke = response.choices[0].text.strip()
        await ctx.send(f"{ctx.author.mention} jokes about {user.mention}: {joke}")
    except Exception as e:
        await ctx.send("Couldn't generate joke 😅")

# ================= SLAP/KISS/HUG =================
@bot.command()
async def slap(ctx, user: discord.Member):
    await ctx.send(f"{ctx.author.mention} slaps {user.mention}! 😳")

@bot.command()
async def kiss(ctx, user: discord.Member):
    await ctx.send(f"{ctx.author.mention} kisses {user.mention}! 😘")

@bot.command()
async def hug(ctx, user: discord.Member):
    await ctx.send(f"{ctx.author.mention} hugs {user.mention}! 🤗")

# ================= CLEAR MESSAGES =================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"Cleared {amount} messages!", delete_after=5)

# ================= GIVE ROLE =================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await ctx.send(f"Gave {role.name} to {user.mention}")

# ================= RUN BOT =================
bot.run(TOKEN)
