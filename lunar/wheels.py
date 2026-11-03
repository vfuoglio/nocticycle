"""Year wheels: the yearly festival cycles of living traditions.

A *wheel* marks the festivals of a tradition's year on top of the lunar
calendar. Wheels combine freely with the lunar *traditions* (``--tradition``):
for example the Wiccan Wheel of the Year together with the Wiccan esbats.

Dates come from the astronomy wherever the tradition defines them that way
(solstices, equinoxes and the 24 solar terms are computed from the Sun's
position, see ``solar.py``) and from fixed calendar dates otherwise
(cross-quarter days such as Imbolc or Samhain).

Wheels flagged ``flip`` follow the northern-hemisphere cycle and are shifted by
six months for locations south of the equator (Yule falls at the June solstice,
Samhain at the end of April, and so on). The Slavic and East Asian wheels are
anchored in the northern hemisphere's seasons and are never shifted.

The texts are short, general summaries written for this project. Traditions
differ between groups and regions: edit them freely to match your own practice.
"""

import math
from calendar import monthrange
from datetime import date

from . import config as cfg
from .moon_svg import is_southern_hemisphere
from .solar import solar_terms
from .wheel_icons import icon_inner, icon_svg

# ---------------------------------------------------------------------------
# Seasons (colours for dark and light themes)
# ---------------------------------------------------------------------------

SEASONS = {
    "winter": {"label": "Winter", "dark": "#8fc7ff", "light": "#2b6cb0"},
    "spring": {"label": "Spring", "dark": "#7fe3a6", "light": "#1f8a4c"},
    "summer": {"label": "Summer", "dark": "#ffd25e", "light": "#a8740a"},
    "autumn": {"label": "Autumn", "dark": "#ff9d62", "light": "#b8501a"},
}


def _ev(id, name, sub, kind, season, icon, rule, theme, celebrates, about,
        major=True, approx=False):
    return {
        "id": id, "n": name, "sub": sub, "kind": kind, "season": season,
        "icon": icon, "rule": rule, "theme": theme, "celebrates": celebrates,
        "about": about, "major": major, "approx": approx,
    }


def _sun(lon):
    return ("sun", lon)


def _day(m, d):
    return ("date", m, d)


# ---------------------------------------------------------------------------
# 1. Wicca: the Wheel of the Year
# ---------------------------------------------------------------------------

_WICCA = [
    _ev("yule", "Yule", "Winter Solstice", "Minor Sabbat · solstice", "winter", "fir", _sun(270),
        "Rebirth of the sun",
        "The longest night and the return of the light: the Sun God is reborn and the days begin to lengthen.",
        "Evergreens, candles and the Yule log, gift-giving and gatherings welcome the turning of the Wheel."),
    _ev("imbolc", "Imbolc", "Candlemas · Brigid's Day", "Major Sabbat · fire festival", "winter", "candle", _day(2, 1),
        "First stirrings of spring",
        "The first signs of returning life: the Goddess recovers, the ewes give milk, and the festival is often dedicated to the goddess Brigid.",
        "Candles and hearth fires, cleaning the home and blessing seeds mark a time of purification and new beginnings."),
    _ev("ostara", "Ostara", "Spring Equinox", "Minor Sabbat · equinox", "spring", "hare", _sun(0),
        "Balance and fertility",
        "Day and night stand in balance and the light begins to win; the earth awakens as the Goddess and God turn toward growth.",
        "Eggs, hares, flowers and seeds symbolise fertility, and rituals focus on planting intentions for the year."),
    _ev("beltane", "Beltane", "May Eve", "Major Sabbat · fire festival", "spring", "bonfire", _day(5, 1),
        "Union and fertility",
        "The sacred union of the Goddess and the God and the full flowering of spring.",
        "Bonfires, maypole dances and flower crowns celebrate life, love and abundance."),
    _ev("litha", "Litha", "Summer Solstice · Midsummer", "Minor Sabbat · solstice", "summer", "sun_high", _sun(90),
        "The Sun at its height",
        "The longest day, when the Sun God reaches the peak of his power before the year begins to wane.",
        "Bonfires, gathering herbs and flowers, and giving thanks for light and growth."),
    _ev("lughnasadh", "Lughnasadh", "Lammas · First Harvest", "Major Sabbat · fire festival", "summer", "wheat", _day(8, 1),
        "The first harvest",
        "The first grain harvest: gratitude for abundance, and the sacrifice of the Sun God's strength as the days shorten.",
        "Baking bread, sharing grain and fruit, games and crafts. The name honours the Irish god Lugh."),
    _ev("mabon", "Mabon", "Autumn Equinox", "Minor Sabbat · equinox", "autumn", "apple", _sun(180),
        "Second harvest and balance",
        "Day and night in balance once more: thanksgiving for the harvest and preparation for the dark half of the year.",
        "Gratitude rituals, feasts of fruit and vegetables, and reflecting on what to keep and what to release."),
    _ev("samhain", "Samhain", "Hallowe'en · Witches' New Year", "Major Sabbat · fire festival", "autumn", "pumpkin", _day(10, 31),
        "Honouring the dead, the turning of the year",
        "The end of the harvest and the Witches' New Year: the veil between the living and the dead is thought to be thinnest.",
        "Ancestors are remembered with candles and a place at the table; divination and reflection open the dark half of the year."),
]

