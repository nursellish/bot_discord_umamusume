import os
import asyncio
import logging
import sys
import database

import discord
from discord.ext import tasks, commands

from datetime import datetime, timezone

from dotenv import load_dotenv
from scraper import get_news, create_preview
from scraper_guide import get_game8_data

from views.guide_view import GuideView, format_guide_overview

from database import ( 
    load_sent_news, 
    save_sent_news, 
    load_guild_config,
    save_guild_config,
    load_guild_sent_news, 
    save_guild_sent_news
)


# ============================================================
# ⚙️ LOGGING SISTEM
# ============================================================

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stdout
)


# ============================================================
# ⚙️ LOAD ENVIRONMENT VARIABLE
# ============================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


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
guild_config = load_guild_config()
guild_sent_news = load_guild_sent_news()

if database.guild_sent_news_corrupted:
    logging.warning(
        " ⚠️ \nDatabase guild_sent_news rusak."
        "Bot masuk recovery mode."
    )

missing_channel_logged = set()
sending_news = set()

last_check = None
api_status = False

# ============================================================
# 🎨 WARNA EMBED
# ============================================================

UMA_COLOR = discord.Color.from_str("#00C3A5")


# ============================================================
# 🔎 MENENTUKAN KATEGORI NEWS
# ============================================================

def get_category(title, message):

    title_lower = title.lower()

    # -----------------------------
    # 🏆 CHAMPIONS MEETING
    # -----------------------------
    if any(keyword in title_lower for keyword in [
        "champions meeting",
        "champion meeting"
    ]):
        return "🏆 Champions Meeting"

    # -----------------------------
    # 🏇 LEGEND RACE
    # -----------------------------
    if "legend race" in title_lower:
        return "🏇 Legend Race"

    # -----------------------------
    # 🎟️ GACHA
    # -----------------------------
    if any(keyword in title_lower for keyword in [
        "spotlight",
        "pickup",
        "gacha"
    ]):
        return "🎟️ Gacha / Banner"

    # -----------------------------
    # 🎉 EVENT
    # -----------------------------
    if "event" in title_lower:
        return "🎉 Event"

    # -----------------------------
    # 🎁 CAMPAIGN
    # -----------------------------
    if any(keyword in title_lower for keyword in [
        "celebration",
        "campaign",
        "bonus rewards"
    ]):
        return "🎁 Campaign"

    # -----------------------------
    # 🔧 UPDATE
    # -----------------------------
    if any(keyword in title_lower for keyword in [
        "update",
        "new functions"
    ]):
        return "🔧 Game Update"

    return "📰 Official News"


CHANNEL_CATEGORY = {
    "gacha": "🎟️ Gacha / Banner",
    "champions": "🏆 Champions Meeting",
    "legend": "🏇 Legend Race",
    "campaign": "🎁 Campaign",
    "event": "🎉 Event",
    "update": "🔧 Game Update",
    "news": "📰 Official News"
}


CATEGORY_KEY = {
    "🎟️ Gacha / Banner": "gacha",
    "🏆 Champions Meeting": "champions",
    "🏇 Legend Race": "legend",
    "🎁 Campaign": "campaign",
    "🎉 Event": "event",
    "🔧 Game Update": "update",
    "📰 Official News": "news"
}

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
        "are set to begin",
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
        "is now live",
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


def initialize_baseline():

    global api_status

    if sent_news:
        logging.info(
            f"Memuat {len(sent_news)} berita dari penyimpanan."
        )
        return

    logging.info(
        "Database global kosong. Mengambil berita awal..."
    )
    
    news_list = get_news()

    if not news_list:
        logging.warning(
            "Tidak dapat membuat baseline karena berita gagal diambil."
        )
        return

    api_status = True

    for news in news_list:
        sent_news.add(
            news["id"]
        )

    save_sent_news(
        sent_news
    )

    logging.info(
        f"Baseline berhasil dibuat: {len(sent_news)} berita."
    )


def format_time_ago(date_time):

    if not date_time:
        return "Belum ada pengecekan"

    now = datetime.now(timezone.utc)

    difference = now - date_time

    seconds = int(
        difference.total_seconds()
    )

    if seconds < 60:
        return f"{seconds} seconds ago"

    minutes = seconds // 60

    if minutes < 60:
        return f"{minutes} minutes ago"

    hours = minutes // 60

    return f"{hours} hours ago"


