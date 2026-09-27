import requests
import logging
from scraper import get_news
from bs4 import BeautifulSoup

GAME8_BASE_URL = "https://game8.co"

GAME8_URL = (
    "https://game8.co/games/"
    "Umamusume-Pretty-Derby"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ============================================================
# SUPPORT CARD EXTRACTION
# ============================================================

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

    bolds = card_soup.find_all(
        "b"
    )

    image = card_soup.find(
        "img"
    )

    if len(bolds) < 4:
        return None

    if not image:
        return None

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


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skill_groups(table):

    groups = []

    if not table:
        return groups

    rows = table.find_all(
        "tr"
    )

    for row in rows:

        cells = row.find_all(
            ["th", "td"],
            recursive=False
        )

        # ====================================================
        # PATTERN 1: TH + TD
        # ====================================================

        if len(cells) == 2:

            heading_cell = cells[0]
            content_cell = cells[1]

            group_name = heading_cell.get_text(
                " ",
                strip=True
            )

            if not group_name:
                continue

            group = {
                "name": group_name,
                "skills": []
            }

            for element in content_cell.find_all(
                "div",
                class_="align",
                recursive=False
            ):

                # ------------------------------------------------
                # DIRECT BOLD SKILL
                # ------------------------------------------------

                bold = element.find(
                    "b",
                    class_="a-bold",
                    recursive=False
                )

                if bold:

                    skill_name = bold.get_text(
                        " ",
                        strip=True
                    )

                    notes = element.get_text(
                        " ",
                        strip=True
                    )

                    notes = notes.replace(
                        skill_name,
                        "",
                        1
                    ).strip()

                    notes = notes.lstrip(
                        "・"
                    ).strip()

                    group["skills"].append({
                        "name": skill_name,
                        "url": None,
                        "notes": notes
                    })

                    continue

                # ------------------------------------------------
                # LINK SKILLS
                # ------------------------------------------------

                links = element.find_all(
                    "a",
                    href=True
                )

                if not links:
                    continue

                source = None
                skill_links = []

                for link in links:

                    tooltip = link.find(
                        "template",
                        class_="js-tooltip-content"
                    )

                    if tooltip:

                        tooltip_text = tooltip.get_text(
                            " ",
                            strip=True
                        )

                        if tooltip_text:

                            source = tooltip_text.split(
                                "Rarity",
                                1
                            )[0].strip()

                        continue

                    skill_links.append(
                        link
                    )

                if not skill_links:
                    continue

                skill_names = []

                for skill_link in skill_links:

                    skill_name = skill_link.get_text(
                        " ",
                        strip=True
                    )

                    if skill_name:
                        skill_names.append(
                            skill_name
                        )

                skill_name = " / ".join(
                    skill_names
                )

                notes = []

                last_skill_link = (
                    skill_links[-1]
                )

                for sibling in (
                    last_skill_link.next_siblings
                ):

                    if getattr(
                        sibling,
                        "name",
                        None
                    ):

                        text = sibling.get_text(
                            " ",
                            strip=True
                        )

                    else:

                        text = str(
                            sibling
                        ).strip()

                    if text:
                        notes.append(
                            text
                        )

                skill_data = {
                    "name": skill_name,
                    "url": skill_links[0].get(
                        "href"
                    ),
                    "notes": " ".join(
                        notes
                    )
                }

                if source:

                    skill_data["source"] = (
                        source
                    )

                group["skills"].append(
                    skill_data
                )

            groups.append(
                group
            )

            continue

        # ====================================================
        # PATTERN 2: SINGLE TD
        # ====================================================

        if len(cells) != 1:
            continue

        cell = cells[0]

        if cell.name != "td":
            continue

        current_group = None

        for element in cell.children:

            # ------------------------------------------------
            # GROUP SEPARATOR
            # ------------------------------------------------

            if getattr(
                element,
                "name",
                None
            ) == "hr":

                current_group = None
                continue

            # ------------------------------------------------
            # GROUP FROM BOLD
            # ------------------------------------------------

            if getattr(
                element,
                "name",
                None
            ) == "b":

                group_name = element.get_text(
                    " ",
                    strip=True
                ).rstrip(":")

                if group_name:

                    current_group = {
                        "name": group_name,
                        "skills": []
                    }

                    groups.append(
                        current_group
                    )

                continue

            # ------------------------------------------------
            # ONLY PROCESS DIV ALIGN
            # ------------------------------------------------

            if getattr(
                element,
                "name",
                None
            ) != "div":

                continue

            if "align" not in element.get(
                "class",
                []
            ):

                continue

            # ------------------------------------------------
            # DIRECT BOLD SKILL
            # ------------------------------------------------

            bold = element.find(
                "b",
                class_="a-bold",
                recursive=False
            )

            if bold:

                skill_name = bold.get_text(
                    " ",
                    strip=True
                )

                notes = element.get_text(
                    " ",
                    strip=True
                )

                notes = notes.replace(
                    skill_name,
                    "",
                    1
                ).strip()

                notes = notes.lstrip(
                    "・"
                ).strip()

                if current_group is not None:

                    current_group["skills"].append({
                        "name": skill_name,
                        "url": None,
                        "notes": notes
                    })

                continue

            # ------------------------------------------------
            # LINK SKILLS
            # ------------------------------------------------

            links = element.find_all(
                "a",
                href=True
            )

            if not links:
                continue

            source = None
            skill_links = []

            for link in links:

                tooltip = link.find(
                    "template",
                    class_="js-tooltip-content"
                )

                if tooltip:

                    tooltip_text = tooltip.get_text(
                        " ",
                        strip=True
                    )

                    if tooltip_text:

                        source = tooltip_text.split(
                            "Rarity",
                            1
                        )[0].strip()

                    continue

                skill_links.append(
                    link
                )

            if not skill_links:
                continue

            skill_names = []

            for skill_link in skill_links:

                skill_name = skill_link.get_text(
                    " ",
                    strip=True
                )

                if skill_name:
                    skill_names.append(
                        skill_name
                    )

            skill_name = " / ".join(
                skill_names
            )

            notes = []

            last_skill_link = (
                skill_links[-1]
            )

            for sibling in (
                last_skill_link.next_siblings
            ):

                if getattr(
                    sibling,
                    "name",
                    None
                ):

                    text = sibling.get_text(
                        " ",
                        strip=True
                    )

                else:

                    text = str(
                        sibling
                    ).strip()

                if text:
                    notes.append(
                        text
                    )

            if current_group is None:
                continue

            skill_data = {
                "name": skill_name,
                "url": skill_links[0].get(
                    "href"
                ),
                "notes": " ".join(
                    notes
                )
            }

            if source:

                skill_data["source"] = source

            current_group["skills"].append(
                skill_data
            )

    return groups


def extract_green_skill_groups(table):

    groups = []

    if not table:
        return groups

    rows = table.find_all("tr")

    for row in rows:

        cells = row.find_all(
            ["th", "td"],
            recursive=False
        )

        if len(cells) != 1:
            continue

        cell = cells[0]

        current_group = None

        for element in cell.children:

            # TEXT NODE
            if not getattr(
                element,
                "name",
                None
            ):

                text = str(element).strip()

                if text.endswith(":"):

                    group_name = text.rstrip(":")

                    current_group = {
                        "name": group_name,
                        "skills": []
                    }

                    groups.append(
                        current_group
                    )

                continue

            # HR = pemisah group
            if element.name == "hr":

                current_group = None

                continue

            # DIV ALIGN = skill
            if element.name != "div":
                continue

            if "align" not in element.get(
                "class",
                []
            ):
                continue

            link = element.find(
                "a",
                href=True
            )

            if not link:
                continue

            skill_name = link.get_text(
                " ",
                strip=True
            )

            if not skill_name:
                continue

            notes = []

            for sibling in link.next_siblings:

                if getattr(
                    sibling,
                    "name",
                    None
                ):

                    text = sibling.get_text(
                        " ",
                        strip=True
                    )

                else:

                    text = str(
                        sibling
                    ).strip()

                if text:
                    notes.append(text)

            skill_data = {
                "name": skill_name,
                "url": link.get("href"),
                "notes": " ".join(notes)
            }

            if current_group is not None:

                current_group["skills"].append(
                    skill_data
                )

    return groups


def extract_debuff_groups(table):

    groups = []

    if not table:
        return groups

    cell = table.find(
        "td"
    )

    if not cell:
        return groups

    current_group = None

    for element in cell.children:

        # ----------------------------------------------------
        # TEXT GROUP
        # ----------------------------------------------------

        if getattr(
            element,
            "name",
            None
        ) is None:

            text = str(
                element
            ).strip()

            if not text:
                continue

            if text in [
                "Speed Debuffs",
                "Stamina Debuffs"
            ]:

                current_group = {
                    "name": text,
                    "skills": []
                }

                groups.append(
                    current_group
                )

            continue

        # ----------------------------------------------------
        # REQUIRES 564 ESCAPADES
        # ----------------------------------------------------

        if (
            getattr(
                element,
                "name",
                None
            ) == "a"
            and "564 Escapades"
            in element.get_text(
                " ",
                strip=True
            )
        ):

            current_group = {
                "name": "Requires 564 Escapades",
                "skills": []
            }

            groups.append(
                current_group
            )

            continue

        # ----------------------------------------------------
        # SKILL
        # ----------------------------------------------------

        if getattr(
            element,
            "name",
            None
        ) != "div":

            continue

        if "align" not in element.get(
            "class",
            []
        ):

            continue

        links = element.find_all(
            "a",
            href=True
        )

        if not links:
            continue

        skill_names = []

        for link in links:

            skill_name = link.get_text(
                " ",
                strip=True
            )

            if skill_name:
                skill_names.append(
                    skill_name
                )

        if not skill_names:
            continue

        if current_group is None:
            continue

        current_group["skills"].append({
            "name": " / ".join(
                skill_names
            ),
            "url": links[0].get(
                "href"
            ),
            "notes": ""
        })

    return groups


# ============================================================
# STAT BASELINES
# ============================================================

def extract_stat_baselines(table):

    result = {}

    if not table:
        return result

    rows = table.find_all(
        "tr"
    )

    for index, row in enumerate(rows):

        cells = row.find_all(
            ["th", "td"],
            recursive=False
        )

        if len(cells) != 5:
            continue

        if not all(
            cell.name == "th"
            for cell in cells
        ):

            continue

        stats = []

        for cell in cells:

            image = cell.find(
                "img"
            )

            if image:

                stat_name = image.get(
                    "alt"
                )

                if stat_name:
                    stats.append(
                        stat_name
                    )

        if stats != [
            "Speed",
            "Stamina",
            "Power",
            "Guts",
            "Wit"
        ]:

            continue

        result["stats"] = stats

        if index + 1 < len(rows):

            value_row = rows[
                index + 1
            ]

            value_cells = value_row.find_all(
                "td",
                recursive=False
            )

            if len(value_cells) == 5:

                values = []

                for cell in value_cells:

                    values.append(
                        cell.get_text(
                            " ",
                            strip=True
                        )
                    )

                result["values"] = dict(
                    zip(
                        stats,
                        values
                    )
                )

        break

    return result


# ============================================================
# OPEN LEAGUE STATS
# ============================================================

def extract_open_league_stats(table):

    result = {}

    if not table:
        return result

    rows = table.find_all(
        "tr"
    )

    for index, row in enumerate(rows):

        cells = row.find_all(
            "td",
            recursive=False
        )

        if len(cells) != 5:
            continue

        previous_row = rows[
            index - 1
        ]

        heading = previous_row.find(
            "th"
        )

        if not heading:
            continue

        heading_text = heading.get_text(
            " ",
            strip=True
        )

        if heading_text != (
            "Open League (A+) Recommendation"
        ):

            continue

        stats = [
            "Speed",
            "Stamina",
            "Power",
            "Guts",
            "Wit"
        ]

        values = []

        for cell in cells:

            value = cell.get_text(
                " ",
                strip=True
            )

            image = cell.find(
                "img"
            )

            if image:

                image_alt = image.get(
                    "alt"
                )

                if image_alt:

                    value = (
                        f"{value} "
                        f"{image_alt}"
                    ).strip()

            values.append(
                value
            )

        result = dict(
            zip(
                stats,
                values
            )
        )

        break

    return result


# ============================================================
# STAT PRIORITY
# ============================================================

def extract_stat_priority(table):

    result = {}

    if not table:
        return result

    rows = table.find_all(
        "tr"
    )

    for row in rows:

        cell = row.find(
            "td",
            colspan="5"
        )

        if not cell:
            continue

        text = cell.get_text(
            " ",
            strip=True
        )

        if not text.startswith(
            "ⓘ Prioritize maximizing stats"
        ):

            continue

        # ----------------------------------------------------
        # PRIORITY
        # ----------------------------------------------------

        links = cell.find_all(
            "a",
            href=True
        )

        priority = []

        for link in links:

            stat_name = link.get_text(
                " ",
                strip=True
            )

            if stat_name:
                priority.append(
                    stat_name
                )

        # ----------------------------------------------------
        # NOTE
        # ----------------------------------------------------

        note = None

        bold = cell.find(
            "b",
            class_="a-bold"
        )

        if bold:

            note_parts = []

            for element in (
                bold.parent.children
            ):

                if element == bold:

                    note_parts.append(
                        bold.get_text(
                            " ",
                            strip=True
                        )
                    )

                    continue

                if getattr(
                    element,
                    "name",
                    None
                ) == "br":

                    continue

                if getattr(
                    element,
                    "name",
                    None
                ):

                    value = element.get_text(
                        " ",
                        strip=True
                    )

                else:

                    value = str(
                        element
                    ).strip()

                if value:

                    note_parts.append(
                        value
                    )

            note = " ".join(
                note_parts
            )

            if "┗" in note:

                note = note.split(
                    "┗",
                    1
                )[1].strip()

        result = {
            "priority": priority,
            "note": note
        }

        break

    return result


# ============================================================
# RACE CONDITIONS
# ============================================================

def extract_race_conditions(table):

    result = {}

    if not table:
        return result

    rows = table.find_all(
        "tr"
    )

    for index, row in enumerate(rows):

        cells = row.find_all(
            "th",
            recursive=False
        )

        if len(cells) != 3:
            continue

        headers = []

        for cell in cells:

            headers.append(
                cell.get_text(
                    " ",
                    strip=True
                )
            )

        if headers != [
            "Distance",
            "Track",
            "Style"
        ]:

            continue

        if index + 1 >= len(rows):
            break

        value_row = rows[
            index + 1
        ]

        value_cells = value_row.find_all(
            "td",
            recursive=False
        )

        if len(value_cells) != 3:
            break

        for header, cell in zip(
            headers,
            value_cells
        ):

            rank = None

            rank_element = cell.find(
                "b",
                class_="a-bold"
            )

            if rank_element:

                rank = rank_element.get_text(
                    " ",
                    strip=True
                )

            text = cell.get_text(
                " ",
                strip=True
            )

            if rank:

                text = text.replace(
                    rank,
                    "",
                    1
                ).strip()

            priority = None

            if "Prio:" in text:

                name, priority = text.split(
                    "Prio:",
                    1
                )

                name = name.strip()
                priority = priority.strip()

            else:

                name = text

            result[header] = {
                "name": name,
                "rank": rank,
                "priority": priority
            }

        break

    return result


# ============================================================
# BLUE SPARKS
# ============================================================

def extract_blue_sparks(table):

    result = {}

    if not table:
        return result

    rows = table.find_all(
        "tr"
    )

    for row in rows:

        cells = row.find_all(
            ["th", "td"],
            recursive=False
        )

        if len(cells) != 2:
            continue

        heading = cells[0].get_text(
            " ",
            strip=True
        )

        if heading != "Blue Sparks Init. Stats":
            continue

        content = cells[1]

        parts = content.find_all(
            "hr",
            recursive=False
        )

        recommendation = None
        note = None

        if parts:

            recommendation = (
                parts[0]
                .previous_sibling
            )

            if recommendation:

                recommendation = str(
                    recommendation
                ).strip()

            note = content.get_text(
                " ",
                strip=True
            )

            if recommendation:

                note = note.replace(
                    recommendation,
                    "",
                    1
                ).strip()

        else:

            recommendation = content.get_text(
                " ",
                strip=True
            )

        result = {
            "recommendation": recommendation,
            "note": note
        }

        break

    return result


# ============================================================
# RECOMMENDED SPARKS
# ============================================================

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
            "url": link.get(
                "href"
            )
        })

    return sparks


