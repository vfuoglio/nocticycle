"""Named moons: the "13 moons" systems laid over the lunations.

Each *lunation* (new moon to new moon, see ``lunations.py``) receives a name.
Systems:

* ``anishinaabe`` - the Anishinaabe (Ojibwe) 13-moon names.
* ``wiccan``      - the modern Wiccan / Pagan esbat moon names.
* ``almanac``     - the Algonquin / "colonial hybrid" names popularised by almanacs.
* ``celtic``      - the Celtic Tree Calendar (Robert Graves' 13 tree months).
* ``chinese``     - the Chinese lunar months (true lunar months, with leap months).

Naming rule for the first three (and the tree calendar): a lunation takes the
name of the calendar month (or tree month) in which its *full moon* falls. When
a calendar month has two full moons, the second is the 13th, "leap" moon (a Blue
Moon). The Chinese months are numbered by the Chinese calendar rules.

The texts are short, general summaries written for this project. The
Anishinaabe, Wiccan and Almanac names follow the table supplied for the project
as published, but communities, authors and regions differ: edit them freely.
"""

from datetime import date, timedelta

from . import config as cfg
from .moon_svg import is_southern_hemisphere
from .wheel_icons import icon_inner, icon_svg
from .wheels import SEASONS, _season_css
from .lunations import chinese_lunar_date, chinese_months, lunations


def _m(n, season, icon, meaning, about, en="", alt="", short=None):
    return {"n": n, "en": en, "alt": alt, "season": season, "icon": icon,
            "meaning": meaning, "about": about, "short": short or en or n}


# ---------------------------------------------------------------------------
# Anishinaabe (Ojibwe) living model
# ---------------------------------------------------------------------------

_ANISHINAABE = {
    1: _m("Manidoo Giizis", "winter", "spirit", en="Spirit Moon",
          meaning="Manidoo means spirit or mystery. The first moon of the calendar year falls in the depth of winter, when the world is quiet and the spirit world is felt to be close.",
          about="Midwinter is a time for rest, reflection and for sharing the old stories, which in many communities are told only once the snow has come."),
    2: _m("Mkwa Giizis", "winter", "paw", en="Bear Moon",
          meaning="Mkwa is the bear. The bear sleeps through the cold in its den, and in many teachings it stands for strength, healing and deep rest.",
          about="The cold is at its hardest. It is a time to conserve energy and mend, while the bears, who give birth in their dens, are asleep."),
    3: _m("Ziisbaakdoke Giizis", "spring", "maple", en="Sugar Moon",
          meaning="Ziisbaakdoke means to make sugar: the sap begins to run in the maple trees as the days warm and the nights stay frozen.",
          about="The sugar camps open. Sap is gathered and boiled into syrup and sugar, a central spring harvest and a time when families gather."),
    4: _m("Namebine Giizis", "spring", "fish", en="Sucker Moon",
          meaning="Namebine is the sucker, a fish that swims up the streams to spawn as the ice breaks up.",
          about="Spring fishing begins. Families gather at the rivers for the run, the ice goes out and the geese and ducks return."),
    5: _m("Waawaaskone Giizis", "spring", "blossom", en="Flower Moon",
          meaning="Named for the flowers that blossom as the earth turns green and the first warm weather arrives.",
          about="The land wakes up: wild flowers and medicine plants appear, birds nest and the planting season starts."),
    6: _m("Ode'miin Giizis", "summer", "strawberry", en="Strawberry Moon",
          meaning="Ode'miin is the strawberry, the 'heart berry', the first fruit of the year. In many teachings it is linked to the heart, to healing and to good relationships.",
          about="Early summer: the first berries ripen and are gathered with thanks, and the season of gatherings and ceremonies begins."),
    7: _m("Mskomini Giizis", "summer", "berries", en="Raspberry Moon",
          meaning="Mskomini is the raspberry, the 'red berry', which ripens in the heat of midsummer.",
          about="Berry picking is in full swing. Fruit is gathered and dried to feed the family through the winter."),
    8: _m("Datkaagmin Giizis", "summer", "maple", en="Thimbleberry Moon",
          meaning="Named for the thimbleberry, a soft red berry that ripens in late summer.",
          about="Late summer: the last berries are gathered and the community begins to prepare for the autumn harvests."),
    9: _m("Mdaamiin Giizis", "autumn", "corn", en="Corn Moon",
          meaning="Mdaamiin is corn. The corn is ripe, and in many communities this is also the season of the wild rice harvest.",
          about="Harvest time: corn, squash and beans are brought in, and thanks are given for the year's food."),
    10: _m("Biinaakwe Giizis", "autumn", "falling_leaves", en="Falling Leaves Moon",
           meaning="Named for the leaves that fall from the trees once the colours have turned.",
           about="Hunting and preparing for winter: food is stored, wood is gathered and the camps are readied for the cold."),
    11: _m("Mshkawji Giizis", "autumn", "crystal", en="Freezing Moon",
           meaning="Mshkawji refers to freezing: the shallow waters ice over and the first hard frosts arrive.",
           about="Early winter: lakes freeze, trapping and hunting continue and the long season of storytelling gets closer."),
    12: _m("Manidoo Giizoonhs", "winter", "candle", en="Little Spirit Moon",
           meaning="The 'little' spirit moon, a smaller companion to the Spirit Moon, comes in the last month of the year.",
           about="The longest nights: a time of family, rest and quiet, as the year turns toward its beginning."),
    "leap": _m("Manidoo Giizis", "winter", "blue_moon", en="Big Spirit Moon",
               meaning="The Anishinaabe teachings link the thirteen moons to the thirteen scutes on the back of the turtle, which carries Turtle Island. Here a thirteenth moon appears when a calendar month holds a second full moon.",
               about="A rare extra moon, a pause in the ordinary run of the year, kept for reflection, thanks and spiritual renewal."),
}

