"""Derive drawing and icon colors from the selected original artwork."""
import colorsys
import math
from PIL import Image

PAPER = (240, 238, 230)


def hex_color(rgb):
    return "#" + "".join(f"{round(value):02x}" for value in rgb)


def luminance(rgb):
    channels = [value / 255 for value in rgb]
    channels = [value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4 for value in channels]
    return sum(value * weight for value, weight in zip(channels, (.2126, .7152, .0722)))


def contrast(rgb, background=PAPER):
    a, b = sorted((luminance(rgb), luminance(background)))
    return (b + .05) / (a + .05)


def readable(rgb, minimum=3):
    # Shade the sampled hue only as much as required for its small line drawing.
    for amount in range(101):
        color = tuple(round(value * (1 - amount / 100)) for value in rgb)
        if contrast(color) >= minimum:
            return color
    return (46, 44, 39)


def mix(rgb, amount):
    return tuple(round(value * (1 - amount) + paper * amount) for value, paper in zip(rgb, PAPER))


def extract_palette(path):
    image = Image.open(path).convert("RGB")
    image.thumbnail((256, 256), Image.Resampling.LANCZOS)
    quantized = image.quantize(colors=24, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    colors = []
    for count, index in sorted(quantized.getcolors(), reverse=True):
        rgb = tuple(palette[index * 3:index * 3 + 3])
        hue, light, saturation = colorsys.rgb_to_hls(*(value / 255 for value in rgb))
        colors.append({"rgb": rgb, "count": count, "hue": hue, "light": light, "sat": saturation,
                       "chroma": (max(rgb) - min(rgb)) / 255})
    structural = [item for item in colors if .12 <= item["light"] <= .72 and item["sat"] >= .06] or colors
    dominant = structural[0]
    secondary = max(colors, key=lambda item: item["count"] * math.dist(item["rgb"], dominant["rgb"]))
    deep = next((item for item in structural if item["light"] < .45), dominant)
    dark = min(colors, key=lambda item: item["light"])
    warm_pool = [item for item in colors if (item["hue"] <= .18 or item["hue"] >= .94)
                 and .18 <= item["light"] <= .8 and item["chroma"] >= .1]
    warm = max(warm_pool, key=lambda item: item["count"] * item["chroma"]) if warm_pool else dominant
    cool_pool = [item for item in colors if .35 <= item["hue"] <= .78
                 and .12 <= item["light"] <= .85 and item["chroma"] >= .08]
    cool = max(cool_pool, key=lambda item: item["count"] * item["chroma"]) if cool_pool else dark
    values = {
        "land-back": mix(secondary["rgb"], .65),
        "land-middle": mix(dominant["rgb"], .28),
        "land-front": readable(deep["rgb"], 2.8),
        "land-sun": readable(warm["rgb"], 2.8),
        "land-water": readable(cool["rgb"], 2.8),
        "land-current": mix(cool["rgb"], .78),
        "icon-energy": readable(warm["rgb"]),
        "icon-leaf": readable(dominant["rgb"]),
        "icon-water": readable(cool["rgb"]),
        "icon-tokens": readable(dark["rgb"]),
        "art-accent": readable(warm["rgb"], 4.5),
        # The graphic is tinted over light paper, so use an almost-black source hue.
        "haiku-ink": tuple(round(value * .12) for value in dark["rgb"]),
    }
    return {
        "colors": {key: hex_color(value) for key, value in values.items()},
        "source_swatches": [hex_color(item["rgb"]) for item in colors[:8]],
        "method": "24 representative image colors; sampled hues shaded for contrast and tinted with page paper",
    }


def palette_css(palette):
    return ":root{" + ";".join(f"--{key}:{value}" for key, value in palette["colors"].items()) + "}"