# ============================================================
# SAMPLE DECK
# ============================================================

def extract_sample_deck_style(
    sample_table,
    target_style
):

    if not sample_table:
        return None

    for row in sample_table.find_all(
        "tr"
    ):

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


# ============================================================
# PARENT DECK
# ============================================================

def extract_parent_deck_style(
    parent_table,
    target_style
):

    if not parent_table:
        return None

    for row in parent_table.find_all(
        "tr"
    ):

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


# ============================================================
# TIER LIST CHARACTER EXTRACTION
# ============================================================

def extract_tier_characters(row):

    rank_cell = row.find(
        "th",
        recursive=False
    )

    character_cell = row.find(
        "td",
        recursive=False
    )

    if not rank_cell or not character_cell:
        return []

    rank_image = rank_cell.find(
        "img"
    )

    rank = None

    if rank_image:

        rank_text = rank_image.get(
            "alt",
            ""
        )

        rank = rank_text.replace(
            " Rank",
            ""
        ).strip()

    characters = []

    character_links = character_cell.find_all(
        "a",
        href=True
    )

    for character_link in character_links:

        character_url = character_link.get(
            "href"
        )

        character_image = character_link.find(
            "img"
        )

        image_url = None

        if character_image:

            image_url = character_image.get(
                "data-src"
            )

        tooltip = character_link.find(
            "template",
            class_="js-tooltip-content"
        )

        name = None
        rarity = None

        if tooltip:

            tooltip_text = tooltip.get_text(
                " ",
                strip=True
            )

            parts = tooltip_text.split(
                "Rarity",
                1
            )

            if parts:

                name = parts[0].strip()

            if len(parts) > 1:

                rarity = parts[1].replace(
                    ":",
                    ""
                ).strip()

        characters.append({
            "rank": rank,
            "name": name,
            "url": character_url,
            "image": image_url,
            "rarity": rarity
        })

    return characters


