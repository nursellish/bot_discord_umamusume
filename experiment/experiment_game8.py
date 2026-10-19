import requests
from scraper import get_news
from bs4 import BeautifulSoup

GUIDE_URL = "https://game8.co/games/Umamusume-Pretty-Derby/archives/616645"



guide_response = requests.get(
    GUIDE_URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=20
)


print( 
    "GUIDE STATUS:", 
    guide_response.status_code 
)

guide_soup = BeautifulSoup(
    guide_response.text,
    "html.parser"
)

print( 
    "GUID TITLE:",
    guide_soup.title.get_text(strip=True)

) 

# -----------------------------------------------------------

print("\nHEADING:")

for heading in guide_soup.find_all(
    ["h2", "h3"]
):
    
    text = heading.get_text(
        " ", strip=True 
    ) 
    if text: 

        print( 
            text )


print("\nMAP IMAGES:")

for image in guide_soup.find_all(
    "img"
):

    alt = image.get(
        "alt",
        ""
    )

    src = image.get(
        "src",
        ""
    )

    if (
        "Scorpio" in alt
        or "Course" in alt
        or "Map" in alt
    ):

        print(
            "ALT:",
            alt
        )

        print(
            "SRC:",
            src
        )

        print("-" * 50)

# ----------------------------------------------------------

print("\nMAP IMAGE ATTRIBUTES:")

for image in guide_soup.find_all(
    "img"
):

    alt = image.get(
        "alt",
        ""
    )

    if alt == "CM19 New Map":

        print(
            image.attrs
        )

# ---------------------------------------------------------

links = guide_soup.find_all( "a", href=True )

print("\nCM GUIDE CANDIDATES:")

for link in links:

    text = link.get_text(
        " ",
        strip=True
    )

    href = link.get(
        "href",
        ""
    )

    if (
        "Champions Meeting" in text
        and "Umamusume-Pretty-Derby" in href
        and "(CM" in text
    ):

        cup_name = text.split(
            "(CM",
            1
        )[0].strip()

        print(
            "CUP:",
            cup_name
        )

        print(
            "TEXT:",
            text
        )

        print(
            "URL:",
            href
        )

        print("-" * 50)

# --------------------------------------------------------------

print("\nCHAMPIONS MEETING NEWS:")

news_list = get_news(
    limit=50
)

for news in news_list:

    title = news["title"]

    if "Champions Meeting" in title:

        print(
            "TITLE:",
            title
        )

        print(
            "ID:",
            news["id"]
        )

        print("-" * 50)

# ------------------------------------------------------------

print("\nEXTRACTED CUP:")

for news in news_list:

    title = news["title"]

    if (
        "The race event Champions Meeting:" in title
        and "is here!" in title
    ):

        cup_name = title.split(
            "Champions Meeting:",
            1
        )[1].strip()

        cup_name = cup_name.replace(
            " is here!",
            ""
        )

        print(
            "TITLE:",
            title
        )

        print(
            "CUP:",
            cup_name
        )

        print("-" * 50)

# ---------------------------------------------------------

print("\nMATCHING RESULT:")

game8_guides = {}

for link in links:

    text = link.get_text(
        " ",
        strip=True
    )

    href = link.get(
        "href",
        ""
    )

    if (
        "Champions Meeting" in text
        and "Umamusume-Pretty-Derby" in href
        and "(CM" in text
    ):

        cup_name = text.split(
            "(CM",
            1
        )[0].strip()

        game8_guides[cup_name] = href


for news in news_list:

    title = news["title"]

    if (
        "The race event Champions Meeting:" in title
        and "is here!" in title
    ):

        cup_name = title.split(
            "Champions Meeting:",
            1
        )[1].strip()

        cup_name = cup_name.replace(
            " is here!",
            ""
        )

        guide_url = game8_guides.get(
            cup_name
        )

        print(
            "CUP:",
            cup_name
        )

        print(
            "GAME8:",
            guide_url
        )

        print("-" * 50)



        if guide_url:
        
            if guide_url.startswith("/"):
                guide_url = (
                    "https://game8.co"
                    + guide_url
                )

            guide_response = requests.get(
                guide_url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=20
            )

            print(
                "\nGUIDE STATUS:",
                guide_response.status_code
            )

            guide_soup = BeautifulSoup(
                guide_response.text,
                "html.parser"
            )

            for image in guide_soup.find_all(
                "img"
            ):

                alt = image.get(
                    "alt",
                    ""
                )

                if "New Map" in alt:
                
                    map_url = image.get(
                        "data-src"
                    )

                    print(
                        "MAP ALT:",
                        alt
                    )

                    print(
                        "MAP URL:",
                        map_url
                    )

