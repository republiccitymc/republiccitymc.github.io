"""Bending data for the wiki: every move, every subelement.

tools/build.py reads this to make:
  - a page per move        (move-<slug>.html)
  - a page per subelement  (sub-<slug>.html)
  - the Moves by Tier table on Bending & Tiers   (<!-- moves-table --> in pages/bending.html)
  - each path page's Abilities table              (<!-- moves:earth --> etc. in pages/<path>.html)

Edit a move here, run python3 tools/build.py, commit. Nothing else to touch.

MOVE fields
  name    in-game name (what /b bind uses, with spaces)
  path    earth | water | fire | chi | wm
  tier    I | II | III | S   (S = Tier star); SC = scroll-only, BX = boss drops and side quests (listed under the table)
  sub     subelement key, or None for the path's own moves
  combo   True if it's performed by chaining other moves
  later   True if it isn't on the server yet (no page, shown as "coming later")
  what    one or two sentences: what it does
  use     list of (label, how) steps; label may be "" for a single step
  get     how you learn it (leave out for the default, which comes from the tier/trainer rules below)
  scroll  for scroll-only moves: {"price": Yuans, "seller": "...", "needs": "..."} (all optional); tier is then "SC"
"""

PATHS = {
    "earth": {"name": "Earthbending", "page": "earthbending", "trainers": {"II": "Foreman Akatsuchi", "III": "Penga", "S": "Toph Beifong"}},
    "water": {"name": "Waterbending", "page": "waterbending", "trainers": {"II": "Young Kya", "III": "Master Kanok", "S": "Katara"}},
    "fire": {"name": "Firebending", "page": "firebending", "trainers": {"II": "Partner Homura", "III": "Royal Academy Elite", "S": "Fire Lord Zuko / General Iroh"}},
    "chi": {"name": "Chi Blocking", "page": "chi-blocking", "trainers": {"II": "Acrobat Lee", "III": "Ty Lee", "S": "Suki"}},
    "wm": {"name": "Weapons Master", "page": "weapons-master", "trainers": {"II": "Young Bumi", "III": "Mai", "S": "Sokka"}},
}

TIERS = {"I": ("Tier I", "Start"), "II": ("Tier II", "50 QP"), "III": ("Tier III", "250 QP"), "S": ("Tier &#9733;", "500 QP")}
# Scroll-only moves: no tier teaches them; the scroll drops from a boss or comes from a quest or vendor, and works at any tier.
SCROLL_TIER = ("Scrolls", "Drops &amp; Vendors")
SCROLL_SELLER = "Weapons Vendor TenTen"
# Moves you get from boss drops and side quests instead of a tier: tier "BX", listed under the table.
BONUS_TIER = ("Boss Drops & Side Quests", "Bonus")

