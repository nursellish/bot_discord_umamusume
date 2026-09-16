import os
import time
import logging

import discord
from discord.ext import tasks, commands

from datetime import datetime, timezone

from dotenv import load_dotenv
from scraper import get_news
from database import load_sent_news, save_sent_news


# ============================================================
# ⚙️ LOGGING SISTEM
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ============================================================
# ⚙️ LOAD ENVIRONMENT VARIABLE
# ============================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))


# ============================================================
# 🤖 DISCORD BOT
# ============================================================

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ============================================================
# 🧠 MENYIMPAN NEWS YANG SUDAH DIKIRIM / DIKENAL
# ============================================================

sent_news = load_sent_news()

last_check = None

# ============================================================
# 🎨 WARNA EMBED
# ============================================================

UMA_COLOR = discord.Color.from_str("#00C3A5")


# ============================================================
# 🔎 MENENTUKAN KATEGORI NEWS
# ============================================================

def get_category(title, message):

    text = f"{title} {message}".lower()

    # -----------------------------
    # 🎟️ GACHA
    # -----------------------------

    if any(keyword in text for keyword in [
        "pickup",
        "gacha",
        "scout"
    ]):

        return "🎟️ Gacha / Banner"


    # -----------------------------
    # 🏆 CHAMPIONS MEETING
    # -----------------------------

    if any(keyword in text for keyword in [
        "champions meeting",
        "champion meeting"
    ]):

        return "🏆 Champions Meeting"


    # -----------------------------
    # 🏇 LEGEND RACE
    # -----------------------------
    
    if "legend race" in text:
    
        return "🏇 Legend Race"


    # -----------------------------
    # 🎁 CAMPAIGN
    # -----------------------------
    
    if any(keyword in text for keyword in [
        "celebration",
        "campaign",
        "bonus rewards"
    ]):
    
        return "🎁 Campaign"


    # -----------------------------
    # 🎉 EVENT
    # -----------------------------

    if "story event" in text:

        return "🎉 Event"


    # -----------------------------
    # 🔧 UPDATE
    # -----------------------------

    if any(keyword in text for keyword in [
        "update",
        "new functions"
    ]):

        return "🔧 Game Update"


    return "📰 Official News"


# ============================================================
# STATUS
# ============================================================

def get_status(title, message):

    text = f"{title} {message}".lower()

    # -----------------------------
    # 🟡 COMING SOON
    # -----------------------------

    if any(keyword in text for keyword in [
        "coming soon",
        "coming shortly",
        "will be held",
        "will begin", 
        "are set to begin"
        "planned to be implemented",
        "in the near future"
    ]):

        return "🟡 Coming Soon"
    
    # -----------------------------
    # 🟢 AVAILABLE NOW
    # -----------------------------

    if any(keyword in text for keyword in [
        "now available",
        "available now",
        "out now",
        "is here",
        "is now live"
        "has begun",
        "have begun"
    ]):

        return "🟢 Available Now"

    # -----------------------------
    # 🔵 INFORMATION
    # -----------------------------

    return "🔵 Information"


# ============================================================
# STATUS COLOR
# ============================================================

def get_status_color(status):

    if status == "🟡 Coming Soon":
        return discord.Color.gold()

    if status == "🟢 Available Now":
        return discord.Color.green()

    return discord.Color.blue()


# ============================================================
# FORMAT DATE
# ============================================================

def format_date(date_string):

    date = datetime.strptime(
        date_string,
        "%Y-%m-%d %H:%M:%S"
    )

    return date.strftime(
        "%d %B %Y • %H:%M UTC"
    )


# ============================================================
# 📢 KIRIM NEWS KE DISCORD
# ============================================================

async def send_news(channel, news):

    title = news["title"]
    news_id = news["id"]
    image = news["image"]

    news_url = f"https://umamusume.com/news/{news_id}/"

    published = format_date(
        news["post_at"]
    )

    category = get_category(title, news["message"])

    status = get_status(
        title,
        news["message"]
    )
    color = get_status_color(status)

    embed = discord.Embed(

        title=category,

        description=(
            f"📌 **{title}**\n\n"
            f"🆔 News ID: `{news_id}`"
        ),

        url=news_url,

        color=color,

        timestamp=datetime.now(timezone.utc)
    )


    embed.set_author(
        name="Satono Diamond • Official News"
    )

    embed.add_field(
        name="📝 Preview",
        value=news["message"],
        inline=False
    )

    embed.add_field(
        name="📢 Kategori",
        value=category,
        inline=True
    )


    embed.add_field(
        name="📊 Status",
        value=status,
        inline=True
    )


    embed.add_field(
        name="📅 Published",
        value=published,
        inline=False
    )


    if image:

        embed.set_image(
            url=image
        )


    embed.set_footer(
        text="Satono Diamond • Fan-made Timeline • Not affiliated with Cygames "
    )

    try:
        await channel.send(
            embed=embed
        )
    except discord.Forbidden as error:

        logging.error(
            f"Discord Permission Error: {error}"
        )

        raise

    except discord.HTTPException as error:

        logging.error(
            f"Discord HTTP Error: {error}"
        )

        raise