def extract_all_tier_characters(
    tier_table
):

    characters = []

    if not tier_table:
        return characters

    for row in tier_table.find_all(
        "tr"
    ):

        characters.extend(
            extract_tier_characters(
                row
            )
        )

    return characters


# ============================================================
# RECOMMENDED CHARACTER EXTRACTION
# ============================================================

def extract_recommended_character(
    row
):

    cells = row.find_all(
        "td",
        recursive=False
    )

    if len(cells) < 2:
        return None

    character_cell = cells[0]
    key_points_cell = cells[1]

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

    # --------------------------------------------------------
    # RUNNING STYLE
    # --------------------------------------------------------

    running_style = []

    style_div = key_points_cell.find(
        "div",
        class_="align"
    )

    if style_div:

        for image in style_div.find_all(
            "img"
        ):

            alt = image.get(
                "alt"
            )

            if alt in [
                "Front Runner",
                "Pace Chaser",
                "Late Surger",
                "End Closer"
            ]:

                running_style.append(
                    alt
                )

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

    # --------------------------------------------------------
    # KEY POINTS
    # --------------------------------------------------------

    key_points = []

    hr = key_points_cell.find(
        "hr"
    )

    if hr:

        current_point = []

        for element in hr.next_siblings:

            if getattr(
                element,
                "name",
                None
            ) == "br":

                text = " ".join(
                    current_point
                ).strip()

                if text:

                    key_points.append(
                        text
                    )

                current_point = []

                continue

            if getattr(
                element,
                "name",
                None
            ):

                text = element.get_text(
                    " ",
                    strip=True
                )

            else:

                text = str(
                    element
                ).strip()

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

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

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

    return {
        "name": name,
        "url": character_url,
        "image": image_url,
        "running_style": running_style,
        "key_points": key_points,
        "skills": skills
    }