# Subelements. Order inside each element is the order they're listed in.
SUBS = {
    "metal": {"name": "Metal", "path": "earth", "first": "II",
              "lead": "Toph Beifong's own invention, and the badge of her police force. Metalbenders sense the bits of earth left in refined metal.",
              "bends": "Iron, gold and copper, ore and block.",
              "teacher": "Pick Metal after Foreman Akatsuchi's jobs and he sends you to Young Lin Beifong, who teaches it herself."},
    "sand": {"name": "Sand", "path": "earth", "first": "II",
             "lead": "Sandbenders shift loose sand and sandstone, the way the Sandbenders of the Si Wong Desert ride the dunes.",
             "bends": "Sand, red sand, sandstone and red sandstone.",
             "teacher": "Pick Sand after Foreman Akatsuchi's jobs and he sends you to Pakura, a Si Wong caravan trader at the stalls by the Sparring Grounds."},
    "lava": {"name": "Lava", "path": "earth", "first": "III",
             "lead": "Rare and feared. Lavabenders melt earth into magma and turn it back to stone.",
             "bends": "Lava, and earth melted into magma.",
             "teacher": "Penga points you to a lavabender once you reach Tier III."},
    "ice": {"name": "Ice", "path": "water", "first": "II",
            "lead": "Freezing water into blades, spikes and platforms: the Northern Water Tribe's oldest art.",
            "bends": "Ice and packed ice.",
            "teacher": "Pick Ice after Young Kya's first lesson and she sends you to Haku at Maru's Butchery. Master Kanok teaches more at Tier III."},
    "healing": {"name": "Healing", "path": "water", "first": "II",
                "lead": "Water's gentlest use. Katara is the greatest healer alive, and her daughter is learning fast.",
                "bends": "Water you already carry, to close wounds.",
                "teacher": "Pick Healing after Young Kya's first lesson and she teaches it herself."},
    "plant": {"name": "Plant", "path": "water", "first": "II",
              "lead": "Drawing the water out of living things, the way the Foggy Swamp Tribe does.",
              "bends": "Plants as a water source: leaves, grass, flowers, vines, moss, cactus, sugar cane, melons and pumpkins.",
              "teacher": "Pick Plant after Young Kya's first lesson and she sends you to Moku, a Foggy Swamp Tribe plantbender by the Public Library."},
    "lightning": {"name": "Lightning", "path": "fire", "first": "II",
                  "lead": "Cold-blooded fire. In Republic City, lightning-benders are starting to find work in the power plants.",
                  "bends": "Lightning, made from your own chi.",
                  "teacher": "The Royal Academy Elite teaches it."},
    "combustion": {"name": "Combustion", "path": "fire", "first": "II",
                   "lead": "Very rare: an explosion focused through the mind. Combustion-benders are feared for good reason.",
                   "bends": "Explosive blasts, made from your own chi.",
                   "teacher": "The Royal Academy Elite teaches it."},
}

# How many subelements you have at each tier, per element (shown on Bending & Tiers and the sub pages).
SUB_RULES = {
    "earth": "One subelement at Tier II: Metal or Sand, your pick after Foreman Akatsuchi's jobs. A second at Tier III, where Lava opens too. All three at Tier &#9733;.",
    "water": "One subelement at Tier II: Healing, Ice or Plant, your pick after Young Kya's first lesson. A second at Tier III. All three at Tier &#9733;.",
    "fire": "Pick Lightning or Combustion at Tier II, and learn the other at Tier III.",
}
SUB_FIRST_TIER = {"earth": "II", "water": "II", "fire": "II"}  # earliest subelement per element; each sub's own "first" wins


def M(name, path, tier, what, use, sub=None, combo=False, later=False, get=None, scroll=None):
    return {"name": name, "path": path, "tier": tier, "what": what, "use": use, "sub": sub,
            "combo": combo, "later": later, "get": get, "scroll": scroll}


def H(name):
    """Default controls step: point to ProjectKorra's own help."""
    return [("", f"Run <code>/b help {name.replace(' ', '')}</code> in game for the controls.")]


def C(seq):
    return [("", seq)]