# ---------------------------------------------------------------------------
# Wiccan / Pagan esbat moons
# ---------------------------------------------------------------------------

_WICCAN = {
    1: _m("Wolf Moon", "winter", "wolf", alt="Storm Moon",
          meaning="Named for the wolves that howl close to the villages in the hungry heart of winter; also called the Storm Moon for the season's gales.",
          about="Protection, loyalty and instinct. A time to set intentions for the year, clear away what no longer serves and face fears."),
    2: _m("Snow Moon", "winter", "snowflake", alt="Ice Moon",
          meaning="Named for the heaviest snowfalls of the year, when ice lies thick on the land.",
          about="Purification, rest and quiet inner work. Close to Imbolc, it is a time for cleansing and for tending the first spark of hope."),
    3: _m("Worm Moon", "spring", "worm", alt="Seed Moon",
          meaning="The thawing soil brings the earthworms back, and the birds follow them; also called the Seed Moon for the first sowing.",
          about="Growth and planting, in the garden and in your plans. A moon of new beginnings and of fertility."),
    4: _m("Hare Moon", "spring", "hare", alt="Egg Moon",
          meaning="The hare and the egg are old symbols of spring's fertility, linked to the goddess Eostre (Ostara).",
          about="Fertility, balance and new life, as the days grow longer and the light begins to win."),
    5: _m("Flower Moon", "spring", "blossom", alt="Dyad Moon",
          meaning="The land is in blossom. 'Dyad' means a pair, a reference to Beltane and the union of the Goddess and the God.",
          about="Love, union, creativity and abundance: a moon for relationships and for celebrating life in bloom."),
    6: _m("Mead Moon", "summer", "goblet", alt="",
          meaning="Named for the honey harvested around midsummer and the mead brewed from it; an echo of the 'honeymoon'.",
          about="Joy, celebration and togetherness at the height of summer, near the Litha solstice."),
    7: _m("Wort Moon", "summer", "herb", alt="Hay Moon",
          meaning="'Wort' is an old word for a herb or plant; this is the season of herb gathering and haymaking.",
          about="Herbal magic and healing: herbs are gathered at the height of their strength, and thanks are given for growth."),
    8: _m("Barley Moon", "summer", "wheat", alt="Corn Moon",
          meaning="The first grain is ready for harvest, the time of Lughnasadh or Lammas.",
          about="Gratitude, sharing and abundance, and the idea of sacrifice that makes growth possible."),
    9: _m("Harvest Moon", "autumn", "apple", alt="",
          meaning="The moon of the autumn harvest, near the equinox, when the fields are gathered under its light.",
          about="Balance and thanksgiving. A time to gather in what has been sown, and to take stock of the year."),
    10: _m("Blood Moon", "autumn", "bow", alt="Hunter's Moon",
           meaning="The season of the hunt and of the slaughter that stocks the winter larder; the low autumn moon often glows orange or red.",
           about="Release, ancestors and endings. Close to Samhain, a good time for divination and for letting go."),
    11: _m("Oak Moon", "autumn", "acorn", alt="Frosty Moon",
           meaning="The oak, sacred to the Druids, stands for strength and endurance; the frosts begin.",
           about="Strength, wisdom and protection. A moon for going inward as the days darken."),
    12: _m("Cold Moon", "winter", "moon", alt="Long Night Moon",
           meaning="The coldest weather and the longest nights of the year, around the winter solstice.",
           about="Rest and rebirth. The light begins its return at Yule, so this is a moon for reflection and for hope."),
    "leap": _m("Blue Moon", "winter", "blue_moon", alt="Black Moon",
               meaning="A Blue Moon is the second full moon in a calendar month. Its counterpart, the Black Moon, is the second new moon in a month.",
               about="Extra magical power: a rare chance to finish a long project, make a wish or release what you have carried. Once in a blue moon."),
}