# -----------------------------------------------------------

print("\nTIER LIST:")

for heading in guide_soup.find_all(
    ["h2", "h3"]
):

    text = heading.get_text(
        " ",
        strip=True
    )

    if "Tier List" in text:

        print(
            "HEADING:",
            text
        )

        print(
            "TAG:",
            heading.name
        )

        print(
            "HTML:"
        )

        print(
            heading.parent.prettify()[:5000]
        )

        break

# ---------------------------------------------------------

print("\nBEST CHARACTERS:")

best_characters = guide_soup.find(
    id="hl_2"
)

if best_characters:

    print(
        "TAG:",
        best_characters.name
    )

    print(
        "TEXT:",
        best_characters.get_text(
            " ",
            strip=True
        )
    )

    print(
        "HTML:"
    )

    print(
        best_characters.parent.prettify()[:8000]
    )

else:

    print(
        "Best Characters tidak ditemukan."
    )


# ----------------------------------------------------------

print("\nBEST CHARACTERS SECTION:")

best_heading = guide_soup.find(
    id="hl_2"
)

next_heading = guide_soup.find(
    id="hl_3"
)

if best_heading and next_heading:

    current = best_heading.find_next()

    while current and current != next_heading:

        if current.name in [
            "h3",
            "table",
            "ul",
            "ol",
            "div"
        ]:

            text = current.get_text(
                " ",
                strip=True
            )

            if text:

                print(
                    "TAG:",
                    current.name
                )

                print(
                    "CLASS:",
                    current.get("class")
                )

                print(
                    "TEXT:",
                    text[:500]
                )

                print("-" * 50)

        current = current.find_next()

else:

    print(
        "Section Best Characters tidak ditemukan."
    )

# ----------------------------------------------------------

print("\nTIER LIST TABLE:")

tier_heading = guide_soup.find(
    string=lambda text: (
        text
        and "Scorpio Cup (CM19) Tier List" in text
    )
)

if tier_heading:

    tier_h3 = tier_heading.find_parent("h3")

    tier_table = tier_h3.find_next(
        "table"
    )

    if tier_table:

        print(
            tier_table.prettify()[:12000]
        )

    else:

        print(
            "Tier List table tidak ditemukan."
        )

else:

    print(
        "Heading Tier List tidak ditemukan."
    )


# --------------------------------------------------------

print("\nTIER LIST DATA:")

if tier_table:

    rows = tier_table.find_all(
        "tr"
    )

    for row in rows:

        cells = row.find_all(
            ["th", "td"]
        )

        if len(cells) != 2:
            continue

        rank_img = cells[0].find(
            "img"
        )

        if not rank_img:
            continue

        rank = rank_img.get(
            "alt"
        )

        characters = []

        for img in cells[1].find_all(
            "img"
        ):

            character = img.get(
                "alt"
            )

            if character:
                characters.append(
                    character
                )

        print(
            "RANK:",
            rank
        )

        for character in characters:

            print(
                " -",
                character
            )

        print("-" * 50)

# ------------------------------------------------------------

print("\nFULL CHARACTER NAMES:")

for row in tier_table.find_all("tr"):

    cells = row.find_all(
        ["th", "td"]
    )

    if len(cells) != 2:
        continue

    rank_img = cells[0].find("img")

    if not rank_img:
        continue

    rank = rank_img.get("alt")

    print("RANK:", rank)

    for template in cells[1].find_all(
        "template",
        class_="js-tooltip-content"
    ):

        text = template.get_text(
            " ",
            strip=True
        )

        rarity = None

        if "Rarity :" in text:

            name, rarity = text.rsplit(
                "Rarity :",
                1
            )

            name = name.strip()
            rarity = rarity.strip()

        else:

            name = text

        print(
            "NAME:",
            name
        )

        print(
            "RARITY:",
            rarity
        )

        print("-" * 30)


print("\nCHARACTER IMAGE + URL:")

for row in tier_table.find_all("tr"):

    cells = row.find_all(
        ["th", "td"]
    )

    if len(cells) != 2:
        continue

    rank_img = cells[0].find("img")

    if not rank_img:
        continue

    rank = rank_img.get("alt")

    for link in cells[1].find_all(
        "a",
        href=True
    ):

        template = link.find(
            "template",
            class_="js-tooltip-content"
        )

        img = link.find("img")

        if not template or not img:
            continue

        text = template.get_text(
            " ",
            strip=True
        )

        if "Rarity :" in text:

            name, rarity = text.rsplit(
                "Rarity :",
                1
            )

            name = name.strip()
            rarity = rarity.strip()

        else:

            name = text
            rarity = None

        character_url = link.get(
            "href"
        )

        image_url = img.get(
            "data-src"
        )

        print("RANK:", rank)
        print("NAME:", name)
        print("RARITY:", rarity)
        print("IMAGE:", image_url)
        print("URL:", character_url)
        print("-" * 50)