# ============================================================
# 🚀 BOT ONLINE
# ============================================================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"Bot aktif sebagai: {bot.user}")
    print("=" * 50)

    # --------------------------------------------------------
    # BASELINE
    # --------------------------------------------------------
    
    print("📚 Jumlah known news:", len(sent_news))

    if not sent_news:

        print("📚 Mengambil berita awal...")
        news_list = get_news()

        for news in news_list:
            sent_news.add(news["id"])

        save_sent_news(sent_news)

        print(
            f"📚 Baseline: {len(sent_news)} berita sudah dikenal."
        )
    else:
        print(

            f"📚 Memuat {len(sent_news)} berita dari penyimpanan."
        )

    # --------------------------------------------------------
    # START MONITORING
    # --------------------------------------------------------

    logging.info("Memulai monitoring...")

    if not check_news.is_running():

        check_news.start()



@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.BadArgument):

        await ctx.send(
            "Salah Torena-san ❌. ID berita harus berupa angka.\n"
            "Dia kasih contoh ya : `!testnews 1023`"
        )

    elif isinstance(error, commands.CommandNotFound):

        await ctx.send(
            f" Sorry ye Dia tidak membuat command `{ctx.message.content.split()[0]}` jadi gk bkl ketemu."
        )

    else:

        print(f"❌ Command error: {error}")
  

# ============================================================
# ⏰ CEK NEWS
# ============================================================

@tasks.loop(seconds=60)
async def check_news():

    global last_check

    last_check = datetime.now(timezone.utc)

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:

        print("❌ Channel tidak ditemukan.")

        return

    try:

        logging.info("Mengecek Official Uma Musume News...")

        news_list = get_news()

        if news_list is None:

            logging.warning(
                "News gagal diambil. Monitoring akan mencoba lagi nanti."
            )

            return

        for news in news_list:

            news_id = news["id"]

            # ------------------------------------------------
            # SUDAH DIKENAL?
            # ------------------------------------------------

            if news_id in sent_news:

                continue

            # ------------------------------------------------
            # BERITA BARU
            # ------------------------------------------------

            logging.info(
                f"Berita baru ditemukan: {news['title']} (ID: {news['id']})"
            )

            print("ID:", news["id"])
            print("TITLE:", news["title"])
            print("POST:", news["post_at"])
            print("IMAGE:", news["image"])

            # ------------------------------------------------
            # KIRIM KE DISCORD
            # ------------------------------------------------

            await send_news(
                channel,
                news
            )

            sent_news.add(news_id)

            save_sent_news(sent_news)

            # ------------------------------------------------
            # KONFIRMASI BERITA TERKIRIM
            # ------------------------------------------------

            logging.info(
                f"News berhasil dikirim: {news['title']} (ID: {news_id})"
            )

    except discord.Forbidden as error:

        logging.error(
            f"Discord Permission Error: {error}"
        )

    except discord.HTTPException as error:

        logging.error(
            f"Discord HTTP Error: {error}"
        )

    except Exception:

        logging.exception(
            "Unexpected Error"
        )

        

# ============================================================
# ⏰ CEK NEWS BEFORE LOOP
# ============================================================

@check_news.before_loop
async def before_check_news():

    logging.info("Menunggu bot siap...")

    await bot.wait_until_ready()

    logging.info("Bot siap, monitoring dimulai.")


# ============================================================
# 👋 COMMAND TEST
# ============================================================

@bot.command(name="halo")
async def halo(ctx):

    await ctx.send(
        "Halo Torena-san! ✨\n"
        "Dia siap memantau Official Uma Musume News!"
    )


bot.remove_command("help")