# ---------------------------------------------------------------------------
# Almanac / Algonquin (colonial hybrid)
# ---------------------------------------------------------------------------

_ALMANAC = {
    1: _m("Wolf Moon", "winter", "wolf",
          meaning="Villagers once heard wolves howling hungrily outside in the cold and snow of midwinter.",
          about="Deep winter: the coldest weeks of the year in the north, a time for staying in and keeping warm."),
    2: _m("Snow Moon", "winter", "snowflake",
          meaning="Named for the heavy snow that usually falls in February. Some tribes called it the Hunger Moon, when hunting was hard.",
          about="The heaviest snowfalls, with the days getting noticeably longer."),
    3: _m("Worm Moon", "spring", "worm",
          meaning="As the soil softens, earthworms appear and birds come to feed on them; some tribes called it the Sap Moon.",
          about="The thaw: the ground softens, sap runs and the first signs of spring arrive."),
    4: _m("Pink Moon", "spring", "blossom",
          meaning="Named for the wild ground phlox, or 'moss pink', one of the first spring flowers. The moon itself is not pink.",
          about="Spring is under way: blossoms open, grass greens and the birds return."),
    5: _m("Flower Moon", "spring", "blossom",
          meaning="Named for the flowers that bloom in abundance across the land in May.",
          about="Full spring: fields and gardens bloom and the planting is well under way."),
    6: _m("Strawberry Moon", "summer", "strawberry",
          meaning="The Algonquin peoples named it for the short season when wild strawberries ripen.",
          about="Early summer, with the first fruit and the long days around the solstice."),
    7: _m("Buck Moon", "summer", "antlers",
          meaning="Male deer (bucks) grow their new antlers in July, covered in soft velvet.",
          about="The height of summer heat, with thunderstorms common; sometimes called the Thunder Moon."),
    8: _m("Sturgeon Moon", "summer", "fish",
          meaning="The large sturgeon of the Great Lakes and Lake Champlain were most easily caught at this time of year.",
          about="Late summer: the days begin to shorten and the first harvests come in."),
    9: _m("Corn Moon", "autumn", "corn", alt="Harvest Moon",
          meaning="The corn is ready to be gathered. The Harvest Moon is the full moon nearest the autumn equinox, which can fall in September or October.",
          about="Autumn arrives. Around the Harvest Moon the moon rises close to sunset for several nights, giving farmers extra light to bring in the crops."),
    10: _m("Hunter's Moon", "autumn", "bow",
           meaning="The time to hunt and to lay in meat for the winter, with the fields cleared and the game easier to see.",
           about="Autumn deepens: leaves fall, frosts begin and the preparations for winter are made."),
    11: _m("Beaver Moon", "autumn", "beaver",
           meaning="The time when beavers build their winter lodges, and when settlers set traps to secure furs before the swamps froze.",
           about="Early winter: the cold sets in and the days become short."),
    12: _m("Cold Moon", "winter", "moon",
           meaning="The cold takes hold and the nights are long, around the winter solstice; also called the Long Night Moon.",
           about="The longest nights of the year, as the year closes."),
    "leap": _m("Blue Moon", "winter", "blue_moon",
               meaning="The second full moon in a calendar month. It is a rare event, which gave rise to the phrase 'once in a blue moon'.",
               about="An extra full moon in the month, occurring roughly every two and a half to three years."),
}

# ---------------------------------------------------------------------------
# Celtic Tree Calendar (Robert Graves, 1948)
# ---------------------------------------------------------------------------