MOVES = [
    # ---------------- EARTH ----------------
    M("Earth Blast", "earth", "I", "Pull a chunk of earth up and throw it. Quick, and you can steer it after it's thrown.",
      [("", "Tap sneak at an earthbendable block, then left-click to throw it. Left-click again to steer it. You can also redirect another earthbender's blast.")]),
    M("Raise Earth", "earth", "I", "Raise a pillar or a wall of earth: for cover, to block a move, or to lift yourself.",
      [("Pillar", "Left-click an earthbendable block."), ("Wall", "Tap sneak on an earthbendable block.")]),
    M("Collapse", "earth", "I", "Drop earth down into the space beneath it. Deadly in tunnels.",
      [("", "Left-click an earthbendable block with space under it. Tap sneak to collapse several at once.")]),
    M("Earth Armor", "earth", "I", "Wrap yourself in earth for extra hearts. It breaks once they're gone.",
      [("", "Tap sneak at earthbendable blocks to pull them onto you. Hold sneak and left-click to take it off.")]),
    M("Earth Tunnel", "earth", "I", "Dig through earth: escape routes, shortcuts, your own caves.",
      [("", "Hold sneak while looking at earth. Let go, or look at something else, to stop.")]),
    M("Shockwave", "earth", "II", "Send a ring of earth out in every direction, hitting everyone around you.",
      [("Ring", "Hold sneak until you see particles, then release."), ("Cone", "Left-click instead of releasing to send it forward only."),
       ("Fall", "Land from a great height with Shockwave selected and it fires by itself.")],
      get="Foreman Akatsuchi's quest <b>Lost in Translation</b>, after The Old Mines."),
    M("Catapult", "earth", "II", "Launch yourself through the air on a burst of earth.",
      [("", "Hold sneak until you hear a sound, then release to launch where you're looking. Left-click for a smaller hop.")],
      get="Foreman Akatsuchi's quest <b>The Old Mines</b>, at Tier II. <b>Scroll: Catapult</b> from Pitmaster Jax teaches it earlier."),
    M("Earth Line", "earth", "II", "Send a steerable ridge of earth along the ground at a target.", H("Earth Line"),
      get="Foreman Akatsuchi teaches it himself at the end of <b>Lost in Translation</b>: his own trick for laying out a street."),
    M("Metal Clips", "earth", "II", "Throw iron ingots that lock around a target as armor, then move them where you want.",
      [("Clips", "Carry iron ingots. Left-click to throw one. Once enough clips are on a target, hold sneak to control them and release to throw them."),
       ("Magnet", "Hold sneak to pull iron ingots to you.")], sub="metal",
      get="Young Lin Beifong's quest <b>The Iron Vein</b>: pull the iron out of the old mine's ore, and she shows you how to throw it."),
    M("Extraction", "earth", "II", "Pull the metal out of ore, sometimes two or three times over.",
      [("", "Tap sneak at an ore block.")], sub="metal",
      get="Young Lin Beifong's quest <b>Hanging by a Cable</b>, if you pick Metal after Foreman Akatsuchi's jobs. She opens up your Metal at the same time."),
    M("Sand Blast", "earth", "II", "Blast sand at a target to damage and blind them.",
      [("", "Tap sneak at a sand block (within 8 blocks), then left-click in a direction.")], sub="sand",
      get="Pakura's job <b>Sand in Their Eyes</b> at her caravan by the Sparring Grounds, if you pick Sand after Foreman Akatsuchi's jobs: dig her barrels out of the sand with your earth moves, and she shows you how sand really moves."),
    M("Earth Smash", "earth", "III", "Raise a boulder, then throw it or ride it.",
      [("Smash", "Hold sneak until particles appear, release at an earthbendable block, hold sneak on the boulder to grab it, then left-click to throw."),
       ("Ride", "Hold sneak and right-click the boulder, then look where you want to go.")]),
    M("Earth Pillars", "earth", "III", "Pillars burst up under everyone near you and throw them into the air.",
      [("", "Shockwave (tap sneak), Shockwave (hold sneak), then Catapult (release sneak). Landing from high up on Catapult also works.")],
      combo=True),
    M("Earth Surf", "earth", "III", "Ride a rolling wave of earth across the ground.", H("Earth Surf"), later=True),
    M("Magnet Shield", "earth", "III", "Repel arrows, metal projectiles, and foes in metal gear.", H("Magnet Shield"), sub="metal", later=True),
    M("Magma Shot", "earth", "III", "Fire balls of magma, up to three in a row.", H("Magma Shot"), sub="lava"),
    M("Lava Manipulation", "earth", "III", "Melt earth into a stream of lava and fling it.", H("Lava Manipulation"), sub="lava"),
    M("Tremorsense", "earth", "SC", "Feel the ground around you. In the dark, the earth under your feet lights up for you only.",
      [("", "Stand on earth in the dark and it works on its own. Left-click to spot hollow pockets nearby.")], scroll={"price": 60, "seller": SCROLL_SELLER}),
    M("Crevice", "earth", "S", "Rip a deep crevice open in the ground.", C("Collapse, Shockwave, Shockwave."), combo=True, later=True),
    M("Metal Cables", "earth", "S", "Fire wrist-mounted metal cables to grapple and control targets.", [], sub="metal", later=True),
    M("Lava Flow", "earth", "S", "Turn the ground around you into lava, or cool lava back into stone.",
      [("Flow", "Hold sneak and the lava spreads out. Tap sneak to turn it back."), ("Pool", "Left-click to melt earth into a pool."),
       ("Solidify", "Left-click lava to turn it to stone.")], sub="lava"),
    M("Lava Disc", "earth", "S", "Form a spinning disc of lava, throw it, and call it back.", H("Lava Disc"), sub="lava", later=True),
    M("Earth Grab", "earth", "SC", "Root a target to the spot, or drag items lying on earth over to you.",
      [("Grab", "Left-click toward the target."), ("Drag", "Sneak to pull nearby items to you."),
       ("Escape", "If you're caught, right-click the trap a few times, or get moved by another earth move.")], scroll={"price": 60, "seller": SCROLL_SELLER}),
    M("Earth Dome", "earth", "SC", "Close yourself, or someone else, inside a dome of earth.",
      [("Yourself", "Raise Earth (right-click), then Shockwave (right-click)."), ("Someone else", "Raise Earth (right-click), then Shockwave (left-click).")], scroll={"price": 80, "seller": SCROLL_SELLER, "needs": "Shockwave (Tier II)"}),
    M("Earth Kick", "earth", "SC", "Kick a spray of earth chunks at a foe.", H("Earth Kick"), scroll={}, later=True),
    M("Earth Shard", "earth", "SC", "Pull up small earth shards, hold several, and launch them one by one.", H("Earth Shard"), scroll={}, later=True),
    M("Mud Surge", "earth", "SC", "Hurl a wave of mud that knocks back, damages, and can blind.", H("Mud Surge"), scroll={}, later=True),
    M("Metal Hook", "earth", "SC", "Fire metal grappling cables to swing across the city.", H("Metal Hook"), sub="metal", scroll={}, later=True),
    M("Metal Fragments", "earth", "SC", "Tear metal fragments off blocks and fire them.", H("Metal Fragments"), sub="metal", scroll={}, later=True),
    M("Metal Shred", "earth", "SC", "Peel open a metal wall to pass through.", H("Metal Shred"), sub="metal", scroll={}, later=True),
    M("Lava Flux", "earth", "SC", "Send a wave of molten lava along the ground.", H("Lava Flux"), sub="lava", scroll={}, later=True),
    M("Fissure", "earth", "SC", "Open a widening crack of lava in the ground and close it again.", H("Fissure"), sub="lava", scroll={}, later=True),
    M("Magma Blast", "earth", "SC", "Fire explosive balls of magma.", C("Earth Blast, then Lava Flow."), sub="lava", combo=True, scroll={"needs": "Lava Flow (Lava, Tier &#9733;)"}, later=True),
    M("Lava Throw", "earth", "SC", "Scoop lava from a pool and hurl it in splashes.", H("Lava Throw"), sub="lava", scroll={}, later=True),
    # ---------------- WATER ----------------
    M("Water Manipulation", "water", "I", "Shoot a fast jet of water. Steer it, or take over someone else's.",
      [("", "Tap sneak at a water source, then left-click to send it. Left-click again to change its direction.")]),
    M("Surge", "water", "I", "A wave that knocks people back, or a shield of water that follows your gaze.",
      [("Surge", "Tap sneak at a water source, then click a direction. Tap sneak again before it hits to freeze the target in ice."),
       ("Shield", "Left-click a water source, then hold sneak while looking up. Left-click to freeze the shield.")]),
    M("Torrent", "water", "I", "A whip of water that drags and hurts whatever it hits, or a wave that pushes everyone away.",
      [("Torrent", "Left-click a water source and hold sneak to form it, then left-click to send it."),
       ("Wave", "Left-click a water source and hold sneak, then release to push everyone back.")]),
    M("Water Spout", "water", "I", "Ride a column of water. Your best way to get around, chase or escape.",
      [("Spout", "Left-click to start. Hold jump to rise, sneak to drop. Left-click to stop."),
       ("Hop", "While on the spout, hold sneak and left-click to jump forward."),
       ("Wave", "Left-click a water source, hold sneak, then release to ride a wave.")]),
    M("Water Bubble", "water", "I", "Push water back to make a pocket of air underwater.",
      [("", "Hold sneak near water. Click for a short bubble.")]),
    M("Octopus Form", "water", "II", "Eight arms of water around you: block, and whip anyone close.",
      [("", "Left-click a water source, then hold sneak to form the tentacles. Left-click to whip.")],
      get="Young Kya's first quest, <b>Lost in the Sewers</b>, once you reach Tier II (50 QP). She teaches it together with Water Flow."),
    M("Water Flow", "water", "II", "Steer a powerful stream of water that can carry you, and anyone in it, wherever you look.",
      [("", "Water Manipulation (tap sneak), Torrent (tap sneak), Torrent (hold sneak), then Water Manipulation (release sneak)."),
       ("Pull back", "Hold sneak."), ("Freeze", "Left-click with Water Manipulation, if you can icebend.")], combo=True,
      get="Young Kya's first quest, <b>Lost in the Sewers</b>, once you reach Tier II (50 QP). She teaches it together with Octopus Form."),
    M("Phase Change", "water", "II", "Freeze water into ice to stand on, or melt ice back.",
      [("Freeze", "Left-click water."), ("Melt", "Hold sneak while looking at ice.")], sub="ice",
      get="Haku's quest at Maru's Butchery, if you pick Ice after Young Kya's first lesson. He teaches it together with Ice Spike."),
    M("Ice Spike", "water", "II", "Fire a shard of ice, or raise spikes from ice under your enemies. Both slow what they hit.",
      [("Blast", "Tap sneak at a water source, then left-click to fire."), ("Spike", "Near ice, tap sneak. Or left-click one ice block.")],
      sub="ice", get="Haku's quest at Maru's Butchery, if you pick Ice after Young Kya's first lesson. He teaches it together with Phase Change."),
    M("Healing Waters", "water", "II", "Heal yourself or someone else with water.",
      [("Yourself", "Hold sneak while standing in water or carrying water bottles."),
       ("Someone else", "Sneak and right-click them, and keep looking at them.")], sub="healing",
      get="Young Kya's quest <b>Great-Gran's Necklace</b>, if you pick Healing after Lost in the Sewers."),
    M("Water Gimbal", "water", "III", "Two spinning rings of water fired at enemies.", C("Torrent, Torrent, Water Manipulation."), combo=True, later=True),
    M("Maelstrom", "water", "III", "Create a deep-water whirlpool that drags enemies down.", C("Phase Change, Torrent, Torrent."), combo=True, later=True),
    M("Ice Blast", "water", "III", "A fast, hard shot of ice. Good for finishing a fight.",
      [("", "Tap sneak at an ice block, then click a direction.")], sub="ice"),
    M("Ice Bullet", "water", "III", "Punch rapid shards out of a wall of ice.",
      [("", "Water Bubble (tap sneak), then Ice Blast (hold sneak). Wait for the ice to form, then alternate left- and right-clicks.")],
      sub="ice", combo=True),
    M("Razor Leaf", "water", "II", "Pull a leaf out of a plant, hold it sharp and spinning, then throw it. Call it back to throw it again.",
      [("Start", "Hold sneak while looking at a plant: a leaf disc spins up in front of you."),
       ("Throw", "Aim and let go of sneak."),
       ("Call it back", "Sneak again while it's out and it flies back towards you.")], sub="plant",
      get="Moku's quest <b>The Seed Thief</b> by the Public Library, if you pick Plant after Young Kya's first lesson."),
    M("Water Arms", "water", "S", "Two arms of water that punch, grab, pull, grapple and freeze.",
      [("Start", "Tap sneak at a water source. Hold sneak and left-click to stop."),
       ("Use", "Left-click to punch, pull, grapple, grab and throw, or fire ice, depending on the arm's mode.")]),
    M("Frost Breath", "water", "S", "Breathe freezing air that freezes targets in place.", H("Frost Breath"), sub="ice", later=True),
    M("Drain", "water", "S", "Draw water out of nearby plants to fill bottles or fire blasts.", H("Drain"), sub="plant", later=True),
    M("Wake Fishing", "water", "SC", "Waterbend fish straight out of the water.", H("Wake Fishing"), scroll={}, later=True),
    M("Ice Wave", "water", "SC", "Freeze your water wave as you ride it, hurting everything it hits.",
      [("", "Ride a Water Spout wave, then switch to Phase Change and left-click.")], sub="ice", combo=True, scroll={}),
    M("Ice Wall", "water", "SC", "Raise a wall of ice that damages nearby enemies when shattered.", H("Ice Wall"), sub="ice", scroll={}, later=True),
    M("Ice Claws", "water", "SC", "Form ice claws on your fingers to slash or throw.", H("Ice Claws"), sub="ice", scroll={}, later=True),
    # ---------------- FIRE ----------------
    M("Fire Blast", "fire", "I", "Your basic fireball, fast and repeatable. Charge it for a bigger blast.",
      [("Ball", "Left-click."), ("Blast", "Hold sneak until particles appear, then release.")]),
    M("Blaze", "fire", "I", "An arc of fire along the ground, or a ring of it around you.",
      [("Arc", "Left-click."), ("Ring", "Tap sneak.")]),
    M("Fire Jet", "fire", "I", "Blast fire behind you to fly forward. Your escape and your gap-closer.",
      [("", "Left-click to launch where you're looking. Left-click again to stop.")]),
    M("Heat Control", "fire", "I", "Put out fire, melt ice, cool lava and cook food.",
      [("Extinguish", "Tap sneak."), ("Melt", "Left-click ice."), ("Solidify", "Stand still and hold sneak at lava."),
       ("Cook", "Put raw food in this slot and hold sneak.")]),
    M("Illumination", "fire", "I", "A small flame that lights the dark around you.",
      [("", "Left-click to turn it on or off.")]),
    M("Fire Burst", "fire", "II", "A sphere of fire bursting out in every direction.",
      [("", "Hold sneak until particles appear, then release. Left-click instead to send it one way.")],
      get="Partner Homura's quest <b>Corporate Synergy &amp; Property Values</b> behind the Caldera Capital tower, at Tier II."),
    M("Fire Manipulation", "fire", "II", "Paint a wall of fire, then throw it.",
      [("", "Hold sneak and move your view to place fire, then left-click to send it out.")],
      get="Partner Homura's quest <b>Brand Visibility &amp; High-Altitude Marketing</b>, after Corporate Synergy &amp; Property Values."),
    M("Fire Kick", "fire", "II", "A short arc of fire off your foot.",
      [("", "Fire Blast, Fire Blast, hold sneak, Fire Blast.")], combo=True,
      get="It comes with Tier II (50 QP) on its own: no quest needed."),
    M("Fire Punch", "fire", "II", "Charge your fist with fire to ignite the next enemy you hit.", H("Fire Punch"),
      get="Partner Homura's quest <b>Corporate Synergy &amp; Property Values</b> behind the Caldera Capital tower, at Tier II."),
    M("Fire Shots", "fire", "II", "Summon several small fireballs and fire them one by one.", H("Fire Shots"),
      get="Partner Homura's quest <b>Brand Visibility &amp; High-Altitude Marketing</b>, after Corporate Synergy &amp; Property Values."),
    M("Wall of Fire", "fire", "III", "Raise a wall of fire that burns and pushes back anyone who touches it.",
      [("", "Left-click where you want the wall.")]),
    M("Jet Blast", "fire", "III", "An explosive Fire Jet that flies faster.",
      [("", "Fire Jet (tap sneak), Fire Jet (tap sneak), Fire Shield (tap sneak), Fire Jet.")], combo=True),
    M("Jet Blaze", "fire", "III", "A Fire Jet that burns everyone you fly past.",
      [("", "Fire Jet (tap sneak), Fire Jet (tap sneak), Blaze (tap sneak), Fire Jet.")], combo=True),
    M("Fire Wheel", "fire", "III", "A wheel of fire that rolls along the ground a long way.",
      [("", "Fire Shield (hold sneak), right-click a block in front of you twice, switch to Blaze, release sneak.")], combo=True),
    M("Lightning", "fire", "III", "Charge lightning and fire it. It can stun.",
      [("", "Hold sneak until particles appear, then release to fire where you're looking.")], sub="lightning"),
    M("Combustion", "fire", "III", "A focused blast that explodes on impact, from far away.",
      [("", "Tap sneak to fire. It explodes when it hits, or left-click to set it off early.")], sub="combustion"),
    M("Fire Breath", "fire", "S", "Breathe a sustained stream of dragon fire.", H("Fire Breath"), later=True),
    M("Lightning Redirection", "fire", "S", "Absorb incoming lightning and redirect it back out.", [], sub="lightning", later=True),
    M("Lightning Burst", "fire", "S", "Charge a sphere of lightning and release it to shock everyone nearby.", H("Lightning Burst"), sub="lightning", later=True),
    M("Fire Shield", "fire", "SC", "A shield of fire that blocks projectiles and bending.",
      [("", "Hold sneak. Left-click for a quick shield that sets anyone inside it alight.")], scroll={"price": 60, "seller": SCROLL_SELLER}),
    M("Fire Spin", "fire", "SC", "A ring of fire that throws everyone near you back.",
      [("", "Fire Blast, Fire Blast, Fire Shield (left-click), Fire Shield (tap sneak).")], combo=True, scroll={"price": 80, "seller": SCROLL_SELLER, "needs": "Fire Shield (also a scroll)"}),
    M("Fire Ski", "fire", "SC", "Skate rapidly along the ground propelled by fire jets.", H("Fire Ski"), scroll={}, later=True),
    M("Fire Ball", "fire", "SC", "Throw a single fireball projectile.", H("Fire Ball"), scroll={}, later=True),
    M("Discharge", "fire", "SC", "Fire rapid bolts of electricity from the fingertips that can stun.", H("Discharge"), sub="lightning", scroll={}, later=True),
    # ---------------- CHI BLOCKING ----------------
    M("Quick Strike", "chi", "I", "A fast jab that can block a bender's chi.", [("", "Left-click a player.")]),
    M("Swift Kick", "chi", "I", "A jumping kick that can block a bender's chi.", [("", "Jump and left-click a player.")]),
    M("Acrobat Stance", "chi", "I", "Faster, higher jumps and a better chance to block chi. Makes you hungry faster.",
      [("", "Left-click to switch it on or off.")]),
    M("High Jump", "chi", "I", "Leap straight up: dodge, or get onto something.", [("", "Left-click while on the ground.")]),
    M("Rapid Punch", "chi", "II", "A flurry of punches for heavy damage.", [("", "Punch a player.")]),
    M("Paralyze", "chi", "II", "Freeze a target where they stand for a moment.", [("", "Punch a player.")],
      get="Acrobat Lee's quest <b>Pipa's Great Escape</b>, at Tier II."),
    M("Smokescreen", "chi", "II", "A smoke bomb that blinds everyone near where it lands.", [("", "Left-click to throw it.")],
      get="Acrobat Lee's quest <b>Catch Me If You Can</b>, after Pipa's Great Escape."),
    M("Bola", "chi", "III", "Throw a bola that wraps a target and slows them, which sets up everything else.",
      [("", "Run <code>/b help Bola</code> in game for the controls.")]),
    M("Immobilize", "chi", "III", "Lock a target in place for several seconds.",
      [("", "Quick Strike, Swift Kick, Quick Strike, Quick Strike.")], combo=True),
    M("Warrior Stance", "chi", "III", "Hit harder, but take a bit more damage.", [("", "Left-click to switch it on or off.")]),
    M("Backstab", "chi", "S", "Deliver a heavy chi-blocking strike from behind.", H("Backstab"), later=True),
    # ---------------- WEAPONS MASTER ----------------
    M("Leaping Strike", "wm", "I", "Leap forward and bring your weapon down, knocking back everyone near where you land. Damage comes from the weapon in your hand.",
      [("", "Hold a weapon and run <code>/b help LeapingStrike</code> in game for the controls.")]),
    M("Weapon Throw", "wm", "I", "Throw your weapon. It hits with the weapon's own damage and effects, then flies back to your hand.",
      [("", "Hold a weapon and run <code>/b help WeaponThrow</code> in game for the controls.")]),
    M("Battle Stance", "wm", "I", "Plant your feet: more strength and resistance, but you move slower.",
      [("", "Run <code>/b help BattleStance</code> in game for the controls.")]),
    M("Dagger Throw", "wm", "II", "Rapid-fire thrown daggers at range.", H("Dagger Throw"), later=True),
    M("Blade Parry", "wm", "II", "Deflect incoming projectiles and basic bending attacks with a weapon.", [], later=True),
    M("Hook Sword Sweep", "wm", "II", "Link twin hook swords to sweep or pull foes in an arc.", [], later=True),
    M("Kyoshi Fan Counter", "wm", "III", "Catch an incoming rush and redirect the attacker into a ground slam.", [], later=True),
    M("Boomerang Ricochet", "wm", "III", "Throw a curved boomerang that arcs around cover and returns.", [], later=True),
    M("Dual Dao Whirlwind", "wm", "III", "Spin with twin broadswords to cleave nearby foes and deflect bolts.", [], later=True),
    M("Way of the White Lotus", "wm", "S", "Execute an unreactable master draw-slash that pierces armor.", [], later=True),
    M("Pinpoint Stiletto Pin", "wm", "S", "Throw precision stilettos to pin a target's clothing to the ground or wall.", [], later=True),
]


