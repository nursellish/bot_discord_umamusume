import json
import os
import logging

FILE_PATH = "data/sent_news.json"


def load_sent_news():

    if not os.path.exists(FILE_PATH):

        logging.info(
            "File sent_news belum ada. Menggunakan database Kosong."
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