import discord


# ============================================================
# SKILL EMBED
# ============================================================

def format_skill_embed(
    skill_groups,
    title
):

    embed = discord.Embed(
        title=title,
        color=discord.Color.from_str(
            "#5865F2"
        )
    )

    for group in skill_groups:

        skills_text = []

        for skill in group["skills"]:

            name = skill["name"]
            notes = skill["notes"]

            skill_line = (
                f"• {name}"
            )

            if notes:
                skill_line += (
                    f" — {notes}"
                )

            skills_text.append(
                skill_line
            )

        if not skills_text:

            skills_text.append(
                "Tidak ada data skill."
            )

        embed.add_field(
            name=f"📌 {group['name']}",
            value="\n".join(
                skills_text
            ),
            inline=False
        )

    embed.set_footer(
        text=(
            "Diamond Fanmade • Timeline • Not affiliated with Cygames "
        )
    )

    return embed


# ============================================================
# GUIDE OVERVIEW
# ============================================================

def format_guide_overview(data):

    embed = discord.Embed(
        title=(
            f"🏆 {data['current_cup']} Guide"
        ),
        description=(
            "Pilih kategori guide "
            "menggunakan tombol di bawah."
        ),
        color=discord.Color.from_str(
            "#5865F2"
        )
    )

    embed.set_author(
        name=(
            "Diamond Fanmade • Guide"
        )
    )

    # --------------------------------------------------------
    # Race Conditions
    # --------------------------------------------------------

    embed.add_field(
        name="🏁 Race Conditions",
        value=(
            f"📏 **Distance:** "
            f"{data['race_conditions']['Distance']['name']} "
            f"({data['race_conditions']['Distance']['rank']})\n"

            f"🌱 **Track:** "
            f"{data['race_conditions']['Track']['name']} "
            f"({data['race_conditions']['Track']['rank']})\n"

            f"🏇 **Style:** "
            f"{data['race_conditions']['Style']['name']} "
            f"({data['race_conditions']['Style']['rank']})"
        ),
        inline=False
    )

    # --------------------------------------------------------
    # Stat Baselines
    # --------------------------------------------------------

    embed.add_field(
        name="📊 Stat Baselines",
        value=(
            f"👟 **Speed:** "
            f"{data['stat_baselines']['values']['Speed']}\n"

            f"❤️ **Stamina:** "
            f"{data['stat_baselines']['values']['Stamina']}\n"

            f"💪 **Power:** "
            f"{data['stat_baselines']['values']['Power']}\n"

            f"🔥 **Guts:** "
            f"{data['stat_baselines']['values']['Guts']}\n"

            f"🧠 **Wit:** "
            f"{data['stat_baselines']['values']['Wit']}"
        ),
        inline=False
    )

    # --------------------------------------------------------
    # Open League Stats
    # --------------------------------------------------------

    embed.add_field(
        name="🏟️ Open League Stats",
        value=(
            f"👟 **Speed:** "
            f"{data['open_league_stats']['Speed']}\n"

            f"❤️ **Stamina:** "
            f"{data['open_league_stats']['Stamina']}\n"

            f"💪 **Power:** "
            f"{data['open_league_stats']['Power']}\n"

            f"🔥 **Guts:** "
            f"{data['open_league_stats']['Guts']}\n"

            f"🧠 **Wit:** "
            f"{data['open_league_stats']['Wit']}"
        ),
        inline=False
    )

    # --------------------------------------------------------
    # Character Summary
    # --------------------------------------------------------

    embed.add_field(
        name="🎯 Recommended Characters",
        value=(
            f"**{len(data['recommended_characters'])}** "
            f"characters"
        ),
        inline=True
    )

    embed.add_field(
        name="⭐ Tier Characters",
        value=(
            f"**{len(data['tier_characters'])}** "
            f"characters"
        ),
        inline=True
    )

    embed.set_footer(
        text=(
            "Diamond Fanmade • Timeline • Not affiliated with Cygames"
        )
    )

    return embed


# ============================================================
# BLUE SPARKS
# ============================================================

def format_blue_sparks_embed(data):

    embed = discord.Embed(
        title="🔵 Blue Sparks",
        color=discord.Color.from_str(
            "#5865F2"
        )
    )

    sparks = data["blue_sparks"]

    embed.add_field(
        name="📌 Recommendation",
        value=sparks["recommendation"],
        inline=False
    )

    if sparks["note"]:

        embed.add_field(
            name="📝 Note",
            value=sparks["note"],
            inline=False
        )

    embed.set_footer(
        text=(
            "Diamond Fanmade • Timeline • Not affiliated with Cygames"
        )
    )

    return embed


# ============================================================
# SUPPORT CARDS
# ============================================================

