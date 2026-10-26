"""Boss pages for the Field Guide.

Stats, abilities and drops come from the Bestiary tab of the public "RCMC Wiki Data" sheet (the
snapshot in assets/wiki-data.js at build time, then live from the sheet when the page loads).
Only the extras that aren't in the sheet live here: where the boss is in the story, and fight tips.
A Bestiary row with Rank "Boss" gets a page even if it isn't listed here.
"""

BOSSES = {
    "Spider-Rat Queen": {
        "story": ('Arc 1, Quest 4: Into the Depths', "quests.html#walkthroughs"),
        "tips": [
            "Follow the glowing crystals down through the Civic Sewers to reach her nest.",
            "Watch chat for the &#9888; warning before each special move, then step aside.",
            "When she flees to her nest at 40%, go after her: she heals while her brood holds you off.",
            "Bring friends. She gets more health per player, but everyone who does 10% of the damage gets their own drops.",
        ],
    },
    "Pitmaster Jax": {
        "story": ('Arc 1, Quest 9: Cut the Supply Line', "quests.html#walkthroughs"),
        "tips": [
            "When he raises his foot, jump: that's Seismic Slam.",
            "At half health his crew joins in and he can't be hurt for 6 seconds. Deal with the crew first.",
            "Earth Catapult bursts the ground under you. Keep moving.",
            "Earthbenders: his Scroll: Catapult (15%) teaches Catapult before Tier II.",
        ],
    },
}