# ---------------------------------------------------------------------------
# 2. Modern Druidry: the Eightfold Wheel
# ---------------------------------------------------------------------------

_DRUID = [
    _ev("alban-arthuan", "Alban Arthuan", "Light of Arthur · Winter Solstice", "Solar festival · solstice", "winter", "sun_low", _sun(270),
        "Rebirth of the light",
        "The shortest day: the sun is reborn out of the darkness, the 'Light of Arthur'.",
        "Druids often gather at dawn, at stone circles or hilltops, to greet the returning light."),
    _ev("imbolc", "Imbolc", "Oimelc · Brigid", "Fire festival · cross-quarter", "winter", "candle", _day(2, 1),
        "Inspiration and awakening",
        "The first stirrings of spring and the goddess Brigid, patron of poetry, healing and smithcraft: a festival of Awen, divine inspiration.",
        "Candles, wells and creative work mark the awakening of the land and of the imagination."),
    _ev("alban-eilir", "Alban Eilir", "Light of the Earth · Spring Equinox", "Solar festival · equinox", "spring", "sprout", _sun(0),
        "Balance and new growth",
        "Light and dark in balance as the earth awakens and the cycle of growth begins.",
        "Rituals of planting and renewal, with attention to the local landscape coming back to life."),
    _ev("beltane", "Beltane", "Bright fire", "Fire festival · cross-quarter", "spring", "bonfire", _day(5, 1),
        "Fire, flowering and fertility",
        "The beginning of summer: the Beltane fires purify and bring blessing to people and herds.",
        "Cattle were traditionally driven between two fires; today bonfires, flower garlands and dancing mark the day."),
    _ev("alban-heruin", "Alban Heruin", "Light of the Shore · Summer Solstice", "Solar festival · solstice", "summer", "sun_high", _sun(90),
        "The Sun at its height",
        "The longest day and the peak of the Sun's strength: a time of fullness, creativity and community.",
        "Dawn gatherings at sacred sites and celebration of the abundance of land and sea."),
    _ev("lughnasadh", "Lughnasadh", "Festival of Lugh", "Fire festival · cross-quarter", "summer", "wheat", _day(8, 1),
        "Harvest and skill",
        "The first harvest, associated with the god Lugh, patron of skills and crafts.",
        "Games, crafts and the first fruits, echoing the old Celtic gatherings and fairs."),
    _ev("alban-elued", "Alban Elued", "Light of the Water · Autumn Equinox", "Solar festival · equinox", "autumn", "drop", _sun(180),
        "Thanksgiving and balance",
        "Light and dark in balance once more, with thanks for the harvest as the year turns toward winter.",
        "Druids give thanks, reflect on gains and losses, and prepare for the darker months."),
    _ev("samhain", "Samhain", "Summer's end", "Fire festival · cross-quarter", "autumn", "lantern", _day(10, 31),
        "Ancestors and the year's end",
        "The end of the Celtic year and the festival of the ancestors, when the veil to the Otherworld is thin.",
        "Remembering those who have died, storytelling and quiet reflection at the start of the dark half."),
]

