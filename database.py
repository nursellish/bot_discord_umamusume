import json
import os
import time
import logging


# ============================== 
# Database Paths 
# ==============================

guild_sent_news_corrupted = False
FILE_PATH = "data/sent_news.json"
GUILD_CONFIG_PATH = "data/guild_config.json"
GUILD_SENT_NEWS_PATH = "data/guild_sent_news.json"


def _atomic_json_dump(file_path, data):
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    temp_path = f"{file_path}.{os.getpid()}.tmp"
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    # Retry jika file terkunci sementara oleh Windows / OneDrive / Antivirus
    for attempt in range(8):
        try:
            os.replace(temp_path, file_path)
            return
        except PermissionError:
            if attempt == 7:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
                raise
            time.sleep(0.15)
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise


# ============================== 
# Global Sent News 
# ==============================

def load_sent_news():

    if not os.path.exists(FILE_PATH):

        logging.info(
            "File sent_news belum ada. Menggunakan database Kosong ."
        )

        return set()

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, (list, set, tuple)):
            logging.warning("Data sent_news tidak berbentuk list. Menggunakan database kosong.")
            return set()
        return set(data)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        logging.error(
            f"Database sent_news rusak: {error}. Menggunakan database kosong."
        )
        return set()


def save_sent_news(sent_news):

    _atomic_json_dump(FILE_PATH, list(sent_news))

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

    try:
        with open(
            GUILD_CONFIG_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)
            if not isinstance(data, dict):
                logging.error("Data guild_config bukan dict. Menggunakan konfigurasi kosong.")
                return {}
            return data
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        logging.error(
            f"Database guild_config rusak: {error}. Menggunakan konfigurasi kosong."
        )
        return {}


def save_guild_config(config):

    _atomic_json_dump(GUILD_CONFIG_PATH, config)

    logging.info(
        "Konfigurasi server berhasil disimpan."
    )


# ============================== 
# Guild Sent News 
# ==============================

def load_guild_sent_news():

    global guild_sent_news_corrupted

    if not os.path.exists(GUILD_SENT_NEWS_PATH):
        logging.info(
            "File guild_sent_news belum ada. Menggunakan database kosong."
        )
        return {}
    
    try:
        with open(
            GUILD_SENT_NEWS_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

    except (json.JSONDecodeError, TypeError, ValueError) as error:
        guild_sent_news_corrupted = True

        logging.error(
            f"Database guild_sent_news rusak: {error}"
        )
        logging.warning(
            "Menggunakan database guild_sent_news kosong."
        )
        return {}

    if not isinstance(data, dict):
        guild_sent_news_corrupted = True
        logging.warning("Data guild_sent_news bukan dict. Masuk recovery mode.")
        return {}

    result = {}
    for guild_id, news_ids in data.items():
        if isinstance(news_ids, (list, set, tuple)):
            result[str(guild_id)] = set(news_ids)
        else:
            result[str(guild_id)] = set()

    return result


def save_guild_sent_news(guild_sent_news):

    data = {
        guild_id: list(news_ids)
        for guild_id, news_ids in guild_sent_news.items()
    }

    _atomic_json_dump(GUILD_SENT_NEWS_PATH, data)

    logging.info(
        "Database berita per server berhasil disimpan."
    )