# --------------------------------------------------------

print("\nRECOMMENDED CHARACTERS TABLE:")

recommended_heading = guide_soup.find(
    string=lambda text: (
        text
        and "Scorpio Cup (CM19) Recommended Characters" in text
    )
)

if recommended_heading:

    recommended_h3 = recommended_heading.find_parent(
        "h3"
    )

    recommended_table = recommended_h3.find_next(
        "table"
    )

    if recommended_table:

        print(
            recommended_table.prettify()[:12000]
        )

    else:

        print(
            "Recommended Characters table tidak ditemukan."
        )

else:

    print(
        "Heading Recommended Characters tidak ditemukan."
    )

# ---------------------------------------------------------

print("\n=== stat table guidline =======")
stat_heading = guide_soup.find(
    "h2",
    string=lambda text: (
        text
        and "Scorpio Cup (CM19) Stat Guidelines" in text
    )
)

if stat_heading:

    print("\nSTAT SECTION:")
    current = stat_heading
    for _ in range(5):
        current = current.find_next()
        if not current:
            break
        print(
            "TAG:",
            current.name
        )
        print(
            "TEXT:",
            current.get_text(
                " ",
                strip=True
            )[:500]
        )
        print("-" * 50)

# ----------------------------------------------------------

print("\n=== STAT TABLE STRUCTURE ===")

stat_heading = guide_soup.find(
    "h2",
    string=lambda text: (
        text
        and "Scorpio Cup (CM19) Stat Guidelines" in text
    )
)

if stat_heading:

    stat_table = stat_heading.find_next("table")

    if stat_table:

        for row in stat_table.find_all("tr"):

            print("\nROW")

            for cell in row.find_all(["th", "td"]):

                print(
                    "TAG:",
                    cell.name
                )

                print(
                    "TEXT:",
                    cell.get_text(
                        " ",
                        strip=True
                    )
                )

                print("-" * 30)

                print("\n=== STAT TABLE HTML ===")

                print(
                    stat_table.prettify()[:15000]
                )

    else:

        print("TABLE TIDAK DITEMUKAN")

else:

    print("HEADING TIDAK DITEMUKAN")


# ----------------------------------------------------

print("\nRUNNING STYLE CHECK:")

for row in recommended_table.find_all("tr"):

    cells = row.find_all("td")

    if len(cells) != 2:
        continue

    character = cells[0].get_text(
        " ",
        strip=True
    )

    key_points = cells[1]

    styles = []

    for image in key_points.find_all("img"):

        alt = image.get("alt")

        if alt:
            styles.append(alt)

    print(
        character,
        "=>",
        styles
    )

 
for row in recommended_table.find_all("tr"):

    character = row.find("a")

    if not character:
        continue

    character_name = character.get_text(
        " ",
        strip=True
    )

    if character_name == "T.M. Opera O (New Year, Same Radiance!)":

        print("\nT.M. OPERA O HTML:")

        print(
            row.find_all("td")[1].prettify()
        )

#--------------------------------------------------


# --------------------------------------------------

print("\n=== RECOMMENDED SKILLS ===")

skill_heading = guide_soup.find(
    "h2",
    string=lambda text: (
        text
        and "Scorpio Cup (CM19) Recommended Skills" in text
    )
)

if skill_heading:

    skill_section = skill_heading.find_next("table")

    if skill_section:

        print(
            skill_section.prettify()[:15000]
        )

    else:

        print("TABLE TIDAK DITEMUKAN")

else:

    print("HEADING TIDAK DITEMUKAN")


# # ------------------------------------------

print("\n=== GREEN SKILLS ===")

green_anchor = guide_soup.find(
    id="hm_301"
)

if green_anchor:

    print(
        green_anchor.parent.prettify()[:15000]
    )

else:

    print("ANCHOR GREEN SKILLS TIDAK DITEMUKAN")

# ----------------------------------------------------------

print("\n=== GREEN ANCHOR ===")

green_anchor = guide_soup.find(
    id="hm_301"
)

if green_anchor:

    print(
        "TAG:",
        green_anchor.name
    )

    print(
        "ID:",
        green_anchor.get("id")
    )

    print(
        "TEXT:",
        green_anchor.get_text(
            " ",
            strip=True
        )
    )

    print(
        "HTML:"
    )

    print(
        green_anchor.prettify()[:5000]
    )