# ---------------------------------------------------------------------------
# 3. Rodnovery: Kolo Goda
# ---------------------------------------------------------------------------

_SLAVIC = [
    _ev("koliada", "Koliada", "Winter Solstice · Kolyada", "Solstice festival", "winter", "sunwheel", _sun(270),
        "Rebirth of the sun",
        "The rebirth of the sun at the longest night: the turning of the year and the welcome of the new sun-child.",
        "Carolling (kolyadki), masked processions, ritual meals and festive fires fill the days around the solstice."),
    _ev("gromnica", "Gromnica", "Gromnitsa · Thunder Candle", "Seasonal festival", "winter", "candle", _day(2, 2),
        "Candles against the winter dark",
        "The meeting of winter and spring: blessed 'thunder candles' protect the home while the first thaw is awaited.",
        "Candles are lit against storms and misfortune; many Rodnovers link the day with Veles, Perun and the first stirring of spring.",
        approx=True),
    _ev("jare-gody", "Jare Gody", "Spring Equinox", "Equinox festival", "spring", "sprout", _sun(0),
        "The awakening of spring",
        "The awakening of nature and the return of the bright half of the year, with young Yarilo as the god of spring.",
        "Songs, dances, new fires and painted eggs greet the spring."),
    _ev("radonitsa", "Radonitsa", "Spring remembrance of the ancestors", "Seasonal festival", "spring", "egg", _day(5, 15),
        "Remembering the ancestors",
        "A spring day of remembrance: the ancestors are greeted and invited to share the season's renewal.",
        "Families visit graves with food, eggs and drink. The date varies by tradition and region; here it is fixed at 15 May.",
        approx=True),
    _ev("kupala", "Kupala Night", "Ivan Kupala · Summer Solstice", "Solstice festival", "summer", "wreath", _sun(90),
        "Fire, water and flowering",
        "The midsummer festival of fire, water and fertility, when herbs are at their most powerful.",
        "Flower wreaths are floated on rivers, couples leap over bonfires, herbs are gathered and the legendary fern flower is sought. "
        "Folk tradition dates it to 6-7 July (24 June in the old calendar)."),
    _ev("perun", "Perun's Day", "Feast of the thunder god", "Seasonal festival", "summer", "lightning", _day(7, 20),
        "Thunder, storm and justice",
        "The feast of Perun, god of thunder, lightning and oaks: protection, justice and the storm that feeds the fields.",
        "Offerings and gatherings in oak groves. The date varies between communities; here it is fixed at 20 July.",
        approx=True),
    _ev("plodovi", "Plodovi", "Autumn Equinox · Harvest", "Equinox festival", "autumn", "apple", _sun(180),
        "Harvest thanks",
        "Thanksgiving for the harvest and the fruitfulness of the earth, and for the stores that will see the family through winter.",
        "The first loaves and fruit are offered, feasts and fairs are held, and the home is readied for the cold."),
    _ev("dziady", "Dziady", "Ancestor Night", "Seasonal festival", "autumn", "lantern", _day(11, 1),
        "Ancestors and the dead",
        "The great autumn feast of the dead, when the ancestors are welcomed home and fed.",
        "Food and drink are left out, candles and bonfires are lit and the names of the dead are spoken. "
        "It is observed around 1-2 November and, in some regions, on other autumn dates.",
        approx=True),
]

# ---------------------------------------------------------------------------
# 5. Heathenry / Asatru: seasonal tides
# ---------------------------------------------------------------------------

