#!/usr/bin/env python3
"""Choose original artwork from the public Abstract board, once per brief build."""
import argparse
import hashlib
import json
import random
import re
import struct
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

BOARD_URL = "https://de.pinterest.com/lorygerma/abstract/"
USER_AGENT = "Mozilla/5.0 (compatible; MorningBrief/1.0)"
BUNDLED_CACHE = Path(__file__).resolve().parents[1] / "assets" / "board-cache.json"


class StateParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.buffer = []
        self.states = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self.active = attrs.get("id") in ("__PWS_INITIAL_PROPS__", "__PWS_DATA__")
            self.buffer = []

    def handle_data(self, data):
        if self.active:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.active:
            self.states.append(json.loads("".join(self.buffer)))
            self.active = False


def original_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "i.pinimg.com":
        raise ValueError("Artwork must be served by i.pinimg.com over HTTPS")
    match = re.fullmatch(r"/[^/]+/([a-f0-9]{2})/([a-f0-9]{2})/([a-f0-9]{2})/([a-f0-9]{32})\.(jpg|jpeg|png|webp)", parsed.path)
    if not match:
        raise ValueError("Unrecognized Pinterest image address")
    return "https://i.pinimg.com/originals/" + "/".join(match.groups()[:3]) + "/" + match[4] + "." + match[5]


def extract_candidates(html):
    parser = StateParser()
    parser.feed(html)
    candidates = {}
    for state in parser.states:
        redux = state.get("initialReduxState", state.get("props", {}).get("initialReduxState", {}))
        for board_id, board in redux.get("boards", {}).items():
            if board.get("url", "").rstrip("/") != "/lorygerma/abstract":
                continue
            if board.get("privacy") != "public":
                continue
            pins = redux.get("pins", {})
            feed = redux.get("feeds", {}).get("boardfeed:" + board_id, [])
            # Only the board's own feed and board image list, never recommendations.
            images = []
            for item in feed:
                if item.get("type") != "pin":
                    continue
                pin = pins.get(item.get("id"), {})
                image = pin.get("images", {}).get("orig")
                if image:
                    images.append({**image, "dominant_color": pin.get("dominant_color")})
            images.extend(board.get("images", {}).get("236x", []))
            for image in images:
                try:
                    url = original_url(image.get("url", ""))
                except ValueError:
                    continue
                image_id = Path(urlparse(url).path).stem
                if image_id not in candidates:
                    candidates[image_id] = {
                        "image_id": image_id,
                        "image_url": url,
                        "board_url": BOARD_URL,
                        "dominant_color": image.get("dominant_color"),
                    }
    if not candidates:
        raise ValueError("No verified images from the public Abstract board were found")
    return list(candidates.values())


def fetch(url, limit):
    parsed = urlparse(url)
    if url != BOARD_URL and parsed.hostname != "i.pinimg.com":
        raise ValueError("Unexpected download host")
    with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=25) as response:
        final = urlparse(response.url)
        expected = urlparse(url).hostname
        if final.scheme != "https" or final.hostname != expected:
            raise ValueError("Unexpected redirect")
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("Download exceeds size limit")
        return data


def image_size(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8X":
            return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
        if chunk == b"VP8L" and data[20] == 0x2F:
            packed = int.from_bytes(data[21:25], "little")
            return (packed & 0x3FFF) + 1, ((packed >> 14) & 0x3FFF) + 1
        if chunk == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
            return tuple(value & 0x3FFF for value in struct.unpack("<HH", data[26:30]))
    if data.startswith(b"\xff\xd8"):
        index = 2
        while index < len(data):
            if data[index] != 255:
                index += 1
                continue
            while data[index] == 255:
                index += 1
            marker = data[index]
            index += 1
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            size = struct.unpack(">H", data[index:index + 2])[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                height, width = struct.unpack(">HH", data[index + 3:index + 7])
                return width, height
            index += size
    raise ValueError("Unsupported image; expected a valid original JPEG, PNG or WebP")


def choose(candidates, excluded, rng=None):
    eligible = [item for item in candidates if item["image_id"] not in excluded]
    pool = eligible or list(candidates)
    (rng or random.SystemRandom()).shuffle(pool)
    return pool


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artwork"))
    parser.add_argument("--history", type=Path)
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    history_path = args.history or args.output_dir / "history.json"
    cache_path = args.output_dir / "board-cache.json"
    history = json.loads(history_path.read_text()) if history_path.exists() else []
    source = "live-board"
    try:
        candidates = extract_candidates(fetch(BOARD_URL, 8_000_000).decode("utf-8"))
        cache_path.write_text(json.dumps(candidates, indent=2) + "\n")
    except Exception as error:
        fallback_cache = cache_path if cache_path.exists() else BUNDLED_CACHE
        if not fallback_cache.exists():
            raise RuntimeError("Board unavailable and no verified cache exists") from error
        candidates = json.loads(fallback_cache.read_text())
        source = "verified-cache"
        print("Using previously verified board cache: " + str(error), file=sys.stderr)
    excluded = set(args.exclude) | {item["image_id"] for item in history[-7:]}
    errors = []
    for item in choose(candidates, excluded):
        try:
            url = original_url(item["image_url"])
            data = fetch(url, 20_000_000)
            width, height = image_size(data)
            suffix = ".png" if data.startswith(b"\x89PNG") else ".webp" if data.startswith(b"RIFF") else ".jpg"
            target = args.output_dir / (item["image_id"] + suffix)
            target.write_bytes(data)
            metadata = {
                **item, "image_url": url, "path": str(target.resolve()),
                "width": width, "height": height, "sha256": hashlib.sha256(data).hexdigest(),
                "selected_at": datetime.now(timezone.utc).isoformat(),
                "selection_source": source, "candidate_count": len(candidates),
            }
            try:
                from art_palette import extract_palette
                metadata["palette"] = extract_palette(target)
            except ImportError:
                metadata["palette_status"] = "Pillow unavailable; sample drawing colors from the original image during brief design"
                print(metadata["palette_status"], file=sys.stderr)
            (args.output_dir / "selected-art.json").write_text(json.dumps(metadata, indent=2) + "\n")
            history_path.parent.mkdir(parents=True, exist_ok=True)
            history_path.write_text(json.dumps((history + [metadata])[-30:], indent=2) + "\n")
            print(json.dumps(metadata, indent=2))
            return
        except Exception as error:
            errors.append(item["image_id"] + ": " + str(error))
    raise RuntimeError("No original artwork could be downloaded: " + "; ".join(errors))


if __name__ == "__main__":
    main()