def extract_all_recommended_characters(
    table
):

    characters = []

    if not table:
        return characters

    for row in table.find_all(
        "tr"
    ):

        character = extract_recommended_character(
            row
        )

        if character:

            characters.append(
                character
            )

    return characters


# ============================================================
# MAP EXTRACTION
# ============================================================

def extract_race_map(
    soup
):

    image_link = soup.find(
        "div",
        class_="js-archive-open-image-modal"
    )

    if not image_link:

        logging.warning(
            "❌ Race map Game8 tidak ditemukan."
        )

        return None

    map_url = image_link.get(
        "data-image-url"
    )

    if not map_url:

        logging.warning(
            "❌ URL race map Game8 kosong."
        )

        return None

    logging.info(
        f"🗺️ Game8 Map URL: {map_url}"
    )

    return map_url


# ============================================================
# MAIN SCRAPER
# ============================================================

def get_game8_data():

    # ========================================================
    # GAME8 PAGE
    # ========================================================

    game8_response = requests.get(
        GAME8_URL,
        headers=HEADERS,
        timeout=20
    )

    game8_response.raise_for_status()

    game8_soup = BeautifulSoup(
        game8_response.text,
        "html.parser"
    )


    # ========================================================
    # OFFICIAL NEWS
    # ========================================================

    news_list = get_news(
        limit=50
    )


    # ========================================================
    # GAME8 GUIDE DISCOVERY
    # ========================================================

    links = game8_soup.find_all(
        "a",
        href=True
    )

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


    # ========================================================
    # FIND CURRENT CHAMPIONS MEETING
    # ========================================================

    guide_soup = None
    current_cup = None
    guide_url = None

    for news in news_list:

        title = news["title"]

        if "The race event Champions Meeting:" not in title:
            continue

        cup_part = title.split(
            "Champions Meeting:",
            1
        )[1].strip()

        if " is here!" in cup_part:

            current_cup = cup_part.replace(
                " is here!",
                ""
            ).strip()

        elif " is coming" in cup_part:

            current_cup = cup_part.split(
                " is coming",
                1
            )[0].strip()

        else:

            continue

        guide_url = game8_guides.get(
            current_cup
        )

        logging.info(
            f"🏆 Game8 Cup Discovery | "
            f"News: {current_cup} | "
            f"Guide: {guide_url}"
        )

        if guide_url:

            if guide_url.startswith("/"):

                guide_url = (
                    GAME8_BASE_URL
                    + guide_url
                )

            guide_response = requests.get(
                guide_url,
                headers=HEADERS,
                timeout=20
            )

            guide_response.raise_for_status()

            guide_soup = BeautifulSoup(
                guide_response.text,
                "html.parser"
            )

            break    


    # ========================================================
    # STOP IF GUIDE NOT FOUND
    # ========================================================

    if not guide_soup:

        return {
            "current_cup": current_cup,
            "guide_url": None,
            "map_url": None,

            "tier_characters": [],
            "recommended_characters": [],

            "green_skills": [],
            "acceleration_skills": [],
            "speed_skills": [],
            "recovery_skills": [],
            "debuff_skills": [],

            "race_conditions": {},
            "blue_sparks": {},

            "stat_baselines": {},
            "open_league_stats": {},
            "stat_priority": {},

            "sample_decks": [],
            "parent_decks": []
        }


    # ========================================================
    # FIND GUIDE TABLES
    # ========================================================

    tier_h3 = None
    tier_table = None

    for heading in guide_soup.find_all(
        ["h2", "h3"]
    ):

        text = heading.get_text(
            " ",
            strip=True
        )

        if "Tier List" in text:

            tier_h3 = heading
            break

    if tier_h3:

        tier_table = tier_h3.find_next(
            "table"
        )


    # --------------------------------------------------------
    # RECOMMENDED CHARACTERS
    # --------------------------------------------------------

    recommended_h3 = None
    recommended_table = None

    for heading in guide_soup.find_all(
        ["h2", "h3"]
    ):

        text = heading.get_text(
            " ",
            strip=True
        )

        if "Recommended Characters" in text:

            recommended_h3 = heading
            break

    if recommended_h3:

        recommended_table = (
            recommended_h3.find_next(
                "table"
            )
        )


    # --------------------------------------------------------
    # STAT GUIDELINES
    # --------------------------------------------------------

    stat_heading = guide_soup.find(
        "h2",
        string=lambda text: (
            text
            and "Stat Guidelines" in text
        )
    )

    stat_table = None

    if stat_heading:

        stat_table = stat_heading.find_next(
            "table"
        )


    # --------------------------------------------------------
    # RECOMMENDED SKILLS
    # --------------------------------------------------------

    skill_heading = guide_soup.find(
        "h2",
        string=lambda text: (
            text
            and "Recommended Skills" in text
        )
    )

    skill_table = None

    if skill_heading:

        skill_table = skill_heading.find_next(
            "table"
        )


    # --------------------------------------------------------
    # SKILL SUBSECTIONS
    # --------------------------------------------------------

    green_heading = guide_soup.find(
        "h3",
        id="hm_301"
    )

    green_table = None

    if green_heading:

        green_table = green_heading.find_next(
            "table"
        )


    accel_heading = guide_soup.find(
        "h3",
        id="hm_302"
    )

    accel_table = None

    if accel_heading:

        accel_table = accel_heading.find_next(
            "table"
        )


    speed_heading = guide_soup.find(
        "h3",
        id="hm_303"
    )

    speed_table = None

    if speed_heading:

        speed_table = speed_heading.find_next(
            "table"
        )


    recovery_heading = guide_soup.find(
        "h3",
        id="hm_304"
    )

    recovery_table = None

    if recovery_heading:

        recovery_table = recovery_heading.find_next(
            "table"
        )


    debuff_heading = guide_soup.find(
        "h3",
        id="hm_305"
    )

    debuff_table = None

    if debuff_heading:

        debuff_table = debuff_heading.find_next(
            "table"
        )


    # --------------------------------------------------------
    # SUPPORT CARDS
    # --------------------------------------------------------

    support_heading = guide_soup.find(
        "h3",
        id="hm_501"
    )

    support_table = None

    if support_heading:

        support_table = support_heading.find_next(
            "table"
        )


    # --------------------------------------------------------
    # SAMPLE DECK
    # --------------------------------------------------------

    sample_heading = guide_soup.find(
        id="hm_502"
    )

    sample_table = None

    if sample_heading:

        tables = sample_heading.find_all_next(
            "table"
        )

        if len(tables) >= 2:

            sample_table = tables[1]


    # --------------------------------------------------------
    # PARENT DECK
    # --------------------------------------------------------

    parent_heading = guide_soup.find(
        id="hm_503"
    )

    parent_table = None

    if parent_heading:

        tables = parent_heading.find_all_next(
            "table"
        )

        if tables:

            parent_table = tables[0]


    # ========================================================
    # EXTRACT ALL DATA
    # ========================================================

    tier_characters = (
        extract_all_tier_characters(
            tier_table
        )
    )

    recommended_characters = (
        extract_all_recommended_characters(
            recommended_table
        )
    )

    green_skills = (
        extract_green_skill_groups(
            green_table
        )
    )

    accel_skills = extract_skill_groups(
        accel_table
    )

    speed_skills = extract_skill_groups(
        speed_table
    )

    recovery_skills = extract_skill_groups(
        recovery_table
    )

    debuff_skills = extract_debuff_groups(
        debuff_table
    )

    stat_baselines = extract_stat_baselines(
        stat_table
    )

    open_league_stats = extract_open_league_stats(
        stat_table
    )

    race_conditions = extract_race_conditions(
        stat_table
    )

    blue_sparks = extract_blue_sparks(
        stat_table
    )

    stat_priority = extract_stat_priority(
        stat_table
    )

    sample_decks = extract_all_sample_decks(
        sample_table
    )

    parent_decks = extract_all_parent_decks(
        parent_table
    )

    map_url = extract_race_map(
        guide_soup
    )
    logging.info(
    f"🖼️ Game8 Map URL: {map_url}"
)


    # ========================================================
    # FINAL DATA
    # ========================================================

    game8_data = {

        "current_cup": current_cup,

        "guide_url": guide_url,

        "map_url": map_url,

        "tier_characters": tier_characters,

        "recommended_characters": (
            recommended_characters
        ),

        "green_skills": green_skills,

        "acceleration_skills": (
            accel_skills
        ),

        "speed_skills": speed_skills,

        "recovery_skills": (
            recovery_skills
        ),

        "debuff_skills": debuff_skills,

        "race_conditions": race_conditions,

        "blue_sparks": blue_sparks,

        "stat_baselines": (
            stat_baselines
        ),

        "open_league_stats": (
            open_league_stats
        ),

        "stat_priority": (
            stat_priority
        ),

        "sample_decks": sample_decks,

        "parent_decks": parent_decks
    }

    return game8_data


if __name__ == "__main__":
    data = get_game8_data()

    print("CURRENT CUP:")
    print(data["current_cup"])

    print("\nGUIDE URL:")
    print(data["guide_url"])

    print("\nTIER CHARACTERS:")
    print(len(data["tier_characters"]))

    print("\nRECOMMENDED CHARACTERS:")
    print(len(data["recommended_characters"]))

    print("\nGREEN SKILL GROUPS:")
    print(len(data["green_skills"]))

    print("\nACCELERATION SKILL GROUPS:")
    print(len(data["acceleration_skills"]))

    print("\nSPEED SKILL GROUPS:")
    print(len(data["speed_skills"]))

    print("\nRECOVERY SKILL GROUPS:")
    print(len(data["recovery_skills"]))

    print("\nDEBUFF SKILL GROUPS:")
    print(len(data["debuff_skills"]))

    print("\nSAMPLE DECKS:")
    print(len(data["sample_decks"]))

    print("\nPARENT DECKS:")
    print(len(data["parent_decks"]))