_HEATHEN = [
    _ev("yule", "Yule", "Midwinter · Jól", "Great tide · solstice", "winter", "bonfire", _sun(270),
        "Midwinter, ancestors and the Wild Hunt",
        "The midwinter festival of the returning sun, family and the honoured dead; the old Yule lasted twelve nights.",
        "A feast with toasts to the gods and ancestors, the Yule log, and oaths sworn on the Yule boar or over a drinking horn."),
    _ev("disting", "Dísablót", "Disting · Honouring the dísir", "Blót", "winter", "candle", _day(2, 2),
        "The dísir and the turning of winter",
        "A blót to honour the dísir, the female ancestral guardian spirits, and to ask for a good year as winter ebbs.",
        "Offerings and a shared feast. The Disting was a great market and assembly in old Uppsala; groups hold it from late January to mid-February.",
        approx=True),
    _ev("ostara", "Ostara · Sigrblót", "Spring Equinox", "Great tide · equinox", "spring", "hare", _sun(0),
        "Awakening and victory",
        "The awakening of spring, honouring the dawn goddess Eostre (Ostara) and, in some traditions, a 'victory blót' (Sigrblót) for success in the coming year.",
        "Hares, eggs and flowers mark the season, with offerings for fertility and luck. Groups differ on the names and the dates."),
    _ev("midsummer", "Midsummer", "Summer Solstice · Miðsumar", "Great tide · solstice", "summer", "sun_high", _sun(90),
        "The Sun at its height",
        "The longest day and the height of the Sun's power: a time for gatherings and fires, honouring the gods of light and growth, Baldr among them in many traditions.",
        "Bonfires, feasts and rites of friendship make it a classic time for communal assembly."),
    _ev("winter-finding", "Winter Finding", "Autumn Equinox · Haustblót", "Great tide · equinox", "autumn", "apple", _sun(180),
        "Harvest and the coming winter",
        "The harvest blessing at the autumn equinox, marking the shift into the dark half of the year.",
        "Thanks for the harvest and the year's successes, with offerings to Thor, Frey and the land spirits."),
    _ev("winternights", "Winternights", "Vetrnætr", "Blót", "autumn", "moon", _day(10, 24),
        "Ancestors and the dark half",
        "The old Norse welcome to winter: a feast for the ancestors, the elves (álfar) and the dísir.",
        "The sagas describe sacrifices and feasting at the onset of winter, held by Icelandic custom in late October. Dates vary.",
        approx=True),
]

# ---------------------------------------------------------------------------
# 4. East Asian calendars: the 24 solar terms
# ---------------------------------------------------------------------------

def _term(id, lon, name, hanzi, english, kind, season, icon, theme, celebrates, about, major=False):
    return _ev(id, name, f"{hanzi} · {english}", kind, season, icon, _sun(lon), theme,
               celebrates, about, major=major)