# ============================================================
# 📢 KIRIM NEWS KE DISCORD
# ============================================================

async def send_news(channel, news):

    title = news["title"]
    news_id = news["id"]

    logging.info(
        f"SEND_NEWS dipanggil | "
        f"News ID: {news_id} | "
        f"Title: {title} | "
        f"Channel: {channel.id}"
    )

    image = news["image"]

    news_url = f"https://umamusume.com/news/{news_id}/"

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

        timestamp=datetime.strptime(
            news["post_at"],
            "%Y-%m-%d %H:%M:%S"
        ).replace(
            tzinfo=timezone.utc
        )
    )

    embed.set_author(
        name="Diamond Fanmade • Official News"
    )

    embed.add_field(
        name="📝 Preview",
        value=create_preview(news["message"]),
        inline=False
    )

    period_text = format_periods(
        news["periods"]
    )

    if period_text:

        embed.add_field(
            name="⏰ Period",
            value=period_text,
            inline=False
        )

    embed.add_field(
        name="📂 Kategori",
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
        value=format_date(
            news["post_at"]
        ),

        inline=False
    )


    if image:

        embed.set_image(
            url=image
        )


    embed.set_footer(
        text="Diamond Fanmade • Timeline • Not affiliated with Cygames"
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


async def send_game8_update(channel):

    logging.info(
        "🎮 Mengambil data Game8..."
    )

    data = await asyncio.to_thread(
        get_game8_data
    )

    if not data or not data.get("guide_url"):

        logging.warning(
            "❌ Data Game8 kosong atau panduan belum tersedia."
        )

        return

    logging.info(
        f"✅ Data Game8 berhasil | "
        f"Cup: {data.get('current_cup')} | "
        f"Tier: {len(data.get('tier_characters', []))} | "
        f"Recommended: {len(data.get('recommended_characters', []))}"
    )

    embed = format_game8_message(
        data
    )

    await channel.send(
        embed=embed
    )

    logging.info(
        "📨 Pesan Game8 berhasil dikirim."
    )


def is_champions_meeting_news(news):

    title = news.get("title", "")
    title_lower = title.lower()

    keywords = [
        "is coming",
        "will begin",
        "will be held",
        "is here",
        "has begun",
        "have begun",
        "has started",
        "is now live",
        "now available"
    ]

    result = (
        "champions meeting" in title_lower
        and any(keyword in title_lower for keyword in keywords)
    )

    logging.info(
        f"CHECK CHAMPIONS MEETING | "
        f"Title: {title} | "
        f"Result: {result}"
    )

    return result


def _parse_period_dt(date_string):
    if not date_string:
        return None
    try:
        cleaned = (
            date_string
            .replace("a.m.", "AM")
            .replace("p.m.", "PM")
        )
        return datetime.strptime(
            cleaned,
            "%I:%M %p, %b %d, %Y (UTC)"
        )
    except ValueError:
        return None


def format_period_datetime(date_string):

    if not date_string:
        return None

    dt = _parse_period_dt(date_string)
    if dt:
        return dt.strftime("%d %b %H:%M UTC")

    return date_string


def format_periods(periods):

    if not periods:
        return None

    parsed_starts = []
    parsed_ends = []

    for p in periods:
        dt_start = _parse_period_dt(p.get("start"))
        if dt_start:
            parsed_starts.append(dt_start)
        dt_end = _parse_period_dt(p.get("end"))
        if dt_end:
            parsed_ends.append(dt_end)

    if parsed_starts and parsed_ends:
        start_str = min(parsed_starts).strftime("%d %b %H:%M UTC")
        end_str = max(parsed_ends).strftime("%d %b %H:%M UTC")
        return f"`{start_str}` → `{end_str}`"
    elif parsed_starts:
        start_str = min(parsed_starts).strftime("%d %b %H:%M UTC")
        return f"`{start_str}`"

    first = periods[0]
    last = periods[-1]

    start = format_period_datetime(
        first.get("start")
    )

    end = format_period_datetime(
        last.get("end")
    )

    if end:

        return (
            f"`{start}` → `{end}`"
        )

    return f"`{start}`"


def format_game8_message(data):

    embed = discord.Embed(
        title=f"🏆 {data.get('current_cup', 'Champions Meeting')}",
        color=discord.Color.from_str("#5865F2")
    )

    if data.get("guide_url"):
        embed.url = data["guide_url"]

    embed.set_author(
        name="Diamond Fanmade • Guide"
    )

    if data.get("map_url"):
        embed.set_image(
            url=data["map_url"]
        )

    stat_vals = data.get("stat_baselines", {}).get("values", {})
    embed.add_field(
        name="📊 Stat Baselines",
        value=(
            f"👟 **Speed:** {stat_vals.get('Speed', '-')}\n"
            f"❤️ **Stamina:** {stat_vals.get('Stamina', '-')}\n"
            f"💪 **Power:** {stat_vals.get('Power', '-')}\n"
            f"🔥 **Guts:** {stat_vals.get('Guts', '-')}\n"
            f"🧠 **Wit:** {stat_vals.get('Wit', '-')}"
        ),
        inline=False
    )

    race_conds = data.get("race_conditions", {})
    dist = race_conds.get("Distance", {})
    track = race_conds.get("Track", {})
    style = race_conds.get("Style", {})

    embed.add_field(
        name="🏁 Race Conditions",
        value=(
            f"📏 **Distance:** {dist.get('name', '-')} ({dist.get('rank', '-')})\n"
            f"🌱 **Track:** {track.get('name', '-')} ({track.get('rank', '-')})\n"
            f"🏇 **Style:** {style.get('name', '-')} ({style.get('rank', '-')})"
        ),
        inline=False
    )

    embed.add_field(
        name="🎯 Recommended Characters",
        value=(
            f"**{len(data.get('recommended_characters', []))}** characters"
        ),
        inline=True
    )

    embed.add_field(
        name="⭐ Tier Characters",
        value=(
            f"**{len(data.get('tier_characters', []))}** characters"
        ),
        inline=True
    )

    embed.set_footer(
        text="Diamond Fanmade • Timeline • Not affiliated with Cygames"
    )

    return embed


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
    initialize_baseline()

    logging.info(
        "Memulai monitoring..."
    )

    if not check_news.is_running():

        check_news.start()


# --------------------------------------------------------
# COMMAND ERROR
# --------------------------------------------------------

@bot.event
async def on_command_error(ctx, error):

    command_name = (
        ctx.message.content.split()[0]
        if ctx.message.content
        else "Unknown"
    )

    if isinstance(error, commands.CommandNotFound):

        await ctx.send(
            f"❌ Command `{command_name}` tidak ditemukan."
        )

        return

    if isinstance(error, commands.BadArgument):

        await ctx.send(
            "Salah Torena-san ❌. ID berita harus berupa angka.\n"
            "Dia kasih contoh ya : `!testnews 1023`"
        )

        return

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "🚫 Kamu tidak memiliki permission "
            "untuk menggunakan command ini."
        )

        return

    if isinstance(error, commands.NoPrivateMessage):

        await ctx.send(
            "🚫 Command ini hanya dapat digunakan "
            "di dalam server (bukan via DM)."
        )

        return

    if isinstance(error, commands.TooManyArguments):

        await ctx.send(
            "❌ Terlalu banyak argumen untuk command ini."
        )

        return

    logging.error(
        f"COMMAND ERROR | "
        f"Command: {ctx.command or command_name} | "
        f"Error: {type(error).__name__} | "
        f"Detail: {error}"
    )