else:

    print(
        "ANCHOR GREEN SKILLS TIDAK DITEMUKAN"
    )


# ----------------------------------------------------------

print("\n=== GREEN SKILLS STRUCTURE ===")

green_heading = guide_soup.find(
    "h3",
    id="hm_301"
)

if green_heading:

    current = green_heading

    for _ in range(8):

        current = current.find_next()

        if not current:
            break

        print(
            "TAG:",
            current.name
        )

        print(
            "TEXT:",
            current.get_text(
                " ",
                strip=True
            )[:500]
        )

        print("-" * 50)

else:

    print(
        "GREEN HEADING TIDAK DITEMUKAN"
    )

# ----------------------------------------------------------

print("\n=== FIRST GREEN SKILL ===")

green_table = green_heading.find_next("table")

if green_table:

    first_skill = green_table.find(
        "a",
        string=lambda text: (
            text
            and "Right-Handed" in text
        )
    )

    first_skill = None

    for link in green_table.find_all(
        "a",
        href=True
    ):

        text = link.get_text(
            " ",
            strip=True
        )

        if "Right-Handed" in text:

            first_skill = link

            break


    if first_skill:

        print(
            first_skill.parent.prettify()
        )

    else:

        print(
            "RIGHT-HANDED TIDAK DITEMUKAN"
        )

# ---------------------------------------------------------

print("\n=== GREEN SKILLS TD ===")

green_td = green_table.find("td")

if green_td:

    print(
        green_td.prettify()[:12000]
    )

else:

    print(
        "TD GREEN SKILLS TIDAK DITEMUKAN"
    )

# # ---------------------------------------------------------

accel_heading = guide_soup.find(
    "h3",
    id="hm_302"
)

if accel_heading:

    accel_table = accel_heading.find_next("table")

    if accel_table:

        print("\n=== ACCELERATION SKILLS TABLE ===")

        print(
            accel_table.prettify()[:12000]
        )

        print(
            "\n=== ACCELERATION TABLE BOTTOM ==="
        )

        print(
            accel_table.prettify()[-12000:]
        )

# ------------------------------------------------------------

speed_heading = guide_soup.find(
    "h3",
    id="hm_303"
)

if speed_heading:

    speed_table = speed_heading.find_next("table")

    if speed_table:

        print("\n=== SPEED SKILLS TABLE ===")

        print(
            speed_table.prettify()[:12000]
        )

        print(
            "\n=== SPEED TABLE BOTTOM ==="
        )

        print(
            speed_table.prettify()[-12000:]
        )

# ---------------------------------------------------------

recovery_heading = guide_soup.find(
    "h3",
    id="hm_304"
)

if recovery_heading:

    recovery_table = recovery_heading.find_next("table")

    if recovery_table:

        print("\n=== RECOVERY SKILLS TABLE ===")

        print(
            recovery_table.prettify()[12000:24000]
        )

#------------------------------------------------------------ 

debuff_heading = guide_soup.find(
    "h3",
    id="hm_305"
)

if debuff_heading:

    debuff_table = debuff_heading.find_next("table")

    if debuff_table:

        print("\n=== DEBUFF SKILLS TABLE ===")

        print(
            debuff_table.prettify()[:12000]
        )

# -----------------------------------------------------------

support_heading = guide_soup.find(
    "h2",
    string=lambda text: (
        text
        and "Scorpio Cup (CM19) Support Cards" in text
    )
)

if support_heading:

    support_table = support_heading.find_next("table")

    if support_table:

        print("\n=== SUPPORT CARDS TABLE ===")

        print(
            support_table.prettify()[:12000]
        )


support_heading = guide_soup.find(
    "h3",
    id="hm_501"
)

if support_heading:

    support_table = support_heading.find_next("table")

    if support_table:

        print("\n=== RECOMMENDED SUPPORT CARDS TABLE ===")

        print(
            support_table.prettify()[36000:48000]
        )

# -----------------------------------------------------------

print("\nOGURI CAP KEY POINTS:")

for row in recommended_table.find_all("tr"):

    character = row.find("a")

    if not character:
        continue

    character_name = character.get_text(
        " ",
        strip=True
    )

    if character_name == "Oguri Cap (Ashen Miracle)":

        key_points_cell = row.find_all("td")[1]

        for element in key_points_cell.contents:

            if getattr(element, "name", None):

                print(
                    "TAG:",
                    element.name
                )

                print(
                    "TEXT:",
                    element.get_text(
                        " ",
                        strip=True
                    )
                )

            else:

                text = str(element).strip()

                if text:

                    print(
                        "TEXT:",
                        text
                    )