_EASTASIAN = [
    _term("lichun", 315, "Lìchūn", "立春", "Start of Spring", "Start of season", "spring", "sprout",
          "Spring begins",
          "The traditional beginning of spring in the solar-term calendar: farmers prepare the fields and the new year's growth is welcomed.",
          "In China spring pancakes and fresh vegetables mark the day; in Japan it is Risshun, the day after Setsubun.", True),
    _term("yushui", 330, "Yǔshuǐ", "雨水", "Rain Water", "Solar term", "spring", "rain",
          "Snow turns to rain",
          "Rain replaces snow and the ice thaws, watering the fields.",
          "Farming work begins in earnest and people look to the spring rains for the year's crops."),
    _term("jingzhe", 345, "Jīngzhé", "惊蛰", "Awakening of Insects", "Solar term", "spring", "thunder",
          "Spring thunder wakes the earth",
          "Spring thunder is said to wake insects and animals from their winter sleep.",
          "In some regions people burn herbs or sweep the house to keep pests and snakes away."),
    _term("chunfen", 0, "Chūnfēn", "春分", "Spring Equinox", "Equinox", "spring", "balance",
          "Day and night in balance",
          "Day and night are equal and the Sun crosses the equator northward; yin and yang are in balance.",
          "In China people try to stand eggs upright; in Japan Shunbun no Hi is a public holiday for honouring ancestors (Higan).", True),
    _term("qingming", 15, "Qīngmíng", "清明", "Clear and Bright", "Solar term · festival", "spring", "kite",
          "Remembrance and spring outings",
          "Qingming, the Tomb-Sweeping Festival: families honour their ancestors and enjoy the fresh spring.",
          "Graves are cleaned and offerings made; kite-flying and spring walks are popular. It is a public holiday in China, Taiwan, Hong Kong and Macau."),
    _term("guyu", 30, "Gǔyǔ", "谷雨", "Grain Rain", "Solar term", "spring", "tulip",
          "Rain nourishes the grain",
          "The last term of spring: gentle rain helps the grains sprout.",
          "Spring tea is picked and peonies are in bloom, both traditional pleasures of the season."),
    _term("lixia", 45, "Lìxià", "立夏", "Start of Summer", "Start of season", "summer", "sun",
          "Summer begins",
          "Crops grow quickly and the heat starts to build: a time to welcome the warm season and nourish the body.",
          "In parts of China people eat tea-boiled eggs and weigh themselves, a custom said to predict the summer's health.", True),
    _term("xiaoman", 60, "Xiǎomǎn", "小满", "Grain Buds", "Solar term", "summer", "wheat",
          "Grain begins to fill",
          "Summer grains start to fill but are not yet ripe.",
          "Farmers watch the ripening of the wheat and prepare for the harvest to come."),
    _term("mangzhong", 75, "Mángzhòng", "芒种", "Grain in Ear", "Solar term", "summer", "sprout",
          "Sowing and reaping",
          "Grain with awns ripens while rice is planted: the busiest season for farmers.",
          "Traditionally also the 'farewell to the flower spirits' as the spring blossoms fade."),
    _term("xiazhi", 90, "Xiàzhì", "夏至", "Summer Solstice", "Solstice", "summer", "sun_high",
          "Longest day, yin begins",
          "The longest daylight of the year in the north, after which yang slowly gives way to yin.",
          "Noodles and cooling foods are traditional in northern China, and the day marks the approach of the hottest weeks.", True),
    _term("xiaoshu", 105, "Xiǎoshǔ", "小暑", "Lesser Heat", "Solar term", "summer", "thermo_hi",
          "The heat arrives",
          "Hot weather begins in earnest, ahead of the hottest days.",
          "Hot-weather foods such as noodles and lotus are enjoyed and the 'dog days' (sanfu) are close."),
    _term("dashu", 120, "Dàshǔ", "大暑", "Greater Heat", "Solar term", "summer", "sun",
          "The hottest days",
          "The hottest period of the year.",
          "People stay cool with herbal teas, watermelon and the customs of the sanfu days."),
    _term("liqiu", 135, "Lìqiū", "立秋", "Start of Autumn", "Start of season", "autumn", "leaf",
          "Autumn begins",
          "The first cool breezes: summer's heat lingers, but the harvest cycle has turned.",
          "In some regions of China people 'stick on autumn fat' (tiē qiū biāo) with hearty meat dishes.", True),
    _term("chushu", 150, "Chǔshǔ", "处暑", "End of Heat", "Solar term", "autumn", "sun_low",
          "The heat recedes",
          "Summer heat begins to fade as autumn approaches.",
          "Early crops are harvested and the weather turns noticeably cooler."),
    _term("bailu", 165, "Báilù", "白露", "White Dew", "Solar term", "autumn", "drop",
          "Dew turns white",
          "Cool nights leave white dew on the grass: autumn is clearly here.",
          "A reminder to dress warmer as the autumn harvests are brought in."),
    _term("qiufen", 180, "Qiūfēn", "秋分", "Autumn Equinox", "Equinox", "autumn", "balance",
          "Equal day and night, harvest",
          "The Sun crosses the equator southward; day and night are equal and the harvest is in. It falls close to the Mid-Autumn (moon) festival.",
          "A time of harvest thanksgiving. In Japan Shūbun no Hi is a public holiday for ancestors, with ohagi sweets.", True),
    _term("hanlu", 195, "Hánlù", "寒露", "Cold Dew", "Solar term", "autumn", "leaf",
          "Dew turns cold",
          "The dew turns cold, the first sign of the frost to come.",
          "Climbing high and chrysanthemum viewing are popular around this time, close to the Double Ninth festival."),
    _term("shuangjiang", 210, "Shuāngjiàng", "霜降", "Frost Descent", "Solar term", "autumn", "crystal",
          "The first frost",
          "The first frost appears: the last solar term of autumn.",
          "In parts of China persimmons are eaten to ward off the cold."),
    _term("lidong", 225, "Lìdōng", "立冬", "Start of Winter", "Start of season", "winter", "thermo_lo",
          "Winter begins",
          "The start of the cold season: crops are stored and the body is nourished against the winter.",
          "Dumplings in northern China, tonic soups in the south; in Korea this is the season of kimjang, making kimchi for the winter.", True),
    _term("xiaoxue", 240, "Xiǎoxuě", "小雪", "Lesser Snow", "Solar term", "winter", "snow_light",
          "The first light snow",
          "Light snow begins to fall in the north.",
          "Foods are pickled and cured for winter, such as preserved vegetables and cured meat."),
    _term("daxue", 255, "Dàxuě", "大雪", "Greater Snow", "Solar term", "winter", "snowflake",
          "Heavy snow and deep cold",
          "Snow falls more heavily and the cold deepens.",
          "People enjoy the snow and eat warming foods as the year draws toward its darkest point."),
    _term("dongzhi", 270, "Dōngzhì", "冬至", "Winter Solstice", "Solstice · festival", "winter", "bowl",
          "Longest night, yang returns",
          "The longest night and the shortest day: the turning point when yang energy begins to return, and one of the most important traditional festivals.",
          "Families gather for tangyuan (sweet rice balls) in the south and dumplings in the north. In Japan Tōji is marked with yuzu baths and kabocha; in Korea with red-bean porridge (patjuk).", True),
    _term("xiaohan", 285, "Xiǎohán", "小寒", "Lesser Cold", "Solar term", "winter", "thermo_lo",
          "The cold sets in",
          "The coldest period begins, though the peak is still to come.",
          "Warming foods such as Laba porridge are eaten around this time."),
    _term("dahan", 300, "Dàhán", "大寒", "Greater Cold", "Solar term", "winter", "crystal",
          "The coldest days, the year ends",
          "The last of the 24 terms: the coldest days before the return of spring.",
          "Families prepare for the Lunar New Year with cleaning and shopping."),
]