# (start month, start day, entry): each tree month lasts 28 days from its start.
_CELTIC_STARTS = [
    ((12, 24), _m("Beth", "winter", "birch", en="Birch", alt="Beith",
                  meaning="The birch is the first tree to colonise cleared ground and the first month of the tree year: a tree of new beginnings and renewal.",
                  about="Fresh starts and purification: a moon for clearing the old and beginning again.")),
    ((1, 21), _m("Luis", "winter", "berries", en="Rowan", alt="Luis",
                 meaning="The rowan with its red berries has long been planted for protection against enchantment and ill luck.",
                 about="Protection, insight and the first stirrings of spring energy.")),
    ((2, 18), _m("Nion", "winter", "herb", en="Ash", alt="Nuin",
                 meaning="The ash is the great world tree of many mythologies, linking the worlds above and below.",
                 about="Connections between the inner and outer worlds; journeys, the sea and the lengthening light.")),
    ((3, 18), _m("Fearn", "spring", "tree_round", en="Alder", alt="Fern",
                 meaning="Alder wood resists water, so it was used for foundations and bridges: a tree of courage and shelter.",
                 about="The spring equinox: laying foundations, courage and the protection of what is new.")),
    ((4, 15), _m("Saille", "spring", "willow", en="Willow", alt="Sail",
                 meaning="The willow loves water and bends without breaking. It is the moon tree, a symbol of intuition and flow.",
                 about="Intuition, dreams and cycles; the healing of the willow and the pull of the tides.")),
    ((5, 13), _m("Uath", "spring", "blossom", en="Hawthorn", alt="Huath",
                 meaning="The hawthorn blossoms at Beltane. It is the fairy tree, linked to hope, cleansing and protection.",
                 about="Hope and purification, with the fertility of early summer.")),
    ((6, 10), _m("Duir", "summer", "acorn", en="Oak", alt="Dair",
                 meaning="The oak, king of the grove, means strength and endurance; its name is related to the word for door.",
                 about="Midsummer: strength, wisdom and the door that opens at the solstice.")),
    ((7, 8), _m("Tinne", "summer", "holly", en="Holly", alt="",
                meaning="The evergreen, spiky holly is the tree of the spear, of balance and of the fiery half of the year.",
                about="Challenge, courage and protection as the summer peaks.")),
    ((8, 5), _m("Coll", "summer", "acorn", en="Hazel", alt="",
                meaning="The hazel is the tree of wisdom. In Irish legend the salmon of wisdom gained its knowledge by eating hazelnuts.",
                about="Wisdom, inspiration and divination, at the first harvest.")),
    ((9, 2), _m("Muin", "autumn", "grapes", en="Vine", alt="",
                meaning="The vine, with grapes or brambles, stands for the harvest, joy and the loosening of the tongue.",
                about="Harvest and celebration; a time for truth-telling and thanks.")),
    ((9, 30), _m("Gort", "autumn", "ivy", en="Ivy", alt="",
                 meaning="Ivy climbs and spirals, a symbol of persistence and of the winding path inward.",
                 about="Resilience, the spiral journey and growth through persistence.")),
    ((10, 28), _m("Ngetal", "autumn", "reed", en="Reed", alt="Ngéadal",
                  meaning="The reed gave pens, pipes and thatch, so it stands for the written word, music and purposeful action.",
                  about="Direct action, order and healing as the year darkens.")),
    ((11, 25), _m("Ruis", "autumn", "elderflower", en="Elder", alt="",
                  meaning="The elder is the tree of endings and rebirth, a tree linked to the cycle of life and death.",
                  about="Transformation: completing the year and making ready for the new one.")),
]

# ---------------------------------------------------------------------------
# Chinese lunar months
# ---------------------------------------------------------------------------

_CHINESE = {
    1: _m("Zhēngyuè 正月", "spring", "plum_blossom", en="First Month", short="Month 1",
          meaning="Zhēng means 'first'. The month that opens the year at the Lunar New Year; its flower is the plum blossom, which blooms in the cold.",
          about="The Spring Festival (day 1) and the Lantern Festival (day 15): family reunions, red envelopes, firecrackers and lanterns. Spring begins."),
    2: _m("Èryuè 二月", "spring", "blossom", en="Second Month", short="Month 2",
          meaning="The second month, with the apricot blossom as its flower.",
          about="Spring farm work begins. Day 2 is the 'dragon raises its head' day in northern China, traditionally for haircuts and ploughing."),
    3: _m("Sānyuè 三月", "spring", "peach", en="Third Month", short="Month 3",
          meaning="The third month, with the peach blossom as its flower.",
          about="Late spring: sowing, spring outings, blossoms and the Qingming season of remembering the ancestors."),
    4: _m("Sìyuè 四月", "summer", "peony", en="Fourth Month", short="Month 4",
          meaning="The fourth month, with the peony as its flower.",
          about="Early summer: wheat ripens and silkworms are raised. In Chinese Buddhism day 8 marks the Buddha's birthday."),
    5: _m("Wǔyuè 五月", "summer", "pomegranate", en="Fifth Month", short="Month 5",
          meaning="The fifth month, with the pomegranate flower. By tradition a month of heat, illness and protective charms.",
          about="The Dragon Boat Festival (day 5): dragon boat races, zongzi rice dumplings and protective herbs."),
    6: _m("Liùyuè 六月", "summer", "lotus", en="Sixth Month", short="Month 6",
          meaning="The sixth month, when the lotus is in bloom.",
          about="The heat of midsummer, with the hottest days of the year (sanfu) falling around now."),
    7: _m("Qīyuè 七月", "autumn", "orchid", en="Seventh Month", short="Month 7",
          meaning="The seventh month, with the orchid as its flower; the month of the Qixi and Ghost festivals.",
          about="Qixi, the festival of the Weaver Girl and the Cowherd (day 7), and the Ghost Festival (day 15), a time to honour ancestors and wandering spirits."),
    8: _m("Bāyuè 八月", "autumn", "elderflower", en="Eighth Month", short="Month 8",
          meaning="The eighth month, with the fragrant osmanthus as its flower.",
          about="The Mid-Autumn Festival (day 15): the full moon, mooncakes, lanterns and family reunions."),
    9: _m("Jiǔyuè 九月", "autumn", "chrysanthemum", en="Ninth Month", short="Month 9",
          meaning="The ninth month, with the chrysanthemum as its flower.",
          about="The Double Ninth Festival (day 9): climbing high, drinking chrysanthemum wine and honouring the elderly."),
    10: _m("Shíyuè 十月", "winter", "peony", en="Tenth Month", short="Month 10",
           meaning="The tenth month, with the hibiscus as its flower and the first of the winter months.",
           about="Early winter: the harvest is in. Day 1 is the traditional day for offering winter clothes to the ancestors."),
    11: _m("Dōngyuè 冬月", "winter", "snowflake", en="Eleventh Month", short="Month 11",
           meaning="Dōngyuè, the 'winter month', is the month that contains the winter solstice, the anchor of the whole calendar.",
           about="The Dongzhi solstice festival: the longest night, with tangyuan rice balls and dumplings, after which the light returns."),
    12: _m("Làyuè 腊月", "winter", "plum_blossom", en="Twelfth Month", short="Month 12",
           meaning="Làyuè, the 'sacrifice month', is the last month of the year; its flower is the wintersweet.",
           about="The Laba Festival (day 8) with its porridge, then cleaning, shopping and preparing for the Lunar New Year."),
}