print("\nKEY POINTS STRUCTURE CHECK:")

for row in recommended_table.find_all("tr"):

    cells = row.find_all("td")

    if len(cells) != 2:
        continue

    character = cells[0].get_text(
        " ",
        strip=True
    )

    key_points = cells[1]

    br_count = len(
        key_points.find_all("br")
    )

    print(
        character,
        "=>",
        br_count,
        "BR"
    )


print("\nOGURI CAP FULL STRUCTURE:")

for row in recommended_table.find_all("tr"):

    character = row.find("a")

    if not character:
        continue

    character_name = character.get_text(
        " ",
        strip=True
    )

    if character_name == "Oguri Cap (Ashen Miracle)":

        key_points_cell = row.find_all("td")[1]

        for index, element in enumerate(
            key_points_cell.contents
        ):

            print(
                "INDEX:",
                index
            )

            if getattr(element, "name", None):

                print(
                    "TAG:",
                    element.name
                )

                print(
                    "TEXT:",
                    element.get_text(
                        " ",
                        strip=True
                    )
                )

                if element.name == "a":

                    print(
                        "HREF:",
                        element.get("href")
                    )

            else:

                text = str(element).strip()

                print(
                    "TEXT:",
                    text
                )

            print("-" * 40)


print("\nOGURI CAP PARSED TEXT:")

for row in recommended_table.find_all("tr"):

    character = row.find("a")

    if not character:
        continue

    character_name = character.get_text(
        " ",
        strip=True
    )

    if character_name == "Oguri Cap (Ashen Miracle)":

        key_points_cell = row.find_all("td")[1]

        parsed_text = key_points_cell.get_text(
            "\n",
            strip=True
        )

        print(parsed_text)

# ---------------------------------------------------------

print("\nKEY POINTS LINKS CHECK:")

for row in recommended_table.find_all("tr"):

    cells = row.find_all("td")

    if len(cells) != 2:
        continue

    character = cells[0].get_text(
        " ",
        strip=True
    )

    key_points = cells[1]

    links = key_points.find_all(
        "a",
        href=True
    )

    print("\nCHARACTER:", character)

    for link in links:

        print(
            "TEXT:",
            link.get_text(
                " ",
                strip=True
            )
        )

        print(
            "URL:",
            link.get("href")
        )

{
    "name": "...",
    "url": "...",
    "image": "...",
    "running_style": [...],
    "key_points": [...],
    "skills": [...]
}


print("\n=== CARI HEADING STAT ===")

for heading in guide_soup.find_all(["h2", "h3", "h4"]):

    text = heading.get_text(
        " ",
        strip=True
    )

    if "Stat" in text:

        print(
            "TAG:",
            heading.name
        )

        print(
            "TEXT:",
            text
        )

        print("-" * 50)



sample_heading = guide_soup.find(
    id="hm_502"
)

if sample_heading:

    print(
        "=== SAMPLE DECK STRUCTURE ==="
    )

    current = sample_heading

    for i in range(15):

        current = current.find_next()

        if not current:
            break

        print(
            f"\n--- ELEMENT {i + 1} ---"
        )

        print(
            "TAG:",
            current.name
        )

        print(
            "ID:",
            current.get("id")
        )

        print(
            "CLASS:",
            current.get("class")
        )

        print(
            "TEXT:",
            current.get_text(
                " ",
                strip=True
            )[:300]
        )


sample_heading = guide_soup.find(
    id="hm_502"
)

sample_heading = guide_soup.find(
    id="hm_502"
)

if sample_heading:

    tables = sample_heading.find_all_next(
        "table"
    )

    print(
        "\nJUMLAH TABLE:",
        len(tables)
    )

    if len(tables) >= 2:

        sample_table = tables[1]

        print(
            "\n=== SAMPLE DECK TABLE ==="
        )

        print(
            sample_table.prettify()[:20000]
        )


print(
    "\n=== SAMPLE DECK ROWS ==="
)

for row in sample_table.find_all("tr"):

    cells = row.find_all(
        ["th", "td"],
        recursive=False
    )

    if not cells:
        continue

    print(
        "\nROW:"
    )

    for cell in cells:

        print(
            "TAG:",
            cell.name,
            "| TEXT:",
            cell.get_text(
                " ",
                strip=True
            )[:200]
        )


print("\n=== BUDGET ROW DETAIL ===")