WHEELS = {
    "wicca": {
        "name": "Wheel of the Year · Wicca",
        "short": "Wheel of the Year",
        "subtitle": "Eight Sabbats",
        "blurb": "The modern Wiccan year turns through eight Sabbats: four solar festivals at the "
                 "solstices and equinoxes (Minor Sabbats) and four fire festivals between them "
                 "(Major Sabbats), following the story of the Goddess and the Horned God.",
        "note": "Practices differ between traditions and covens; these are general associations.",
        "accent": ("#ffb454", "#b3590a"),
        "flip": True,
        "events": _WICCA,
    },
    "druid": {
        "name": "Eightfold Wheel · Modern Druidry",
        "short": "Eightfold Wheel",
        "subtitle": "Eight festivals",
        "blurb": "Modern Druidry keeps eight festivals: the four solar 'Albans' of the solstices "
                 "and equinoxes, and four fire festivals, flowing with Awen (divine inspiration) "
                 "and the rhythms of the local landscape.",
        "note": "Druid orders differ in names, dates and customs; these are general summaries.",
        "accent": ("#7fd18b", "#2f7d3a"),
        "flip": True,
        "events": _DRUID,
    },
    "slavic": {
        "name": "Kolo Goda · Slavic Rodnovery",
        "short": "Kolo Goda",
        "subtitle": "Wheel of the year",
        "blurb": "Rodnovery, the living Slavic native faith, follows the Kolo Goda: eight seasonal "
                 "thresholds anchored in Slavic folklore and its gods, Perun the thunderer and "
                 "Veles among them, and in the memory of the ancestors.",
        "note": "Names and dates differ among Rodnover communities and regions; fixed-date festivals "
                "here are approximate. The wheel is not shifted for the southern hemisphere.",
        "accent": ("#f2705e", "#b8321f"),
        "flip": False,
        "events": _SLAVIC,
    },
    "eastasian": {
        "name": "24 Solar Terms · East Asia",
        "short": "24 Solar Terms",
        "subtitle": "Jiéqì · the 24 solar terms",
        "blurb": "The East Asian calendars divide the year into 24 solar terms, each 15° of the Sun's "
                 "path, used across China, Korea, Vietnam and Japan to guide farming, health and "
                 "festivals. Eight of them are the cornerstones: the solstices, the equinoxes and "
                 "the four 'starts' of the seasons; the other sixteen are shown as small markers.",
        "note": "Computed from the Sun's position. Customs differ between regions and countries; "
                "the terms follow the northern hemisphere's seasons everywhere.",
        "accent": ("#ff7a8a", "#c2263d"),
        "flip": False,
        "events": _EASTASIAN,
    },
    "heathen": {
        "name": "Seasonal Tides · Heathenry",
        "short": "Seasonal Tides",
        "subtitle": "Blóts and tides",
        "blurb": "Modern Heathens (Ásatrú) keep a living calendar of communal blóts: Yule at midwinter, "
                 "the spring awakening, Midsummer and Winter Finding, interspersed with blessings "
                 "for the dísir and the ancestors.",
        "note": "Heathen groups differ in names, dates and customs, and many avoid Wiccan terms; "
                "these are general summaries.",
        "accent": ("#6fa8ff", "#2a5fc2"),
        "flip": True,
        "events": _HEATHEN,
    },
}

