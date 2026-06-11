from __future__ import annotations

import math
import random

from tenderness.cairo_backend.color_patterns import (
    ColorStop,
    ImagePatternSpec,
    LinearGradientColorSpec,
    SolidColorSpec,
)
from tenderness.colors.color_selector import Color, ColorSelector

COLOR_SELECTOR = ColorSelector()

# --------------------------
# Colors from predefined color groups
# --------------------------
BLACK = COLOR_SELECTOR.by_names(color_names=["black"], color_group_name="CSS4")[0]
WHITE = COLOR_SELECTOR.by_names(color_names=["white"], color_group_name="CSS4")[0]
RED = COLOR_SELECTOR.by_names(color_names=["red"], color_group_name="CSS4")[0]
GREEN = COLOR_SELECTOR.by_names(color_names=["green"], color_group_name="CSS4")[0]
BLUE = COLOR_SELECTOR.by_names(color_names=["blue"], color_group_name="CSS4")[0]


# --------------------------
# Custom colors
# --------------------------
WOOD_BARK = Color.from_hex(
    color_name="wood_bark",
    color_group_name="CUSTOM_GROUP",
    hex_color="#2c2520",
)
NINJA_PRINCESS = Color.from_hex(
    color_name="ninja_princess",
    color_group_name="CUSTOM_GROUP",
    hex_color="#7a5590",
)
NAMIBIA = Color.from_hex(
    color_name="namibia",
    color_group_name="CUSTOM_GROUP",
    hex_color="#7a6e66",
)
SCENTED_SPRING = Color.from_hex(
    color_name="scented_spring",
    color_group_name="CUSTOM_GROUP",
    hex_color="#e5d4ef",
)
VEILING_WATERFALLS = Color.from_hex(
    color_name="veiling_waterfalls",
    color_group_name="CUSTOM_GROUP",
    hex_color="#d6e6ff",
)
PAPAYA_WHIP = Color.from_hex(
    color_name="papaya_whip",
    color_group_name="CUSTOM_GROUP",
    hex_color="#fff0d4",
)

DEEP_LAGOON = Color.from_hex(
    color_name="deep_lagoon",
    color_group_name="CUSTOM_GROUP",
    hex_color="#065666",
)
COBALT_NIGHT = Color.from_hex(
    color_name="cobalt_night",
    color_group_name="CUSTOM_GROUP",
    hex_color="#1237a0",
)
VOID_VIOLET = Color.from_hex(
    color_name="void_violet",
    color_group_name="CUSTOM_GROUP",
    hex_color="#4c1d95",
)
PHANTOM_ORCHID = Color.from_hex(
    color_name="phantom_orchid",
    color_group_name="CUSTOM_GROUP",
    hex_color="#7e0d8f",
)


# --------------------------
# Solid color specs
# --------------------------
SOLID_BLACK = SolidColorSpec(color=BLACK)
SOLID_WHITE = SolidColorSpec(color=WHITE)
SOLID_WOOD_BARK = SolidColorSpec(color=WOOD_BARK)
SOLID_NINJA_PRINCESS = SolidColorSpec(color=NINJA_PRINCESS)
SOLID_NAMIBIA = SolidColorSpec(color=NAMIBIA)
SOLID_SCENTED_SPRING = SolidColorSpec(color=SCENTED_SPRING)
SOLID_VEILING_WATERFALLS = SolidColorSpec(color=VEILING_WATERFALLS)
SOLID_PAPAYA_WHIP = SolidColorSpec(color=PAPAYA_WHIP)
SOLID_DEEP_LAGOON = SolidColorSpec(color=DEEP_LAGOON)
SOLID_COBALT_NIGHT = SolidColorSpec(color=COBALT_NIGHT)
SOLID_VOID_VIOLET = SolidColorSpec(color=VOID_VIOLET)
SOLID_PHANTOM_ORCHID = SolidColorSpec(color=PHANTOM_ORCHID)


# --------------------------
# Linear gradient color specs
# --------------------------
def angle_to_points(deg: float, w: float, h: float) -> tuple[float, float, float, float]:
    """Convert a CSS-style gradient angle to cairo (x0,y0) → (x1,y1)."""
    rad = math.radians(deg)
    cx, cy = w / 2, h / 2
    # half-length of the gradient line across the bounding box
    half = abs(w * math.sin(rad)) / 2 + abs(h * math.cos(rad)) / 2
    dx, dy = math.sin(rad), -math.cos(rad)
    return (
        cx - dx * half,
        cy - dy * half,  # x0, y0
        cx + dx * half,
        cy + dy * half,  # x1, y1
    )