for row in sample_table.find_all("tr"):
    cells = row.find_all(
        ["th", "td"],
        recursive=False
    )

    if not cells:
        continue

    if cells[0].get_text(
        " ",
        strip=True
    ) == "Budget":

        td = cells[1]

        for i, child in enumerate(td.find_all(recursive=False)):

            print(
                "CHILD:",
                i,
                "| TAG:",
                child.name,
                "| TEXT:",
                child.get_text(
                    " ",
                    strip=True
                )[:200]
            )


print("\n=== BUDGET SETUP DETAIL ===")

for row in sample_table.find_all("tr"):
    cells = row.find_all(
        ["th", "td"],
        recursive=False
    )

    if not cells:
        continue

    if cells[0].get_text(
        " ",
        strip=True
    ) == "Budget":

        td = cells[1]

        setups = td.find_all(
            "div",
            class_="align",
            recursive=False
        )

        for i, setup in enumerate(setups, start=1):

            print(
                f"\nSETUP {i}:"
            )

            for link in setup.find_all(
                "a",
                href=True
            ):

                print(
                    "URL:",
                    link.get("href")
                )

                print(
                    "TEXT:",
                    link.get_text(
                        " ",
                        strip=True
                    )
                )

                print("-" * 30)


print("\n=== FIRST SUPPORT CARD ===")

for row in sample_table.find_all("tr"):

    target_style = "End"

    cells = row.find_all(
        ["th", "td"],
        recursive=False
    )

    if not cells:
        continue

    if cells[0].get_text(
        " ",
        strip=True
    ) == target_style:

        td = cells[1]

        setups = td.find_all(
            "div",
            class_="align",
            recursive=False
        )

        setup = setups[0]

        first_link = setup.find(
            "a",
            href=True
        )

        print("URL:")
        print(first_link.get("href"))

        tooltip = first_link.find(
            "template",
            class_="js-tooltip-content"
        )

        print("\n=== TOOLTIP ===")

        if tooltip:
            print(
                tooltip.prettify()
            )
        else:
            print(
                "Tooltip tidak ditemukan."
            )

        break


if tooltip:

    content = tooltip.decode_contents()

    card_soup = BeautifulSoup(
        content,
        "html.parser"
    )

    bolds = card_soup.find_all("b")

    print("\n=== CARD DATA ===")

    print(
        "CHARACTER:",
        bolds[0].get_text(strip=True)
    )

    print(
        "CARD TITLE:",
        bolds[1].get_text(strip=True)
    )

    print(
        "RARITY:",
        bolds[2].next_sibling.strip()
    )

    print(
        "TYPE:",
        bolds[3].next_sibling.strip()
    )

    image = card_soup.find("img")

    print(
        "IMAGE:",
        image.get("data-src")
    )


def extract_support_card(link):

    tooltip = link.find(
        "template",
        class_="js-tooltip-content"
    )

    if not tooltip:
        return None

    content = tooltip.decode_contents()

    card_soup = BeautifulSoup(
        content,
        "html.parser"
    )

    bolds = card_soup.find_all("b")

    image = card_soup.find("img")

    card = {
        "character": bolds[0].get_text(
            strip=True
        ),

        "title": bolds[1].get_text(
            strip=True
        ),

        "rarity": bolds[2].next_sibling.strip(
            " :"
        ),

        "type": bolds[3].next_sibling.strip(
            " :"
        ),

        "image": image.get(
            "data-src"
        ),

        "url": link.get(
            "href"
        )
    }

    return card


def extract_sample_deck_style(
    sample_table,
    target_style
):

    for row in sample_table.find_all("tr"):

        cells = row.find_all(
            ["th", "td"],
            recursive=False
        )

        if not cells:
            continue

        style = cells[0].get_text(
            " ",
            strip=True
        )

        if style != target_style:
            continue

        td = cells[1]

        setups = td.find_all(
            "div",
            class_="align",
            recursive=False
        )

        stamina_setup = []

        speed_wit_option = []

        if len(setups) >= 1:

            for link in setups[0].find_all(
                "a",
                href=True
            ):

                card = extract_support_card(
                    link
                )

                if card:
                    stamina_setup.append(
                        card
                    )

        if len(setups) >= 2:

            for link in setups[1].find_all(
                "a",
                href=True
            ):

                card = extract_support_card(
                    link
                )

                if card:
                    speed_wit_option.append(
                        card
                    )

        return {
            "style": style,
            "stamina_setup": stamina_setup,
            "speed_wit_option": speed_wit_option
        }

    return None