def format_support_cards_embed(
    data,
    style
):

    embed = discord.Embed(
        title=f"🃏 Support Cards • {style}",
        color=discord.Color.from_str(
            "#5865F2"
        )
    )

    type_emoji = {
        "Speed": "👟",
        "Stamina": "❤️",
        "Power": "💪",
        "Wit": "🧠",
        "Guts": "🔥",
        "Pal": "🤝"
    }

    selected_deck = None

    for deck in data["sample_decks"]:

        if deck["style"] == style:

            selected_deck = deck
            break

    if selected_deck is None:

        embed.description = (
            "❌ Data Support Cards "
            "tidak ditemukan."
        )

        return embed

    cards_text = []

    for card in selected_deck["stamina_setup"]:

        character = card["character"]
        rarity = card["rarity"]
        card_type = card["type"]

        emoji = type_emoji.get(
            card_type,
            "🃏"
        )

        cards_text.append(
            f"{emoji} **{character}** — {rarity}"
        )

    if not cards_text:

        cards_text.append(
            "Tidak ada data Support Cards."
        )

    embed.add_field(
        name=f"📌 {style}",
        value="\n".join(
            cards_text
        ),
        inline=False
    )

    embed.set_footer(
        text=(
            "Diamond Fanmade • Timeline • Not affiliated with Cygames"
        )
    )

    return embed


# ============================================================
# PARENT DECK EMBED
# ============================================================

def format_parent_deck_embed(
    data,
    style
):

    embed = discord.Embed(
        title=f"🧬 Parent Deck • {style}",
        color=discord.Color.from_str(
            "#5865F2"
        )
    )

    type_emoji = {
        "Speed": "👟",
        "Stamina": "❤️",
        "Power": "💪",
        "Wit": "🧠",
        "Guts": "🔥",
        "Pal": "🤝"
    }

    selected_deck = None

    for deck in data["parent_decks"]:

        if deck["style"] == style:
            selected_deck = deck
            break

    if selected_deck is None:

        embed.description = (
            "❌ Data Parent Deck tidak ditemukan."
        )

        return embed

    cards_text = []

    for card in selected_deck["support_cards"]:

        character = card["character"]
        rarity = card["rarity"]
        card_type = card["type"]

        emoji = type_emoji.get(
            card_type,
            "🃏"
        )

        cards_text.append(
            f"{emoji} **{character}** — {rarity}"
        )

    if cards_text:

        embed.add_field(
            name="🃏 Support Cards",
            value="\n".join(cards_text),
            inline=False
        )

    sparks = selected_deck.get(
        "recommended_sparks",
        []
    )

    if sparks:

        sparks_text = []

        for spark in sparks:

            sparks_text.append(
                f"• {spark['name']}"
            )

        embed.add_field(
            name="🌱 Recommended Skills",
            value="\n".join(sparks_text),
            inline=False
        )

    embed.set_footer(
        text=(
            "Diamond Fanmade • Timeline • Not affiliated with Cygames"
        )
    )

    return embed


# ============================================================
# SKILL VIEW
# ============================================================