WHEEL_CHOICES = list(WHEELS)


# ---------------------------------------------------------------------------
# Resolving the events of a year
# ---------------------------------------------------------------------------

def wheel_events(wheel_id: str, year: int) -> dict:
    """Return {iso date: event dict} for the wheel in `year`.

    Each event dict is a copy of the data above plus ``iso`` and, for
    astronomical events, ``time`` (local HH:MM of the exact moment).
    """
    spec = WHEELS[wheel_id]
    flip = spec["flip"] and is_southern_hemisphere()
    terms = solar_terms(year)
    out = {}
    for ev in spec["events"]:
        rule = ev["rule"]
        e = {k: v for k, v in ev.items() if k != "rule"}
        if rule[0] == "sun":
            lon = (rule[1] + 180) % 360 if flip else rule[1]
            moment = terms[lon]
            e["iso"] = moment.date().isoformat()
            e["time"] = moment.strftime("%H:%M")
            e["lon"] = lon
        else:
            m, d = rule[1], rule[2]
            if flip:
                m = (m + 5) % 12 + 1
                d = min(d, monthrange(year, m)[1])
            e["iso"] = date(year, m, d).isoformat()
        e["flipped"] = bool(flip)
        out[e["iso"]] = e
    return out


# ---------------------------------------------------------------------------
# Presentation: banner, wheel graphic, month chips, CSS
# ---------------------------------------------------------------------------

def _season_css() -> str:
    dark = "\n".join(f'[data-wk="{k}"] {{ --wk: {v["dark"]}; }}' for k, v in SEASONS.items())
    light = "\n".join(f'  [data-wk="{k}"] {{ --wk: {v["light"]}; }}' for k, v in SEASONS.items())
    return dark + "\n@media (prefers-color-scheme: light) {\n" + light + "\n}\n"


def wheel_css(wheel_id: str) -> str:
    dark_accent, light_accent = WHEELS[wheel_id]["accent"]
    return (
        f":root {{ --wa: {dark_accent}; --wa-bg: #12151d; }}\n"
        + _season_css()
        + "@media (prefers-color-scheme: light) {\n"
        f"  :root {{ --wa: {light_accent}; --wa-bg: #ffffff; }}\n}}\n"
    )


def _angle(iso: str, year: int) -> float:
    d = date.fromisoformat(iso)
    n = 366 if monthrange(year, 2)[1] == 29 else 365
    return (d.timetuple().tm_yday - 1) / n * 360 - 90


