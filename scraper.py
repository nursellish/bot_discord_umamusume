import requests
import logging

from bs4 import BeautifulSoup


# ============================================================
# 🌐 OFFICIAL UMA MUSUME NEWS API
# ============================================================

NEWS_URL = "https://umamusume.com/api/ajax/pr_info_index?format=json"


def clean_message(message):

    soup = BeautifulSoup(
        message,
        "html.parser"
    )

    return soup.get_text(
        "\n",
        strip=True
    )


def create_preview(message):

    max_length = 500

    if len(message) <= max_length:
        return message

    return message[:max_length] + "..."


def get_news(limit=10):

    data = {
        "announce_label": 0,
        "limit": limit,
        "offset": 0
    }
    try:

        response = requests.post(
            NEWS_URL,
            json=data,
            timeout=20
        )
    except requests.exceptions.RequestException as error:

        logging.error(
            f"HTTP Error: {error}"
        )

        return None

    except requests.exceptions.RequestException as error:

        logging.error(
            f"Network Error: {error}"
        )

        return None


    logging.info(
        f"STATUS API: {response.status_code}"
    )

    response.raise_for_status()

    data = response.json()

    news_list = []

    for news in data["information_list"]:

        item = {
            "id": news["announce_id"],
            "title": news["title"],
            "message": create_preview(
                clean_message(news["message"])
            ),
            "label": news["announce_label"],
            "post_at": news["post_at"],
            "image": news["image"]
        }

        news_list.append(item)

    return news_list

if __name__ == "__main__":

    news_list = get_news()

    print("Jumlah berita:", len(news_list))

    for news in news_list:

        print("ID:", news["id"])
        print("TITLE:", news["title"])
        print("LABEL:", news["label"])
        print("MESSAGE:")
        print(news["message"][:500])
        print("-" * 50)