class SkillView(discord.ui.View):

    def __init__(self, data):

        super().__init__(
            timeout=None
        )

        self.data = data

    # ========================================================
    # GREEN SKILL
    # ========================================================

    @discord.ui.button(
        label="Green Skill",
        emoji="🌱",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def green_skill(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_skill_embed(
            self.data["green_skills"],
            "🌱 Green Skills"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # ACCELERATION
    # ========================================================

    @discord.ui.button(
        label="Acceleration",
        emoji="⚡",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def acceleration_skill(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_skill_embed(
            self.data["acceleration_skills"],
            "⚡ Acceleration Skills"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # SPEED
    # ========================================================

    @discord.ui.button(
        label="Speed",
        emoji="👟",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def speed_skill(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_skill_embed(
            self.data["speed_skills"],
            "👟 Speed Skills"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # RECOVERY
    # ========================================================

    @discord.ui.button(
        label="Recovery",
        emoji="❤️",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def recovery_skill(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_skill_embed(
            self.data["recovery_skills"],
            "❤️ Recovery Skills"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # DEBUFF
    # ========================================================

    @discord.ui.button(
        label="Debuff",
        emoji="😈",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def debuff_skill(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_skill_embed(
            self.data["debuff_skills"],
            "😈 Debuff Skills"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # BACK
    # ========================================================

    @discord.ui.button(
        label="Back",
        emoji="⬅️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_guide_overview(
            self.data
        )

        await interaction.response.edit_message(
            embed=embed,
            view=GuideView(
                self.data
            )
        )


# ============================================================
# SUPPOCARD VIEW
# ============================================================

class SupportCardView(discord.ui.View):

    def __init__(self, data):

        super().__init__(
            timeout=None
        )

        self.data = data

    # ========================================================
    # BUDGET
    # ========================================================

    @discord.ui.button(
        label="Budget",
        emoji="📌",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def budget(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_support_cards_embed(
            self.data,
            "Budget"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # FRONT
    # ========================================================

    @discord.ui.button(
        label="Front",
        emoji="📌",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def front(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_support_cards_embed(
            self.data,
            "Front"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # PACE
    # ========================================================

    @discord.ui.button(
        label="Pace",
        emoji="📌",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def pace(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_support_cards_embed(
            self.data,
            "Pace"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # LATE
    # ========================================================

    @discord.ui.button(
        label="Late",
        emoji="📌",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def late(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_support_cards_embed(
            self.data,
            "Late"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # END
    # ========================================================

    @discord.ui.button(
        label="End",
        emoji="📌",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def end(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_support_cards_embed(
            self.data,
            "End"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # BACK
    # ========================================================

    @discord.ui.button(
        label="Back",
        emoji="⬅️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_guide_overview(
            self.data
        )

        await interaction.response.edit_message(
            embed=embed,
            view=GuideView(
                self.data
            )
        )


# ============================================================
# PARENT DECK VIEW
# ============================================================

class ParentDeckView(
    discord.ui.View
):

    def __init__(
        self,
        data
    ):

        super().__init__(
            timeout=None
        )

        self.data = data

    @discord.ui.button(
        label="Front",
        emoji="📌",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def front(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.defer()

        embed = format_parent_deck_embed(
            self.data,
            "Front"
        )

        await interaction.edit_original_response(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="Pace",
        emoji="📌",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def pace(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.defer()

        embed = format_parent_deck_embed(
            self.data,
            "Pace"
        )

        await interaction.edit_original_response(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="Late",
        emoji="📌",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def late(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.defer()

        embed = format_parent_deck_embed(
            self.data,
            "Late"
        )

        await interaction.edit_original_response(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="End",
        emoji="📌",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def end(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.defer()

        embed = format_parent_deck_embed(
            self.data,
            "End"
        )

        await interaction.edit_original_response(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="Back",
        emoji="⬅️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_guide_overview(
            self.data
        )

        await interaction.response.edit_message(
            embed=embed,
            view=GuideView(
                self.data
            )
        )


# ============================================================
# GUIDE VIEW
# ============================================================

class GuideView(discord.ui.View):

    def __init__(self, data):

        super().__init__(
            timeout=None
        )

        self.data = data

    # ========================================================
    # OVERVIEW
    # ========================================================

    @discord.ui.button(
        label="Overview",
        emoji="🏠",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def overview(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_guide_overview(
            self.data
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # SKILLS
    # ========================================================

    @discord.ui.button(
        label="Skills",
        emoji="🌱",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def skills(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="🌱 Skills",
            description=(
                "Pilih kategori skill "
                "yang ingin kamu lihat."
            ),
            color=discord.Color.from_str(
                "#5865F2"
            )
        )

        embed.set_author(
            name=(
                "Diamond Fanmade • Guide"
            )
        )

        embed.set_footer(
            text=(
                "Diamond Fanmade • Timeline • Not affiliated with Cygames"
            )
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SkillView(
                self.data
            )
        )

    # ========================================================
    # BLUE SPARKS
    # ========================================================

    @discord.ui.button(
        label="Blue Sparks",
        emoji="🔵",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def blue_sparks(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = format_blue_sparks_embed(
            self.data
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # SUPPORT CARDS
    # ========================================================

    @discord.ui.button(
        label="Support Cards",
        emoji="🃏",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def support_cards(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
    
        embed = discord.Embed(
            title="🃏 Support Cards",
            description=(
                "Pilih style untuk melihat "
                "rekomendasi Support Cards."
            ),
            color=discord.Color.from_str(
                "#5865F2"
            )
        )
    
        embed.set_author(
            name=(
                "Diamond Fanmade • Guide"
            )
        )
    
        embed.set_footer(
            text=(
                "Diamond Fanmade • Timeline • Not affiliated with Cygames"
            )
        )
    
        await interaction.response.edit_message(
            embed=embed,
            view=SupportCardView(
                self.data
            )
        )


    # ========================================================
    # PARENT DECKS
    # ========================================================

    @discord.ui.button(
        label="Parent Decks",
        emoji="🧬",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def parent_decks(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="🧬 Parent Decks",
            description=(
                "Pilih style untuk melihat "
                "rekomendasi Parent Deck."
            ),
            color=discord.Color.from_str(
                "#5865F2"
            )
        )

        embed.set_author(
            name=(
                "Diamond Fanmade • Guide"
            )
        )

        embed.set_footer(
            text=(
                "Diamond Fanmade • Timeline • Not affiliated with Cygames"
            )
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ParentDeckView(
                self.data
            )
        )

