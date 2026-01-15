import discord
from discord.ext import commands
import os, random, datetime
import psycopg2

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="ncl", intents=intents, help_command=None)

# ================= ROLE IDS =================
FOUNDER_ID   = 1457168593123803222
COOWNER_ID   = 1457168593123803221
HEAD_MOD_ID  = 1458041286006276267
MOD_ID       = 1458040204781948938
TRIAL_MOD_ID = 1458040060472459488

VIP_ROLE_ID  = 1460000000000000000  # 🔴 CHANGE THIS

ROLE_POWER = {
    FOUNDER_ID: 100,
    COOWNER_ID: 95,
    HEAD_MOD_ID: 80,
    MOD_ID: 60,
    TRIAL_MOD_ID: 40
}

def get_power(member):
    return max((ROLE_POWER.get(r.id, 0) for r in member.roles), default=0)

def can_punish(ctx, target):
    return get_power(ctx.author) > get_power(target)

# ================= DATABASE (POSTGRESQL) =================
DATABASE_URL = os.getenv("DATABASE_URL")
db = psycopg2.connect(DATABASE_URL)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    invites INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS warnings (
    user_id BIGINT,
    reason TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS profiles (
    user_id BIGINT PRIMARY KEY,
    nickname TEXT,
    emoji TEXT,
    bio TEXT,
    color TEXT
)
""")

db.commit()

def get_user(uid):
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (uid,))
    db.commit()

# ================= READY =================
invites_cache = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # Initialize invites cache
    for g in bot.guilds:
        invites_cache[g.id] = await g.invites()

# ================= INVITES → CASH =================
@bot.event
async def on_member_join(member):
    before = invites_cache.get(member.guild.id, [])
    after = await member.guild.invites()

    for i in after:
        for b in before:
            if i.code == b.code and i.uses > b.uses:
                get_user(i.inviter.id)
                cur.execute(
                    "UPDATE users SET invites = invites + 1, coins = coins + 25 WHERE user_id=%s",
                    (i.inviter.id,)
                )
                db.commit()
                break

    invites_cache[member.guild.id] = after

# ================= ECONOMY =================
@bot.command()
async def balance(ctx):
    get_user(ctx.author.id)
    cur.execute("SELECT coins FROM users WHERE user_id=%s", (ctx.author.id,))
    await ctx.send(f"💰 You have **{cur.fetchone()[0]} coins**")

@bot.command()
async def daily(ctx):
    get_user(ctx.author.id)
    cur.execute("UPDATE users SET coins = coins + 50 WHERE user_id=%s", (ctx.author.id,))
    db.commit()
    await ctx.send("💸 You got **50 daily coins**")

@bot.command()
async def gamble(ctx, amount: int):
    get_user(ctx.author.id)
    cur.execute("SELECT coins FROM users WHERE user_id=%s", (ctx.author.id,))
    coins = cur.fetchone()[0]

    if amount <= 0 or coins < amount:
        return await ctx.send("❌ Invalid amount")

    if random.choice([True, False]):
        cur.execute("UPDATE users SET coins = coins + %s WHERE user_id=%s", (amount, ctx.author.id))
        msg = f"🎰 You WON **{amount} coins**"
    else:
        cur.execute("UPDATE users SET coins = coins - %s WHERE user_id=%s", (amount, ctx.author.id))
        msg = f"💀 You LOST **{amount} coins**"

    db.commit()
    await ctx.send(msg)

# ================= SHOP =================
SHOP = {
    "vip": 500,
    "rename": 200,
    "rolecolor": 300
}

@bot.command()
async def shop(ctx):
    embed = discord.Embed(
        title="🛒 NCL SHOP",
        description="Spend your hard-earned coins wisely 💸",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🎖️ VIP — 500 coins",
        value="• VIP role\n• Flex status\n• Future perks",
        inline=False
    )
    embed.add_field(
        name="✏️ Rename — 200 coins",
        value="Change your nickname once",
        inline=False
    )
    embed.add_field(
        name="🎨 Role Color — 300 coins",
        value="Custom role color (admin approved)",
        inline=False
    )

    embed.set_footer(text="Use: nclbuy <item>")
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, item: str):
    if item not in SHOP:
        return await ctx.send("❌ Item not found")

    get_user(ctx.author.id)
    cur.execute("SELECT coins FROM users WHERE user_id=%s", (ctx.author.id,))
    coins = cur.fetchone()[0]

    if coins < SHOP[item]:
        return await ctx.send("❌ Not enough coins")

    if item == "vip":
        vip_role = ctx.guild.get_role(VIP_ROLE_ID)
        if vip_role in ctx.author.roles:
            return await ctx.send("⚠️ You already have VIP")
        await ctx.author.add_roles(vip_role, reason="Bought VIP from shop")

    cur.execute(
        "UPDATE users SET coins = coins - %s WHERE user_id=%s",
        (SHOP[item], ctx.author.id)
    )
    db.commit()

    await ctx.send(f"✅ You bought **{item.upper()}**")

# ================= WARN SYSTEM + AUTO BAN =================
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not can_punish(ctx, member):
        return await ctx.send("🚫 Cannot warn higher role")

    get_user(member.id)
    cur.execute("INSERT INTO warnings VALUES (%s,%s)", (member.id, reason))
    db.commit()

    cur.execute("SELECT COUNT(*) FROM warnings WHERE user_id=%s", (member.id,))
    count = cur.fetchone()[0]

    if count >= 5:
        await member.ban(reason="Auto-ban: 5 warnings")
        await ctx.send("🔨 **AUTO-BANNED (5 WARNINGS)**")
    else:
        await ctx.send(f"⚠️ Warning added ({count}/5)")

@bot.command()
async def warnings(ctx, member: discord.Member):
    cur.execute("SELECT COUNT(*) FROM warnings WHERE user_id=%s", (member.id,))
    await ctx.send(f"📝 Warnings: **{cur.fetchone()[0]}**")

@bot.command()
async def unwarn(ctx, member: discord.Member):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Head Mod+ only")
    cur.execute("DELETE FROM warnings WHERE user_id=%s", (member.id,))
    db.commit()
    await ctx.send("✅ Warnings cleared")

# ================= MODERATION =================
@bot.command()
async def kick(ctx, member: discord.Member):
    if not can_punish(ctx, member):
        return await ctx.send("🚫 Cannot kick higher role")
    await member.kick()
    await ctx.send("👢 User kicked")

@bot.command()
async def ban(ctx, member: discord.Member):
    if not can_punish(ctx, member):
        return await ctx.send("🚫 Cannot ban higher role")
    await member.ban()
    await ctx.send("🔨 User banned")

@bot.command()
async def unban(ctx, user_id: int):
    if get_power(ctx.author) < 80:
        return await ctx.send("❌ Head Mod+ only")
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send("🎉 User unbanned")

# ================= FUN =================
@bot.command()
async def slap(ctx, m: discord.Member):
    await ctx.send(f"👋 {ctx.author.mention} slapped {m.mention}")

@bot.command()
async def hug(ctx, m: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention} hugged {m.mention}")

@bot.command()
async def kiss(ctx, m: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention} kissed {m.mention}")

@bot.command()
async def pat(ctx, m: discord.Member):
    await ctx.send(f"✨ {ctx.author.mention} patted {m.mention}")

@bot.command()
async def ship(ctx, u1: discord.Member, u2: discord.Member):
    await ctx.send(f"❤️ {u1.name} x {u2.name} = {random.randint(1,100)}%")

# ================= DAILY MISSIONS =================
MISSIONS = [
    {"task": "Say hi 3 times today", "coins": 20},
    {"task": "Slap someone", "coins": 15},
    {"task": "Give a hug", "coins": 10},
]

user_missions = {}  # {user_id: {"task": task_index, "completed": 0}}

@bot.command()
async def mission(ctx):
    uid = ctx.author.id
    if uid not in user_missions:
        task_index = random.randint(0, len(MISSIONS) - 1)
        user_missions[uid] = {"task": task_index, "completed": 0}
    task = MISSIONS[user_missions[uid]["task"]]["task"]
    await ctx.send(f"📝 Your mission: **{task}**")

def complete_mission(uid, action_name):
    if uid in user_missions:
        current_task = user_missions[uid]["task"]
        mission = MISSIONS[current_task]
        if action_name.lower() in mission["task"].lower():
            user_missions[uid]["completed"] += 1
            if user_missions[uid]["completed"] >= 1:
                coins = mission["coins"]
                get_user(uid)
                cur.execute("UPDATE users SET coins = coins + %s WHERE user_id=%s", (coins, uid))
                db.commit()
                user_missions.pop(uid)
                return coins
    return 0

# Update fun commands to handle missions
@bot.command()
async def slap(ctx, m: discord.Member):
    await ctx.send(f"👋 {ctx.author.mention} slapped {m.mention}")
    coins_earned = complete_mission(ctx.author.id, "slap")
    if coins_earned:
        await ctx.send(f"🎉 Mission completed! You earned **{coins_earned} coins**")

@bot.command()
async def hug(ctx, m: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention} hugged {m.mention}")
    coins_earned = complete_mission(ctx.author.id, "hug")
    if coins_earned:
        await ctx.send(f"🎉 Mission completed! You earned **{coins_earned} coins**")

# ================= MINI-GAMES =================
@bot.command()
async def nclslots(ctx, bet: int):
    get_user(ctx.author.id)
    cur.execute("SELECT coins FROM users WHERE user_id=%s", (ctx.author.id,))
    coins = cur.fetchone()[0]
    
    if bet <= 0 or bet > coins:
        return await ctx.send("❌ Invalid bet")
    
    symbols = ["🍎", "🍌", "🍒", "🍇", "⭐", "💎"]
    result = [random.choice(symbols) for _ in range(3)]
    await ctx.send(" | ".join(result))
    
    if len(set(result)) == 1:
        winnings = bet * 5
        msg = f"🎉 JACKPOT! You won {winnings} coins!"
    elif len(set(result)) == 2:
        winnings = bet * 2
        msg = f"✨ Nice! You won {winnings} coins!"
    else:
        winnings = -bet
        msg = f"💀 You lost {bet} coins!"
    
    cur.execute("UPDATE users SET coins = coins + %s WHERE user_id=%s", (winnings, ctx.author.id))
    db.commit()
    await ctx.send(msg)

@bot.command()
async def nclroll(ctx, guess: int):
    if guess < 1 or guess > 6:
        return await ctx.send("🎲 Guess a number between 1 and 6!")
    
    roll = random.randint(1, 6)
    if guess == roll:
        get_user(ctx.author.id)
        cur.execute("UPDATE users SET coins = coins + 10 WHERE user_id=%s", (ctx.author.id,))
        db.commit()
        await ctx.send(f"🎲 You guessed {guess} and rolled {roll}! You won 10 coins!")
    else:
        await ctx.send(f"🎲 You guessed {guess} but rolled {roll}. Better luck next time!")

@bot.command()
async def nclrps(ctx, member: discord.Member, choice: str):
    choices = ["rock", "paper", "scissors"]
    user_choice = choice.lower()
    if user_choice not in choices:
        return await ctx.send("❌ Choose rock, paper, or scissors")
    
    bot_choice = random.choice(choices)
    result = ""
    
    if user_choice == bot_choice:
        result = "It's a tie!"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        result = f"You win! {user_choice} beats {bot_choice}"
        get_user(ctx.author.id)
        cur.execute("UPDATE users SET coins = coins + 10 WHERE user_id=%s", (ctx.author.id,))
        db.commit()
    else:
        result = f"You lose! {bot_choice} beats {user_choice}"
    
    await ctx.send(f"{ctx.author.mention} chose {user_choice}\n{member.mention} chose {bot_choice}\n{result}")

# ================= CUSTOM PROFILES =================
@bot.command()
async def nclsetbio(ctx, *, bio: str):
    get_user(ctx.author.id)
    cur.execute("""
    INSERT INTO profiles (user_id, bio) VALUES (%s, %s)
    ON CONFLICT (user_id) DO UPDATE SET bio=%s
    """, (ctx.author.id, bio, bio))
    db.commit()
    await ctx.send("✅ Bio updated!")

@bot.command()
async def nclprofile(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    cur.execute("SELECT nickname, emoji, bio, color FROM profiles WHERE user_id=%s", (member.id,))
    data = cur.fetchone()
    
    embed = discord.Embed(title=f"{member.name}'s Profile", color=discord.Color.blue())
    
    if data:
        nickname, emoji, bio, color = data
        if nickname: embed.add_field(name="Nickname", value=nickname, inline=False)
        if emoji: embed.add_field(name="Emoji", value=emoji, inline=False)
        if bio: embed.add_field(name="Bio", value=bio, inline=False)
        if color:
            try:
                embed.color = discord.Color.from_str(color)
            except:
                pass
    
    await ctx.send(embed=embed)
# ================= CUSTOM HELP =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📜 NCL Bot Commands",
        description="Here's a list of all commands you can use!",
        color=discord.Color.blurple()
    )

    # ECONOMY
    embed.add_field(
        name="💰 Economy",
        value=(
            "`nclbalance` — Check your coins\n"
            "`ncldaily` — Claim daily coins\n"
            "`nclgamble <amount>` — Gamble your coins\n"
            "`nclshop` — See items in the shop\n"
            "`nclbuy <item>` — Buy an item"
        ),
        inline=False
    )

    # MODERATION
    embed.add_field(
        name="🔨 Moderation",
        value=(
            "`nclkick @user` — Kick a member\n"
            "`nclban @user` — Ban a member\n"
            "`nclunban <user_id>` — Unban a member\n"
            "`nclwarn @user <reason>` — Warn a member\n"
            "`nclwarnings @user` — Check warnings\n"
            "`nclunwarn @user` — Clear warnings"
        ),
        inline=False
    )

    # FUN
    embed.add_field(
        name="🎉 Fun",
        value=(
            "`nclslap @user` — Slap someone\n"
            "`nclhug @user` — Hug someone\n"
            "`nclkiss @user` — Kiss someone\n"
            "`nclpat @user` — Pat someone\n"
            "`nclship @user @user` — Check compatibility\n"
            "`ncljoke @user` — Tell a joke to someone"
        ),
        inline=False
    )

    # DAILY MISSIONS
    embed.add_field(
        name="📋 Daily Missions",
        value="`nclmission` — Get your daily task for extra coins",
        inline=False
    )

    # MINI-GAMES
    embed.add_field(
        name="🎲 Mini-Games",
        value=(
            "`nclslots <bet>` — Play slot machine\n"
            "`nclroll <1-6>` — Roll dice for coins\n"
            "`nclrps @user <rock/paper/scissors>` — Play rock-paper-scissors"
        ),
        inline=False
    )

    # PROFILES
    embed.add_field(
        name="📝 Profiles",
        value=(
            "`nclprofile @user` — See someone's profile\n"
            "`nclsetbio <text>` — Set your bio"
        ),
        inline=False
    )

    embed.set_footer(text="Use ncl<command> to run a command")
    await ctx.send(embed=embed)


# ================= RUN =================
bot.run(os.getenv("TOKEN"))