# Well-known festivals by (lunar month, day): name, native name, icon, text.
_CHINESE_FESTIVALS = {
    (1, 1): ("Spring Festival", "春节", "lantern",
             "The Lunar New Year, the most important Chinese festival: family reunions, red envelopes, firecrackers, lion dances and wishes for luck."),
    (1, 15): ("Lantern Festival", "元宵节", "lantern",
              "The first full moon of the year closes the New Year celebrations with lantern displays, riddles and sweet rice balls (yuanxiao)."),
    (5, 5): ("Dragon Boat Festival", "端午节", "wave",
             "Dragon boat races and zongzi dumplings, remembering the poet Qu Yuan; protective herbs are hung on doors."),
    (7, 7): ("Qixi Festival", "七夕", "blossom",
             "The festival of the Weaver Girl and the Cowherd, who meet once a year on a bridge of magpies: often called the Chinese Valentine's Day."),
    (7, 15): ("Ghost Festival", "中元节", "candle",
              "The gates of the underworld are said to open: families honour ancestors and wandering spirits with offerings and lanterns."),
    (8, 15): ("Mid-Autumn Festival", "中秋节", "moon",
              "The harvest moon festival: families reunite to admire the full moon and share mooncakes."),
    (9, 9): ("Double Ninth Festival", "重阳节", "chrysanthemum",
             "Climbing high, chrysanthemum wine and honouring the elderly on the ninth day of the ninth month."),
    (12, 8): ("Laba Festival", "腊八节", "bowl",
              "Laba porridge is eaten, and the festival opens the countdown to the Lunar New Year."),
}


