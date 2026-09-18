import json
import os
import logging


# ============================== 
# Database Paths 
# ==============================

FILE_PATH = "data/sent_news.json"
GUILD_CONFIG_PATH = "data/guild_config.json"
GUILD_SENT_NEWS_PATH = "data/guild_sent_news.json"


# ============================== 
# Global Sent News 
# ==============================

def load_sent_news():

    if not os.path.exists(FILE_PATH):

        logging.info(
            "File sent_news belum ada. Menggunakan database Kosong ."
        )

        return set()

    with open(FILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return set(data)


def save_sent_news(sent_news):

    os.makedirs("data", exist_ok=True)

    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(
            list(sent_news),
            file,
            ensure_ascii=False,
            indent=2
        )

    logging.info(
        f"Database saved. Total known news: {len(sent_news)}"
    )


# ============================== 
# Guild Configuration 
# ==============================

def load_guild_config():

    if not os.path.exists(GUILD_CONFIG_PATH):

        logging.info(
            "File guild_config belum ada. Menggunakan konfigurasi kosong."
        )

        return {}

    with open(
        GUILD_CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_guild_config(config):

    os.makedirs("data", exist_ok=True)

    with open(
        GUILD_CONFIG_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            config,
            file,
            ensure_ascii=False,
            indent=2
        )

    logging.info(
        "Konfigurasi server berhasil disimpan."
    )


# ============================== 
# Guild Sent News 
# ==============================

def load_guild_sent_news():

    if not os.path.exists(GUILD_SENT_NEWS_PATH):

        logging.info(
            "File guild_sent_news belum ada. Menggunakan database kosong."
        )

        return {}

    with open(
        GUILD_SENT_NEWS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return {
        guild_id: set(news_ids)
        for guild_id, news_ids in data.items()
    }


def save_guild_sent_news(guild_sent_news):

    os.makedirs("data", exist_ok=True)

    data = {
        guild_id: list(news_ids)
        for guild_id, news_ids in guild_sent_news.items()
    }

    with open(
        GUILD_SENT_NEWS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    logging.info(
        "Database berita per server berhasil disimpan."
    )