def extract_all_sample_decks(
    sample_table
):

    styles = [
        "Budget",
        "Front",
        "Pace",
        "Late",
        "End"
    ]

    decks = []

    for style in styles:

        deck = extract_sample_deck_style(
            sample_table,
            style
        )

        if deck:
            decks.append(
                deck
            )

    return decks


sample_heading = guide_soup.find(
    id="hm_502"
)

tables = sample_heading.find_all_next(
    "table"
)

if len(tables) >= 2:

    sample_table = tables[1]

    all_decks = extract_all_sample_decks(
        sample_table
    )

    print(
        "\n=== ALL SAMPLE DECKS ==="
    )

    for deck in all_decks:

        print(
            "\nSTYLE:",
            deck["style"]
        )

        print(
            "Stamina:",
            len(
                deck["stamina_setup"]
            )
        )

        print(
            "Speed/Wit:",
            len(
                deck["speed_wit_option"]
            )
        )


print("\n=== PARENT DECK SETUPS ===")
parent_heading = guide_soup.find(
    id="hm_503"
)

if parent_heading:

    print(
        "TAG:",
        parent_heading.name
    )

    print(
        "TEXT:",
        parent_heading.get_text(
            " ",
            strip=True
        )
    )

    tables = parent_heading.find_all_next(
        "table"
    )

    print(
        "JUMLAH TABLE:",
        len(tables)
    )

print("\n=== PARENT TABLE SUMMARY ===")

for i, table in enumerate(tables):

    text = table.get_text(
        " ",
        strip=True
    )

    print(
        f"\nTABLE {i}:"
    )

    print(
        text[:300]
    )

parent_table = tables[0]

print("\n=== PARENT TABLE HTML ===")

print(
    parent_table.prettify()[:20000]
)

def extract_recommended_sparks(row):

    sparks = []

    for link in row.find_all(
        "a",
        href=True
    ):

        text = link.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        sparks.append({
            "name": text,
            "url": link.get("href")
        })

    return sparks

print(
    "\n=== RECOMMENDED SPARKS ==="
)

for row in parent_table.find_all("tr"):

    cells = row.find_all(
        ["th", "td"],
        recursive=False
    )

    if len(cells) < 2:
        continue

    style = cells[0].get_text(
        " ",
        strip=True
    )

    sparks = extract_recommended_sparks(
        cells[1]
    )

    print(
        "\nSTYLE:",
        style
    )

    for spark in sparks:
        print(
            spark["name"],
            "|",
            spark["url"]
        )


def extract_parent_deck_style(
    parent_table,
    target_style
):

    for row in parent_table.find_all("tr"):

        cells = row.find_all(
            ["th", "td"],
            recursive=False
        )

        if len(cells) < 2:
            continue

        style = cells[0].get_text(
            " ",
            strip=True
        )

        if style != target_style:
            continue

        td = cells[1]

        setups = td.find_all(
            "div",
            class_="align",
            recursive=False
        )

        support_cards = []

        if setups:

            for link in setups[0].find_all(
                "a",
                href=True
            ):

                card = extract_support_card(
                    link
                )

                if card:
                    support_cards.append(
                        card
                    )

        sparks = extract_recommended_sparks(
            td
        )

        return {
            "style": style,
            "support_cards": support_cards,
            "recommended_sparks": sparks
        }

    return None


parent_deck = extract_parent_deck_style(
    parent_table,
    "Front"
)

print(
    "\n=== PARENT DECK FRONT ==="
)

print(
    "STYLE:",
    parent_deck["style"]
)

print(
    "\nSUPPORT CARDS:"
)

for card in parent_deck["support_cards"]:

    print(
        card["character"],
        "|",
        card["title"],
        "|",
        card["rarity"],
        "|",
        card["type"]
    )

print(
    "\nRECOMMENDED SPARKS:"
)

for spark in parent_deck["recommended_sparks"]:

    print(
        spark["name"],
        "|",
        spark["url"]
    )


def extract_all_parent_decks(
    parent_table
):

    styles = [
        "Front",
        "Pace",
        "Late",
        "End"
    ]

    decks = []

    for style in styles:

        deck = extract_parent_deck_style(
            parent_table,
            style
        )

        if deck:
            decks.append(
                deck
            )

    return decks

all_parent_decks = extract_all_parent_decks(
    parent_table
)

print(
    "\n=== ALL PARENT DECKS ==="
)

for deck in all_parent_decks:

    print(
        "\nSTYLE:",
        deck["style"]
    )

    print(
        "SUPPORT CARDS:",
        len(
            deck["support_cards"]
        )
    )

    print(
        "RECOMMENDED SPARKS:",
        len(
            deck["recommended_sparks"]
        )
    )