# ============================================================
# ⏰ CHECK NEWS
# ============================================================

@tasks.loop(seconds=60)
async def check_news():

    global last_check
    global api_status

    last_check = datetime.now(timezone.utc)

    try:

        logging.info(
            "Mengecek Official Uma Musume News..."
        )

        news_list = await asyncio.to_thread(get_news)

        if news_list is None:

            api_status = False

            logging.warning(
                "News gagal diambil. Monitoring akan mencoba lagi nanti."
            )

            return

        api_status = True

        if database.guild_sent_news_corrupted:
        
            logging.warning(
                "Recovery mode aktif. Membuat baseline berita per server..."
            )

            for guild_id in guild_config:
            
                guild_sent_news[guild_id] = {
                    news["id"]
                    for news in news_list
                }

            save_guild_sent_news(
                guild_sent_news
            )

            database.guild_sent_news_corrupted = False

            logging.info(
                "Recovery selesai. Berita lama tidak dikirim."
            )

            return

        updated_guild_news = False

        # Urutkan secara kronologis (berita lebih lama diproses dulu) agar rapi di Discord
        for news in reversed(news_list):

            news_id = news["id"]

            # ------------------------------------------------
            # DATABASE GLOBAL SENT NEWS
            # ------------------------------------------------
            if news_id not in sent_news:
                sent_news.add(news_id)
                save_sent_news(sent_news)

            # ------------------------------------------------
            # KATEGORI BERITA
            # ------------------------------------------------

            category = get_category(
                news["title"],
                news["message"]
            )

            category_key = CATEGORY_KEY.get(
                category
            )

            if category_key is None:

                logging.warning(
                    f"Kategori tidak memiliki mapping: {category}"
                )

                continue

            # ------------------------------------------------
            # CEK SEMUA SERVER
            # ------------------------------------------------

            for guild_id, config in guild_config.items():

                # --------------------------------------------
                # DATABASE BERITA SERVER
                # --------------------------------------------

                if guild_id not in guild_sent_news:
                    # Inisialisasi tanpa news_id saat ini agar berita baru tetap terkirim
                    guild_sent_news[guild_id] = set(sent_news) - {news_id}
                    updated_guild_news = True

                if news_id in guild_sent_news[guild_id]:

                    continue

                # --------------------------------------------
                # CARI CHANNEL SESUAI KATEGORI
                # --------------------------------------------

                channel_id = config.get(
                    category_key
                )

                if channel_id is None:

                    log_key = (
                        guild_id,
                        news_id,
                        category_key
                    )

                    if log_key not in missing_channel_logged:

                        logging.warning(
                            f"Channel belum dikonfirmasi | "
                            f"Guild: {guild_id} | "
                            f"News ID: {news_id} | "
                            f"Kategori: {category_key} | "
                            f"Judul: {news['title']}"
                        )

                        missing_channel_logged.add(
                            log_key
                        )

                    guild_sent_news[guild_id].add(
                        news_id
                    )
                    updated_guild_news = True
                    continue

                channel = bot.get_channel(
                    channel_id
                )

                if channel is None:
                    try:
                        channel = await bot.fetch_channel(channel_id)
                    except Exception as fetch_err:
                        logging.warning(
                            f"Channel tidak ditemukan atau tidak dapat diakses "
                            f"untuk guild {guild_id} (id: {channel_id}): {fetch_err}"
                        )
                        continue

                send_key = (
                    guild_id,
                    news_id
                )
            
                if send_key in sending_news:
                    continue
            
                sending_news.add(
                    send_key
                )

                # --------------------------------------------
                # KIRIM BERITA
                # --------------------------------------------

                logging.info(
                    f"Mengirim berita ID {news_id} "
                    f"ke guild {guild_id} "
                    f"kategori {category_key}"
                )

                try:

                    await send_news(
                        channel,
                        news
                    )

                    # --------------------------------------------
                    # GAME8 CHAMPIONS MEETING
                    # --------------------------------------------

                    if is_champions_meeting_news(news):

                        logging.info(
                            f"🏆 Champions Meeting terdeteksi | "
                            f"News ID: {news_id}"
                        )

                        try:
                            await send_game8_update(
                                channel
                            )
                        except Exception as game8_error:
                            logging.error(
                                f"Gagal mengirim Game8 update ke guild {guild_id}: {game8_error}"
                            )

                    guild_sent_news[guild_id].add(
                        news_id
                    )
                    updated_guild_news = True

                except discord.Forbidden as error:

                    logging.error(
                        f"Permission Error "
                        f"guild {guild_id}: {error}"
                    )
                    # Tandai agar tidak loop spam error setiap 60 detik
                    guild_sent_news[guild_id].add(
                        news_id
                    )
                    updated_guild_news = True

                except discord.HTTPException as error:

                    logging.error(
                        f"Discord HTTP Error "
                        f"guild {guild_id}: {error}"
                    )

                finally:

                    sending_news.discard(
                        send_key

                    )

        if updated_guild_news:
            save_guild_sent_news(
                guild_sent_news
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

    guild_display = (
        ctx.guild.id
        if ctx.guild
        else "DM"
    )

    logging.info(
        f"HELP dipanggil | "
        f"Guild: {guild_display} | "
        f"User: {ctx.author.id} | "
        f"Message ID: {ctx.message.id}"
    )

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
        name="⚙️ !setchannel <kategori>",
        value=(
            "Mengatur channel untuk kategori berita.\n"
            "Contoh: `!setchannel gacha`"
        ),

        inline=False
    )

    embed.add_field(
        name="📋 !channels",
        value="Melihat konfigurasi channel server saat ini.",
        inline=False
    )  

    embed.add_field(
        name="🗑️ !removechannel <kategori>",
        value=(
            "Menghapus konfigurasi channel suatu kategori.\n"
            "Contoh: `!removechannel gacha`"
        ),
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

    embed.add_field(
        name="📖 !guide",
        value="Menampilkan daftar skill.",
        inline=False
    )

    embed.set_footer(
        text="Diamond Fanmade • Timeline • Not affiliated with Cygames "
    )

    logging.info(
        f"HELP mengirim embed | "
        f"Message ID: {ctx.message.id}"
    )

    await ctx.send(embed=embed)
    

@bot.command(name="testnews")
async def testnews(ctx, news_id: int = None):

    if news_id is None:
        await ctx.send(
            "Format command salah Torena-san `!testnews` ❌.\n\n"
            "Gunakan format ini :`!testnews <id>`\n"
            "Dia kasih contoh ya : `!testnews 1023` ✅"
        )
        return

    news_list = await asyncio.to_thread(get_news, 50)

    if not news_list:
        await ctx.send("❌ Tidak ada berita dari API.")
        return

    news = None

    for item in news_list:
        if item["id"] == news_id:
            news = item
            break

    if news is None:

        await ctx.send(
            f"❌ News ID `{news_id}` tidak ditemukan dalam 50 berita terakhir."
        )

        return


    await send_news(
        ctx.channel,
        news
    )

    if is_champions_meeting_news(news):

        logging.info(
            f"🏆 Champions Meeting terdeteksi | "
            f"News ID: {news_id}"
        )
        await send_game8_update(
            ctx.channel
        )


    logging.info(
        f"🧪 Test news dikirim: {news['title']}"
    )


@bot.command(name="latest")
async def latest(ctx):

    news_list = await asyncio.to_thread(get_news, 5)

    if not news_list:

        await ctx.send(
            "❌ Tidak ada berita dari API."
        )
        return

    news_items = []

    for index, news in enumerate(
        news_list,
        start=1
    ):

        status = get_status(
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

        period = format_periods(
            news["periods"]
        )

        news_item = (
            f"**{index}. [{news['title']}]"
            f"(https://umamusume.com/news/{news['id']}/)**\n"
            f"🆔 ID: `{news['id']}`\n\n"
            f"📂 Kategori: {category}\n\n"
            f"📊 Status: {status}\n\n"
            f"📅 Published: {published}"
        )

        if period:
            news_item += (
                f"\n\n⏰ Period: {period}"
            )

        news_items.append(
            news_item
        )

    embed = discord.Embed(
        title=f"📰 Latest {len(news_list)} Official News",
        description="\n\n────────────────────\n\n".join(
            news_items
        ),
        color=UMA_COLOR,
        timestamp=datetime.now(
            timezone.utc
        )
    )

    latest_image = news_list[0]["image"]

    if latest_image:
        embed.set_thumbnail(
            url=latest_image
        )

    embed.set_footer(
        text="Diamond Fanmade • Timeline • Not affiliated with Cygames "
    )

    await ctx.send(
        embed=embed
    )
    

@bot.command(name="status")
async def status(ctx):

    embed = discord.Embed(
        title="🤖 Bot Status",
        color=UMA_COLOR
    )

    embed.add_field(
        name="📊 Status",
        value="🟢 Online",
        inline=True
    )

    api_text = (
        "🟢 Online"
        if api_status
        else "🔴 Offline"
    )

    embed.add_field(
        name="🌐 API Status",
        value=api_text,
        inline=True
    )


    embed.add_field(
        name="📚 Known News",
        value=str(len(sent_news)),
        inline=False
    )

    guild_id = (
        str(ctx.guild.id)
        if ctx.guild
        else None
    )

    guild_news = (
        guild_sent_news.get(guild_id, set())
        if guild_id
        else set()
    )

    embed.add_field(
        name="📨 Sent to This Server",
        value=str(len(guild_news)) if guild_id else "N/A (DM)",
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
            (
                last_check.strftime(
                    "%d %B %Y • %H:%M:%S UTC"
                )
                + "\n" 
                + f"⏳ {format_time_ago(last_check)}"
            )
            if last_check
            else "Belum ada pengecekan"

        ),

        inline=False
    )

    await ctx.send(embed=embed)


@bot.command(name="stats")
async def stats(ctx):

    news_list = await asyncio.to_thread(
        get_news,
        50
    )

    if not news_list:

        await ctx.send(
            "❌ Tidak ada berita dari API."
        )

        return

    category_count = {}
    status_count = {}

    category_order = [ 
                "🏆 Champions Meeting",               
                "🏇 Legend Race",         
                "🎉 Event",   
                "🎟️ Gacha / Banner",
                "🎁 Campaign",
                "🔧 Game Update",
                "📰 Official News" 
            ]

    for news in news_list:

        category = get_category(
            news["title"],
            news["message"]
        )

        status = get_status(
            news["title"],
            news["message"]
        )

        category_count[category] = (
            category_count.get(category, 0) + 1
        )

        status_count[status] = (
            status_count.get(status, 0) + 1
        )

    embed = discord.Embed(
        title="📊 News Statistics",
        color=UMA_COLOR
    )

    embed.add_field(
        name="🔎 Analyzed",
        value=f"Latest {len(news_list)} official news",
        inline=False
    )

    category_text = ""

    for category in category_order:

        count = category_count.get(
            category,
            0
        )

        category_text += (
            f"{category} — **{count}**\n\n"
        )

    embed.add_field(
        name="📂 Category Distribution",
        value=category_text,
        inline=False
    )

    status_text = ""

    for status, count in status_count.items():

        status_text += (
            f"{status} — **{count}**\n\n"
        )

    embed.add_field(
        name="📊 Status Distribution",
        value=status_text,
        inline=False
    )

    await ctx.send(
        embed=embed
    )


@bot.command(name="channels")
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def channels(ctx):

    guild_id = str(ctx.guild.id)

    config = guild_config.get(
        guild_id,
        {}
    )

    total_channels = len(
        CHANNEL_CATEGORY
    )

    configured_channels = sum(
        1
        for category in CHANNEL_CATEGORY
        if config.get(category) is not None
    )

    embed = discord.Embed(
        title="⚙️ Channel Configuration",
        description=(
            f"Konfigurasi channel untuk "
            f"**{ctx.guild.name}**\n\n"
        ),
        color=UMA_COLOR
    )

    embed.add_field( 
        name="⚙️ Configured",
        value=( 
            f"**{configured_channels}/{total_channels}** "
            f"channels" 
        ), 
        inline=False 
    )

    for category, category_name in CHANNEL_CATEGORY.items():

        channel_id = config.get(
            category
        )

        if channel_id is None:

            channel_text = "❌ Belum dikonfigurasi"

        else:

            channel = bot.get_channel(
                channel_id
            )

            if channel is None:

                channel_text = (
                    f"⚠️ Channel tidak ditemukan "
                    f"(`{channel_id}`)"
                )

            else:

                channel_text = channel.mention

        embed.add_field(
            name=category_name,
            value=channel_text,
            inline=True
        )

    embed.set_footer(
        text="Diamond Fanmade • Timeline • Not affiliated with Cygames"
    )

    await ctx.send(
        embed=embed
    )


@bot.command(name="setchannel")
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def setchannel(ctx, category=None, channel: discord.TextChannel = None):

    if category is None:

        await ctx.send(
            "❌ Gunakan: `!setchannel <kategori> [channel]`\n\n"
            "Kategori yang tersedia:\n"
            "`gacha`\n"
            "`champions`\n"
            "`legend`\n"
            "`campaign`\n"
            "`event`\n"
            "`update`\n"
            "`news`\n\n"
            "Contoh:\n"
            "`!setchannel gacha` (menggunakan channel ini)\n"
            "`!setchannel gacha #berita-gacha`"
        )

        return

    category = category.lower()

    if category not in CHANNEL_CATEGORY:

        await ctx.send(
            "❌ Kategori tidak ditemukan.\n"
            "Gunakan `!setchannel` untuk melihat daftar kategori."
        )

        return

    target_channel = channel or ctx.channel
    guild_id = str(ctx.guild.id)
    channel_id = target_channel.id

    if guild_id not in guild_config:
        guild_config[guild_id] = {}

    if guild_id not in guild_sent_news:

        guild_sent_news[guild_id] = set(sent_news)

        save_guild_sent_news(
            guild_sent_news
        )

    guild_config[guild_id][category] = channel_id

    save_guild_config(
        guild_config
    )

    category_name = CHANNEL_CATEGORY[category]

    total_channels = len(
        CHANNEL_CATEGORY
    )

    configured_channels = sum(
        1
        for configured_category in CHANNEL_CATEGORY
        if guild_config[guild_id].get(
            configured_category
        ) is not None
    )

    await ctx.send(
        f"✅ Channel berhasil disimpan!\n\n"
        f"📂 Kategori: **{category_name}**\n"
        f"📢 Channel: {target_channel.mention}\n\n"
        f"⚙️ Configuration: "
        f"**{configured_channels}/{total_channels} channels**"
    )


@bot.command(name="removechannel")
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def removechannel(ctx, category=None):

    if category is None:

        await ctx.send(
            "❌ Gunakan: `!removechannel <kategori>`\n\n"
            "Contoh: `!removechannel gacha`"
        )

        return

    category = category.lower()

    if category not in CHANNEL_CATEGORY:

        await ctx.send(
            "❌ Kategori tidak ditemukan.\n"
            "Gunakan kategori yang tersedia."
        )

        return

    guild_id = str(ctx.guild.id)

    config = guild_config.get(
        guild_id
    )

    if config is None:
        await ctx.send(
            "❌ Server ini belum memiliki konfigurasi channel."
        )

        return

    if category not in config:

        await ctx.send(
            f"❌ Kategori **{CHANNEL_CATEGORY[category]}** "
            "belum memiliki channel."
        )

        return

    del config[category]

    save_guild_config(
        guild_config
    )

    total_channels = len(
        CHANNEL_CATEGORY
    )

    configured_channels = sum(
        1
        for configured_category in CHANNEL_CATEGORY
        if guild_config[guild_id].get(
            configured_category
        ) is not None
    )

    await ctx.send(
        f"🗑️ Konfigurasi channel berhasil dihapus!\n\n"
        f"📂 Kategori: **{CHANNEL_CATEGORY[category]}**\n\n"
        f"⚙️ Configuration: "
        f"**{configured_channels}/{total_channels} channels**"
    )


@bot.command(name="guide")
async def guide(ctx):

    logging.info(
        f"📖 !guide dipanggil | "
        f"User: {ctx.author} | "
        f"Guild: {ctx.guild}"
    )

    async with ctx.typing():
        data = await asyncio.to_thread(
            get_game8_data
        )

    if not data or not data.get("guide_url"):
        await ctx.send(
            "❌ Data Game8 tidak berhasil diambil atau "
            "panduan turnamen ini belum tersedia."
        )
        return

    embed = format_guide_overview(data)

    await ctx.send(
        embed=embed,
        view=GuideView(data)
    )


# ============================================================
# ▶️ START BOT
# ============================================================

if __name__ == "__main__":

    if not TOKEN:

        raise RuntimeError(
            "DISCORD_TOKEN belum ditemukan di .env"
        )

    bot.run(TOKEN)