def slug(name):
    return name.lower().replace(" ", "-")


def default_get(m):
    p = PATHS[m["path"]]
    t = m["tier"]
    if m.get("scroll") is not None:
        sc = m["scroll"]
        who = (f"{p['name'].lower().replace('bending', 'benders')} only" if m["path"] in ("earth", "fire", "water") else p["name"])
        if sc.get("seller"):
            price = f" for {sc['price']} Yuans" if sc.get("price") else ""
            txt = f"Buy <b>Scroll: {m['name']}</b> from {sc['seller']} at the Sparring Grounds{price} ({who})."
        elif sc.get("from"):
            txt = f"<b>Scroll: {m['name']}</b> comes from {sc['from']} ({who})."
        else:
            txt = (f"<b>Scroll: {m['name']}</b>, a Technique Scroll. Scrolls drop from bosses and come from quests and "
                   f"vendors ({who}). Where this one comes from isn't decided yet.")
        txt += " Right-click it to learn the move for good, at any tier."
        if sc.get("needs"):
            txt += f" To perform it you also need {sc['needs']}."
        return txt
    if t == "BX":
        return "A bonus move: it comes from a boss drop or a side quest, not from a tier."
    if t == "I":
        return "You start with it. It's already on your hotbar when you create your character."
    tier_name, qp = TIERS[t]
    if m["sub"]:
        s = SUBS[m["sub"]]
        if t == s.get("first", SUB_FIRST_TIER[m["path"]]):
            return f"Learned through a trainer quest once you have <b>{s['name']}</b>. {s['teacher']}"
        return (f"It comes with {tier_name} ({qp}) once you have <b>{s['name']}</b>: you get it automatically when you reach the tier. "
                f"{p['trainers'][t]}'s teacher quests are planned.")
    if t == "II":
        return f"Taught by {p['trainers'][t]}'s quests once you reach {tier_name} ({qp})."
    return (f"It comes with {tier_name} ({qp}): you get it automatically when you reach the tier. "
            f"{p['trainers'][t]}'s teacher quests are planned.")