def extract_recommended_character(row):

    cells = row.find_all(
        "td",
        recursive=False
    )

    if len(cells) < 2:
        return None

    character_cell = cells[0]
    key_points_cell = cells[1]

    # --------------------------------------------------
    # CHARACTER
    # --------------------------------------------------

    character_link = character_cell.find(
        "a",
        href=True
    )

    if not character_link:
        return None

    name = character_link.get_text(
        " ",
        strip=True
    )

    character_url = character_link.get(
        "href"
    )

    image = character_link.find(
        "img"
    )

    image_url = None

    if image:
        image_url = image.get(
            "data-src"
        )

    # --------------------------------------------------
    # RUNNING STYLE
    # --------------------------------------------------

    running_style = []

    style_div = key_points_cell.find(
        "div",
        class_="align"
    )

    if style_div:

        for image in style_div.find_all("img"):

            alt = image.get("alt")

            if alt in [
                "Front Runner",
                "Pace Chaser",
                "Late Surger",
                "End Closer"
            ]:

                running_style.append(
                    alt
                )

        # GAME8 ANOMALY:
        # T.M. Opera O menampilkan
        # "Late Surger" pada alt kedua,
        # tetapi teks sebenarnya adalah "Pace / Late".

        style_text = style_div.get_text(
            " ",
            strip=True
        )

        if (
            "Pace /" in style_text
            and "Late" in style_text
        ):

            running_style = [
                "Pace Chaser",
                "Late Surger"
            ]

    # --------------------------------------------------
    # KEY POINTS
    # --------------------------------------------------

    key_points = []

    hr = key_points_cell.find(
        "hr"
    )

    if hr:

        current_point = []

        for element in hr.next_siblings:

            if getattr(element, "name", None) == "br":

                text = " ".join(
                    current_point
                ).strip()

                if text:
                    key_points.append(
                        text
                    )

                current_point = []

                continue

            if getattr(element, "name", None):

                text = element.get_text(
                    " ",
                    strip=True
                )

            else:

                text = str(element).strip()

            if text:
                current_point.append(
                    text
                )

        text = " ".join(
            current_point
        ).strip()

        if text:
            key_points.append(
                text
            )

    # --------------------------------------------------
    # SKILLS
    # --------------------------------------------------

    skills = []

    for link in key_points_cell.find_all(
        "a",
        href=True
    ):

        skill_name = link.get_text(
            " ",
            strip=True
        )

        if not skill_name:
            continue

        skills.append({
            "name": skill_name,
            "url": link.get(
                "href"
            )
        })

    # --------------------------------------------------
    # RESULT
    # --------------------------------------------------

    return {
        "name": name,
        "url": character_url,
        "image": image_url,
        "running_style": running_style,
        "key_points": key_points,
        "skills": skills
    }


print(
    "\n=== TEST RECOMMENDED CHARACTER ==="
)

for row in recommended_table.find_all(
    "tr"
):

    character_link = row.find(
        "a",
        href=True
    )

    if not character_link:
        continue

    name = character_link.get_text(
        " ",
        strip=True
    )

    if name == "Oguri Cap (Ashen Miracle)":

        character = extract_recommended_character(
            row
        )

        print(
            character
        )

        break


def extract_all_recommended_characters(table):

    characters = []

    for row in table.find_all("tr"):

        character = extract_recommended_character(
            row
        )

        if character:
            characters.append(
                character
            )

    return characters

recommended_characters = extract_all_recommended_characters(
    recommended_table
)

print(
    "TOTAL RECOMMENDED CHARACTERS:",
    len(recommended_characters)
)

for character in recommended_characters:

    print(
        character["name"],
        "|",
        character["running_style"]
    )

recommended_characters = []

for index, row in enumerate(
    recommended_table.find_all("tr")
):

    character = extract_recommended_character(
        row
    )

    if character:
        recommended_characters.append(
            character
        )
    else:
        print(
            "SKIP ROW:",
            index,
            row.get_text(
                " ",
                strip=True
            )[:300]
        )

print(
    "TOTAL:",
    len(recommended_characters)
)

for row in recommended_table.find_all("tr"):

    character = extract_recommended_character(
        row
    )

    if character:
        if character["name"] == "T.M. Opera O (New Year, Same Radiance!)":

            print(
                "=== TEST T.M. OPERA O ==="
            )

            print(
                character
            )

            break

recommended_characters = extract_all_recommended_characters(
    recommended_table
)

print(
    "TOTAL RECOMMENDED CHARACTERS:",
    len(recommended_characters)
)

for character in recommended_characters:

    print(
        character["name"],
        "|",
        character["running_style"]
    )