@bot.command(name="help")
async def help_command(ctx):

    embed = discord.Embed(
        title="📖 Uma Musume Bot Help",
        description="Berikut daftar command yang tersedia:",
        color=UMA_COLOR
    )

    embed.add_field(
        name="📊 !status",
        value="Melihat status bot dan monitoring.",
        inline=False
    )

    embed.add_field(
        name="📰 !latest",
        value="Melihat berita resmi terbaru.",
        inline=False
    )

    embed.add_field(
        name="📈 !stats",
        value="Melihat statistik berita.",
        inline=False
    )

    embed.add_field(
        name="🧪 !testnews <id>",
        value="Mengirim berita tertentu untuk testing.\nContoh: `!testnews 1023`",
        inline=False
    )

    embed.add_field(
        name="📖 !help",
        value="Menampilkan daftar command ini.",
        inline=False
    )

    embed.set_footer(
        text="Satono Diamond • Fan-made Timeline • Not affiliated with Cygames "
    )

    await ctx.send(embed=embed)
    

@bot.command(name="testnews")
async def testnews(ctx, news_id: int= None):

    if news_id is None:
        await ctx.send(
            "Format command salah Torena-san `!testnews` ❌.\n\n"
            "Gunakan format ini :`!testnews <id>`\n"
            "Dia kasih contoh ya : `!testnews 1023` ✅"
        )
        return

    news_list = get_news(limit=50)

    if not news_list:
        await ctx.send("❌ Tidak ada berita dari API.")
        return

    # news = news_list[0]
    news= None

    for item in news_list:
        if item["id"] == news_id:
            news = item
            break

    if news is None:

        await ctx.send(
            f"❌ News ID `{news_id}` tidak ditemukan."
        )

        return

    print("TITLE:", news["title"])
    print("MESSAGE:", news["message"])

    await send_news(
        ctx.channel,
        news
    )

    print(
        f"🧪 Test news dikirim: {news['title']}"
    )


@bot.command(name="latest")
async def latest(ctx):

    news_list = get_news(limit=5)

    if not news_list:
        await ctx.send(
            "❌ Tidak ada berita dari API."
        )
        return

    embed = discord.Embed(
        title=f"📰 Latest {len(news_list)} Official News",
        color=UMA_COLOR
    )

    for index, news in enumerate(news_list, start=1):

        status= get_status(
            news["title"],
            news["message"]
        )

        category = get_category(
            news["title"],
            news["message"]
        )

        published = format_date(
            news["post_at"]
        )

        embed.description = (
            f"{embed.description or ''}"
            f"**{index}. [{news['title']}](https://umamusume.com/news/{news['id']}/)**\n"
            f"🆔 ID: `{news['id']}`\n"
            f"📢 Kategori: {category}\n"
            f"📊 Status: {status}\n"
            f"📅 Published: {published}\n"
            f"───────────────────────────────────\n\n"

        )

    await ctx.send(embed=embed)
    

@bot.command(name="status")
async def status(ctx):

    embed = discord.Embed(
        title="🤖 Bot Status",
        color=UMA_COLOR
    )

    embed.add_field(
        name="🟢 Status",
        value="Online",
        inline=True
    )

    embed.add_field(
        name="📚 Known News",
        value=str(len(sent_news)),
        inline=True
    )

    monitoring = (
        "Active"
        if check_news.is_running()
        else "Stopped"
    )

    interval = check_news.seconds

    embed.add_field(
        name="🔎 Monitoring",
        value=monitoring,
        inline=True
    )
    
    embed.add_field(
        name="⏱️ Interval",
        value=f"{int(interval)} seconds",
        inline=True
    )

    embed.add_field(
        name="🕐 Last Check",
        value=(
            last_check.strftime("%d %B %Y • %H:%M:%S UTC")
            if last_check
            else "Belum ada pengecekan"

        ),

        inline=False
    )

    await ctx.send(embed=embed)


@bot.command(name="stats")
async def stats(ctx):

    news_list = get_news(limit=50)

    if not news_list:
        await ctx.send(
            "❌ Tidak ada berita dari API."
        )
        return


    embed = discord.Embed(
        title="📊 News Statistics",
        color=UMA_COLOR
    )

    embed.add_field(
        name="🔎 Analyzed",
        value=f"Latest {len(news_list)} official news",
        inline=False
    )


    category_count = {}
    
    for news in news_list:

        category = get_category(
            news["title"],
            news["message"]
        )

        if category not in category_count:
            category_count[category] = 0

        category_count[category] += 1


    for category, count in category_count.items():

        embed.add_field(
            name=category,
            value=str(count),
            inline=True
        )

    status_count = {}

    for news in news_list:

        status = get_status(
            news["title"],
            news["message"]
        )

        if status not in status_count:
            status_count[status] = 0

        status_count[status] += 1

    for status, count in status_count.items():

        embed.add_field(
            name=status,
            value=str(count),
            inline=True
        )

    await ctx.send(embed=embed)

    

# ============================================================
# ▶️ START BOT
# ============================================================

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN belum ditemukan di .env"
    )


bot.run(TOKEN)