LG_ROYAL_SMOKE = LinearGradientColorSpec(
    *angle_to_points(deg=145, w=1280, h=720),
    stops=(
        ColorStop(offset=0.0, color=WOOD_BARK),
        ColorStop(offset=0.45, color=NINJA_PRINCESS),
        ColorStop(offset=1.0, color=SCENTED_SPRING),
    ),
)

LG_DUSK_CANOPY = LinearGradientColorSpec(
    *angle_to_points(deg=160, w=1280, h=720),
    stops=(
        ColorStop(offset=0.0, color=SCENTED_SPRING),
        ColorStop(offset=1.0, color=VEILING_WATERFALLS),
    ),
)

LG_ABYSS_BLOOM = LinearGradientColorSpec(
    *angle_to_points(deg=105, w=1280, h=720),
    stops=(
        ColorStop(offset=0.00, color=DEEP_LAGOON),
        ColorStop(offset=0.33, color=COBALT_NIGHT),
        ColorStop(offset=0.66, color=VOID_VIOLET),
        ColorStop(offset=1.00, color=PHANTOM_ORCHID),
    ),
)

LG_DEEP_CURRENT = LinearGradientColorSpec(
    *angle_to_points(deg=105, w=1280, h=720),
    stops=(
        ColorStop(offset=0.0, color=DEEP_LAGOON),
        ColorStop(offset=1.0, color=VOID_VIOLET),
    ),
)

# --------------------------
# Multi-script text sample
# --------------------------
english = """Text Rendering Hates You"""
spanish = """La representación de texto te odia"""
assamese = """টেক্সট ৰেণ্ডাৰে আপোনাক ঘৃণা কৰে"""
arabic = """عرض النصوص يكرهك"""
hebrew = """עיבוד טקסט שונא אותך"""
hindi = """टटेक्स्ट रेंडरिंग आपसे नफ़रत करता है"""
thai = """การแสดงผลข้อความเกลียดคุณ"""
chinese_simplified = """文本渲染跟你作对"""
kazakh = """Мәтінді көрсету сізді жек көреді"""
armenian = """Տեքստի մատուցումը ատում է ձեզ"""
japanese = """テキストレンダリングはあなたを嫌っています"""
korean = """텍스트 렌더링이 당신을 싫어합니다"""
hebrew = """עיבוד טקסט שונא אותך"""
russian = """Отображение текста вас ненавидит"""
french = """Le rendu de texte vous déteste"""
german = """Die Textdarstellung hasst dich"""
bulgarian = """Текстовото рендиране те мрази"""
qeqchi = """Lix k’utb’esinkil li tz’iib’anb’il esil xik’ naril laa’at ."""  # noqa: RUF001
greek = """Η απόδοση κειμένου σε μισεί"""  # noqa: RUF001
serbian = """Приказивање текста мрзи те"""
tigrinya = """ጽሑፍ ምቕራብ ይጸልኣካ"""
secret_language = "[REDACTED_BY] ████ ███ █ ████"

multilingual_texts = [
    spanish,
    assamese,
    arabic,
    hebrew,
    hindi,
    thai,
    chinese_simplified,
    kazakh,
    armenian,
    japanese,
    korean,
    russian,
    french,
    german,
    bulgarian,
    qeqchi,
    greek,
    serbian,
    tigrinya,
    secret_language,
]


def make_multilingual_sample(texts: list[str], seed: int = 42) -> str:
    rng = random.Random(seed)
    shuffled = rng.sample(texts, len(texts))  # no mutation
    return f"It's definitely a good translation from English 😂\nSource: {english}\n\n" + "\n".join(
        f"{i}) {text}" for i, text in enumerate(shuffled, 1)
    )


MULTILINGUAL_SAMPLE = make_multilingual_sample(multilingual_texts, seed=12345)


# --------------------------
# Image pattern specs
# --------------------------
IMP_COFFEE = ImagePatternSpec(path="images/coffee_1280_853.png")
