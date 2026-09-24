import requests
import logging
import re

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


def extract_periods(message):

    lines = message.splitlines()

    periods = []

    current_label = None
    pending_label = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line.lower().endswith(
            ("period", "periods")
        ):

            current_label = line
            pending_label = None
            continue

        if line.startswith("•"):
            pending_label = None
            continue

        if current_label is not None:

            if (             
                "–" in line
                or " - " in line
            ):

                 # Pisahkan bagian awal dan akhir
                if "–" in line:
                    start_text, end_text = line.split(
                        "–",
                        1
                    )
                else:
                    start_text, end_text = line.split(
                        " - ",
                        1
                    )

                start_text = start_text.strip()
                end_text = end_text.strip()

                 # Cek apakah kedua sisi memiliki tanggal
                has_start_date = bool(
                    re.search(
                        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}",
                        start_text
                    )
                )

                has_end_date = bool(
                    re.search(
                        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}",
                        end_text
                    )
                )

                if has_start_date and has_end_date:

                    label = (
                        pending_label
                        if pending_label is not None
                        else current_label
                    )

                    periods.append({
                        "label": label,
                        "period": line
                    })

                    pending_label = None

                    continue

            pending_label = line
       
    return periods


def parse_period(period_text):

    period_text = period_text.strip()

    en_dash = chr(8211)

    if en_dash in period_text:

        start_text, end_text = period_text.split(
            en_dash,
            1
        )

    elif " - " in period_text:

        start_text, end_text = period_text.split(
            " - ",
            1
        )

    else:

        return {
            "start": period_text,
            "end": None
        }

    start_text = start_text.strip()
    end_text = end_text.strip()

    if "," in end_text:

        end_parts = end_text.split(",")

        if len(end_parts) >= 3:

            year_timezone = ",".join(
                end_parts[2:]
            ).strip()

            start_text = (
                f"{start_text}, "
                f"{year_timezone}"
            )

    return {
        "start": start_text.strip(),
        "end": end_text.strip()
    }


def create_preview(message):

    max_length = 500

    if len(message) <= max_length:
        return message

    lines = message.splitlines()

    preview = ""

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line.lower().endswith(
            ("period", "periods")
        ):
            break

        if len(preview) + len(line) + 1 > max_length:
            break

        if preview:
            preview += "\n"

        preview += line

    if not preview:
        return "No preview available." 

    if len(preview) < len(message):
        preview += "..."

    return preview


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

        response.raise_for_status()

    except requests.exceptions.RequestException as error:

        logging.error(
            f"Request Error: {error}"
        )

        return None

    logging.info(
        f"STATUS API: {response.status_code}"
    )


    data = response.json()

    news_list = []

    for news in data["information_list"]:

        cleaned_message = clean_message(
            news["message"]
        )

        periods = extract_periods(
            cleaned_message
        )

        parsed_periods = []

        for period in periods:

            parsed = parse_period(
                period["period"]
                
            )

            parsed_periods.append({
                "label": period["label"],
                "start": parsed["start"],
                "end": parsed["end"]
            })

        item = {
            "id": news["announce_id"],
            "title": news["title"],
            "message": cleaned_message,
            "label": news["announce_label"],
            "post_at": news["post_at"],
            "image": news["image"],
            "periods": parsed_periods
        }

        news_list.append(item)

    return news_list


if __name__ == "__main__":

    news_list = get_news(limit=50)

    print("Jumlah berita:", len(news_list))

    for news in news_list:

        print(
            f"ID: {news['id']} | "
            f"{news['title']} | "
            f"Periods: {len(news['periods'])}"
        )