SYSTEMS = {
    "anishinaabe": {
        "name": "Anishinaabe Moons · Ojibwe",
        "short": "Anishinaabe Moons",
        "blurb": "The Anishinaabe (Ojibwe) 13-moon calendar follows the 13 scutes on the turtle's shell. "
                 "Its names are a seasonal map of life on the land: the run of the suckerfish, the flow of "
                 "maple sap, the ripening of the berries and the harvest of corn.",
        "note": "The Anishinaabe teachings are living and vary between communities and regions. "
                "These names follow one commonly published list; defer to your own community's teachings.",
        "accent": ("#6ee0c2", "#1c8a6e"),
        "rule": "month",
        "entries": _ANISHINAABE,
    },
    "wiccan": {
        "name": "Wiccan Moons · Esbat Names",
        "short": "Esbat Moons",
        "blurb": "Each full moon is an esbat with its own name and magical focus. The names draw on folk "
                 "tradition, and each carries an energy for reflection, intention and change.",
        "note": "Names and meanings vary between authors and covens; these are general associations. "
                "The Black Moon (second new moon of a month) is marked on its day.",
        "accent": ("#b79cff", "#6c46d1"),
        "rule": "month",
        "entries": _WICCAN,
    },
    "almanac": {
        "name": "Full Moon Names · Almanac",
        "short": "Almanac Moons",
        "blurb": "The best-known names outside religious practice, many drawn from the Algonquin and other "
                 "Northeastern peoples' vocabulary and popularised by agricultural almanacs.",
        "note": "A colonial-era blend of Indigenous and settler names, as popularised in almanacs. "
                "Several nations used different names for the same moon.",
        "accent": ("#ffcf6b", "#a87100"),
        "rule": "month",
        "entries": _ALMANAC,
    },
    "celtic": {
        "name": "Celtic Tree Calendar",
        "short": "Tree Moons",
        "blurb": "Thirteen months named after the trees of the Irish Ogham alphabet, each lasting 28 days "
                 "from 24 December. A lunation takes the name of the tree month in which its full moon falls.",
        "note": "The tree calendar was assembled by the poet Robert Graves in 1948; there is no evidence of an "
                "ancient Celtic calendar of tree months. It is a popular modern Pagan system. Because the tree months "
                "last 28 days and lunations 29.5, one tree month is occasionally skipped.",
        "accent": ("#8fd16f", "#3b8a2a"),
        "rule": "tree",
        "entries": {i: e for i, (_, e) in enumerate(_CELTIC_STARTS)},
    },
    "chinese": {
        "name": "Chinese Lunar Months",
        "short": "Lunar Months",
        "blurb": "A true lunar calendar: each month begins at the new moon, the Lunar New Year falls on the "
                 "second new moon after the winter solstice, and a leap month is added about every three years "
                 "to keep the months in step with the seasons.",
        "note": "Computed with the official rules (Beijing time). Month names and customs differ between regions; "
                "the season labels follow the northern hemisphere.",
        "accent": ("#ff7a8a", "#c2263d"),
        "rule": "chinese",
        "entries": _CHINESE,
    },
}

MOON_NAME_CHOICES = list(SYSTEMS)

_MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _tree_index(d: date) -> int:
    """Index of the Celtic tree month (0..12) in effect on date `d`."""
    key = (d.month, d.day)
    if key >= (12, 24) or key < (1, 21):
        return 0
    idx = 0
    for i, (start, _) in enumerate(_CELTIC_STARTS):
        if start != (12, 24) and key >= start:
            idx = i
    return idx


# ---------------------------------------------------------------------------
# Building the layer for a year
# ---------------------------------------------------------------------------