def wheel_art_svg(events: dict, year: int, flip: bool) -> str:
    """The year as a ring: seasonal arcs, an icon at each major festival."""
    cx = cy = 100
    r_ring = 74
    terms = solar_terms(year)
    # Season arcs between the solstices and equinoxes (swapped in the south).
    bounds = {lon: terms[lon].date().isoformat() for lon in (270, 0, 90, 180)}
    arcs = []
    seq = [(f"{year}-01-01", "winter"), (bounds[0], "spring"), (bounds[90], "summer"),
           (bounds[180], "autumn"), (bounds[270], "winter"), (f"{year}-12-31", None)]
    swap = {"winter": "summer", "spring": "autumn", "summer": "winter", "autumn": "spring"}
    for (start, season), (end, _) in zip(seq, seq[1:]):
        if flip:
            season = swap[season]
        a0, a1 = _angle(start, year), _angle(end, year)
        x0, y0 = cx + r_ring * math.cos(math.radians(a0)), cy + r_ring * math.sin(math.radians(a0))
        x1, y1 = cx + r_ring * math.cos(math.radians(a1)), cy + r_ring * math.sin(math.radians(a1))
        large = 1 if (a1 - a0) > 180 else 0
        arcs.append(
            f'<path data-wk="{season}" d="M{x0:.2f},{y0:.2f} A{r_ring},{r_ring} 0 {large} 1 {x1:.2f},{y1:.2f}" '
            f'fill="none" stroke="var(--wk)" stroke-width="5" stroke-linecap="butt" opacity=".55"/>'
        )

    marks = []
    for iso, e in sorted(events.items()):
        ang = math.radians(_angle(iso, year))
        x, y = cx + r_ring * math.cos(ang), cy + r_ring * math.sin(ang)
        if e["major"]:
            marks.append(
                f'<g data-wk="{e["season"]}" style="color:var(--wk)"><title>{e["n"]}</title>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="12" fill="var(--wa-bg)" stroke="var(--wk)" stroke-width="1.8"/>'
                f'<svg x="{x - 8:.2f}" y="{y - 8:.2f}" width="16" height="16" viewBox="0 0 24 24">{icon_inner(e["icon"])}</svg></g>'
            )
        else:
            marks.append(
                f'<g data-wk="{e["season"]}"><title>{e["n"]}</title>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="var(--wk)"/></g>'
            )
    return (
        '<svg class="wheel-art" viewBox="0 0 200 200" aria-hidden="true">'
        '<circle cx="100" cy="100" r="74" fill="none" stroke="var(--wa)" stroke-opacity=".16" stroke-width="22"/>'
        '<circle cx="100" cy="100" r="50" fill="none" stroke="var(--wa)" stroke-opacity=".25" stroke-dasharray="2 5"/>'
        + "".join(arcs) + "".join(marks) +
        f'<text x="100" y="101" text-anchor="middle" font-family="Georgia, serif" font-size="22" '
        f'fill="var(--wa)" letter-spacing="2">{year}</text>'
        '<text x="100" y="117" text-anchor="middle" font-size="8" fill="currentColor" opacity=".65" letter-spacing="2">'
        'YEAR WHEEL</text></svg>'
    )


def _short_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}"


def banner_html(wheel_id: str, events: dict, year: int) -> str:
    spec = WHEELS[wheel_id]
    flip = spec["flip"] and is_southern_hemisphere()
    chips = "".join(
        f'<span class="wheel-chip" data-wk="{e["season"]}">{icon_svg(e["icon"], "wi")}'
        f'<b>{e["n"]}</b><i>{_short_date(iso)}</i></span>'
        for iso, e in sorted(events.items()) if e["major"]
    )
    minor = sum(1 for e in events.values() if not e["major"])
    extra = (f'<p class="wheel-more">Plus {minor} further solar terms, shown as small dots on the wheel '
             f'and marked on their days.</p>') if minor else ""
    south = ('<p class="wheel-south">Southern hemisphere: the festivals are shifted by six months '
             'so they follow your seasons.</p>') if flip else ""
    seasons = "".join(
        f'<span class="wheel-key" data-wk="{k}"><span class="wheel-key-dot"></span>{v["label"]}</span>'
        for k, v in SEASONS.items()
    )
    return (
        '<section class="wheel-banner">'
        f'<div class="wheel-art-wrap">{wheel_art_svg(events, year, flip)}</div>'
        '<div class="wheel-text">'
        f'<div class="wheel-title">{spec["name"]}</div>'
        f'<p class="wheel-blurb">{spec["blurb"]}</p>'
        f'<div class="wheel-chips">{chips}</div>{extra}'
        f'<div class="wheel-keys">{seasons}</div>{south}'
        f'<p class="wheel-note">{spec["note"]}</p>'
        '</div></section>'
    )


def month_strip_html(events: dict, year: int, month: int) -> str:
    """Chips for the month's festivals, shown under the month's grid."""
    items = [(iso, e) for iso, e in sorted(events.items()) if int(iso[5:7]) == month]
    if not items:
        return ""
    chips = "".join(
        f'<span class="wchip{"" if e["major"] else " wminor"}" data-wk="{e["season"]}" '
        f'data-wd="{iso}">{icon_svg(e["icon"], "wi")}<b>{int(iso[8:])}</b>{e["n"]}</span>'
        for iso, e in items
    )
    return f'<div class="wheel-strip">{chips}</div>'