class MoonLayer:
    """Everything the page needs for one system and one year."""

    def __init__(self, system: str, year: int):
        self.id = system
        self.spec = SYSTEMS[system]
        self.year = year
        self.south = is_southern_hemisphere()
        self.segments = []        # one per lunation / Chinese month, in time order
        self.day_seg = {}         # iso -> segment index
        self.badges = {}          # iso -> {"seg": i, "kind": "full" | "black"}
        self.extra = {}           # iso -> extra card info (Chinese date, festival, black moon)
        self._build()

    # -- construction ------------------------------------------------------
    def _build(self):
        lunas = lunations(self.year)
        rule = self.spec["rule"]
        entries = self.spec["entries"]

        if rule == "chinese":
            raw = []
            for cm in chinese_months(self.year):
                base = entries[cm.number]
                entry = dict(base)
                if cm.leap:
                    entry["n"] = "Leap " + base["n"]
                    entry["en"] = "Leap " + base["en"]
                    entry["short"] = "Leap " + base["short"]
                    entry["meaning"] = ("A leap month (rùnyuè) is added about every three years to keep the lunar months "
                                        "in step with the seasons; it repeats the number of the month before it. "
                                        + base["meaning"])
                full = next((l for l in lunas if cm.start <= l.full.date() < cm.end), None)
                raw.append((cm.start, cm.end, entry, full, {"leap": cm.leap, "num": cm.number}))
        else:
            raw = []
            for l in lunas:
                if rule == "tree":
                    entry = dict(entries[_tree_index(l.full.date())])
                else:
                    entry = dict(entries["leap" if l.blue else l.full.month])
                raw.append((l.start_date, l.end_date, entry, l, {"blue": l.blue}))

        for i, (start, end, entry, lun, flags) in enumerate(raw):
            seg = {
                "id": f"m{i}", "start": start, "end": end, "entry": entry,
                "full": lun.full if lun else None, "flags": flags,
                "system": self.id,
            }
            self.segments.append(seg)
            d = start
            while d < end:
                self.day_seg[d.isoformat()] = i
                d += timedelta(days=1)
            if lun and lun.full.year == self.year:
                self.badges[lun.full.date().isoformat()] = {"seg": i, "kind": "full"}

        if self.id == "wiccan":
            for l in lunas:
                if l.black_new and l.start_date.year == self.year:
                    iso = l.start_date.isoformat()
                    self.extra.setdefault(iso, {})["black"] = True
                    self.badges.setdefault(iso, {"seg": self.day_seg.get(iso), "kind": "black"})

        if self.id == "chinese":
            d = date(self.year, 1, 1)
            while d.year == self.year:
                ld = chinese_lunar_date(d, self.year)
                if ld:
                    month, day, leap = ld
                    info = {"ld": f"{'Leap ' if leap else ''}Month {month} · Day {day}"}
                    fest = _CHINESE_FESTIVALS.get((month, day)) if not leap else None
                    if fest:
                        info["fest"] = {"n": fest[0], "native": fest[1], "text": fest[3],
                                        "svg": icon_svg(fest[2]), "icon": fest[2]}
                    self.extra[d.isoformat()] = info
                d += timedelta(days=1)

    # -- accessors ---------------------------------------------------------
    def seg_for(self, iso: str):
        i = self.day_seg.get(iso)
        return self.segments[i] if i is not None else None

    def full_moon_names(self) -> dict:
        """date -> moon name, for the .ics export."""
        out = {}
        for iso, b in self.badges.items():
            if b["kind"] == "full" and b["seg"] is not None:
                e = self.segments[b["seg"]]["entry"]
                out[iso] = e["n"] + (f" ({e['en']})" if e["en"] and self.id != "chinese" else "")
        return out

    # -- presentation ------------------------------------------------------
    def css(self) -> str:
        dark_accent, light_accent = self.spec["accent"]
        return (
            f":root {{ --ma: {dark_accent}; --ma-bg: #12151d; }}\n"
            + _season_css()
            + "@media (prefers-color-scheme: light) {\n"
              f"  :root {{ --ma: {light_accent}; --ma-bg: #ffffff; }}\n}}\n"
        )

    def _chip_hint(self, seg) -> str:
        if self.spec["rule"] == "tree":
            idx = next(i for i, e in self.spec["entries"].items() if e["n"] == seg["entry"]["n"])
            (m, d), _ = _CELTIC_STARTS[idx]
            return f"from {_MONTH_ABBR[m - 1]} {d}"
        return ""

    def art_svg(self) -> str:
        """A ring of the system's moons, one icon per name, coloured by season."""
        import math
        entries = [e for k, e in self.spec["entries"].items() if k != "leap"]
        n = len(entries)
        cx = cy = 100
        r = 72
        marks = []
        for i, e in enumerate(entries):
            ang = math.radians(i * 360 / n - 90)
            x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
            marks.append(
                f'<g data-wk="{e["season"]}" style="color:var(--wk)"><title>{e["short"]}</title>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="13" fill="var(--ma-bg)" stroke="var(--wk)" stroke-width="1.8"/>'
                f'<svg x="{x - 9:.2f}" y="{y - 9:.2f}" width="18" height="18" viewBox="0 0 24 24">{icon_inner(e["icon"])}</svg></g>'
            )
        # a full moon at the centre
        return (
            '<svg class="mn-art" viewBox="0 0 200 200" aria-hidden="true">'
            '<circle cx="100" cy="100" r="72" fill="none" stroke="var(--ma)" stroke-opacity=".18" stroke-width="26"/>'
            '<circle cx="100" cy="100" r="72" fill="none" stroke="var(--ma)" stroke-opacity=".5" stroke-dasharray="1 5"/>'
            '<circle cx="100" cy="100" r="38" fill="var(--ma)" fill-opacity=".14" stroke="var(--ma)" stroke-width="2"/>'
            '<circle cx="100" cy="100" r="30" fill="var(--ma)" fill-opacity=".85"/>'
            '<circle cx="90" cy="92" r="6" fill="var(--ma-bg)" fill-opacity=".25"/>'
            '<circle cx="109" cy="106" r="8" fill="var(--ma-bg)" fill-opacity=".2"/>'
            '<circle cx="96" cy="112" r="3.500" fill="var(--ma-bg)" fill-opacity=".2"/>'
            + "".join(marks) + '</svg>'
        )

    def banner_html(self) -> str:
        spec = self.spec
        entries = [(k, e) for k, e in spec["entries"].items() if k != "leap"]
        chips = "".join(
            f'<span class="mn-chip" data-wk="{e["season"]}">{icon_svg(e["icon"], "wi")}<b>{e["short"]}</b>'
            + (f'<i>{_MONTH_ABBR[k - 1]}</i>' if spec["rule"] == "month" else
               f'<i>{_MONTH_ABBR[_CELTIC_STARTS[k][0][0] - 1]} {_CELTIC_STARTS[k][0][1]}</i>' if spec["rule"] == "tree" else "")
            + '</span>'
            for k, e in entries
        )
        leap = spec["entries"].get("leap")
        if leap:
            chips += (f'<span class="mn-chip mn-leap" data-wk="{leap["season"]}">{icon_svg(leap["icon"], "wi")}'
                      f'<b>{leap["short"]}</b><i>2nd full moon of a month</i></span>')
        south = ('<p class="mn-south">Southern hemisphere: these names come from northern seasons and are shown '
                 'as published, not shifted.</p>') if self.south else ""
        return (
            '<section class="mn-banner">'
            f'<div class="mn-art-wrap">{self.art_svg()}</div>'
            '<div class="mn-text">'
            f'<div class="mn-title">{spec["name"]}</div>'
            f'<p class="mn-blurb">{spec["blurb"]}</p>'
            f'<div class="mn-chips">{chips}</div>{south}'
            f'<p class="mn-note">{spec["note"]}</p>'
            '</div></section>'
        )

    def ribbon_row_html(self, month: int, days: int) -> str:
        """A table row of colspan segments (the moon names) for one month."""
        cells = []
        d = 1
        while d <= days:
            iso = date(self.year, month, d).isoformat()
            i = self.day_seg.get(iso)
            span = 1
            while d + span <= days and self.day_seg.get(date(self.year, month, d + span).isoformat()) == i:
                span += 1
            if i is None:
                cells.append(f"<td colspan='{span}' class='mn-seg mn-none'></td>")
            else:
                e = self.segments[i]["entry"]
                label = f'<span class="mn-nm">{e["short"]}</span>' if span >= 4 else ""
                cells.append(
                    f"<td colspan='{span}' class='mn-seg' data-wk='{e['season']}' data-seg='{i}' "
                    f"title=\"{e['n']}{(' · ' + e['en']) if e['en'] else ''}\">"
                    f"<div class='mn-inner'>{icon_svg(e['icon'], 'wi')}{label}</div></td>"
                )
            d += span
        return "<tr class='mn-row'>" + "".join(cells) + "</tr>\n"

    def badge_html(self, iso: str) -> str:
        b = self.badges.get(iso)
        if not b:
            return ""
        if b["kind"] == "black":
            return ("<div class='mbadge mbadge-black' data-wk='winter' title='Black Moon: the second new moon of the month'>"
                    + icon_svg("black_moon") + "</div>")
        seg = self.segments[b["seg"]]
        e = seg["entry"]
        tip = f"{e['n']}" + (f" ({e['en']})" if e["en"] else "")
        return (f"<div class='mbadge' data-wk='{e['season']}' title=\"{tip}\">{icon_svg(e['icon'])}</div>")

    def month_strip_html(self, month: int) -> str:
        """Chips for the month's named full moons, Black Moon and festivals."""
        chips = []
        for iso, b in sorted(self.badges.items()):
            if int(iso[5:7]) != month or iso[:4] != str(self.year):
                continue
            if b["kind"] == "black":
                chips.append(f'<span class="mchip" data-wk="winter" data-wd="{iso}">{icon_svg("black_moon", "wi")}'
                             f'<b>{int(iso[8:])}</b>Black Moon</span>')
                continue
            e = self.segments[b["seg"]]["entry"]
            chips.append(f'<span class="mchip" data-wk="{e["season"]}" data-wd="{iso}">{icon_svg(e["icon"], "wi")}'
                         f'<b>{int(iso[8:])}</b>{e["short"]}</span>')
        for iso, x in sorted(self.extra.items()):
            if int(iso[5:7]) == month and x.get("fest") and iso[:4] == str(self.year):
                f = x["fest"]
                chips.append(f'<span class="mchip mfest" data-wk="autumn" data-wd="{iso}">{f["svg"]}'
                             f'<b>{int(iso[8:])}</b>{f["n"]}</span>')
        return f'<div class="mn-strip">{"".join(chips)}</div>' if chips else ""

    def payload(self) -> dict:
        """JSON for the day card."""
        items = {}
        for s in self.segments:
            e = s["entry"]
            items[s["id"]] = {
                "n": e["n"], "en": e["en"], "alt": e["alt"], "season": e["season"],
                "svg": icon_svg(e["icon"]), "meaning": e["meaning"], "about": e["about"],
                "start": s["start"].isoformat(), "end": s["end"].isoformat(),
                "full": s["full"].strftime("%Y-%m-%d") if s["full"] else "",
                "fullTime": s["full"].strftime("%H:%M") if s["full"] else "",
                "blue": bool(s["flags"].get("blue")), "leap": bool(s["flags"].get("leap")),
                "hint": self._chip_hint(s),
            }
        return {
            "id": self.id, "name": self.spec["name"], "south": self.south,
            "blackNote": ("A Black Moon is the second new moon in a calendar month." if self.id == "wiccan" else ""),
            "daySeg": {iso: self.segments[i]["id"] for iso, i in self.day_seg.items()
                       if iso.startswith(str(self.year))},
            "items": items,
            "extra": {k: v for k, v in self.extra.items()},
        }
