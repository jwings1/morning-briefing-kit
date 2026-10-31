# Morning Briefing Kit

Official visual composition kit for the automated morning briefing.

The repository contains the responsive theme, the semantic HTML scaffold, bundled fonts, the verified Pinterest artwork selector, palette extraction, and the abstract SVG generator. The finished briefing remains a single self-contained HTML file: inline the CSS, fonts, selected image, and generated SVG before delivery.

## Start here

1. Read [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md).
2. Use [`templates/briefing-shell.html`](templates/briefing-shell.html) for DOM order and class names.
3. Inline [`themes/morning-brief.css`](themes/morning-brief.css).
4. Fill and inline [`components/energy-strip.html`](components/energy-strip.html).
5. Run `python3 scripts/select_bulletin_art.py --output-dir artwork` once per briefing.
6. Derive colors with `scripts/art_palette.py` and generate the opening SVG with `scripts/abstract_graphics.py`.
7. Render at 360 × 780 and desktop width before upload.

The content prompt owns facts, narration, section inclusion, and delivery. This repository owns visual composition and artwork handling.

## Dependencies

- Python 3.10 or newer.
- Pillow for palette extraction and abstract graphics.
- Network access to the public Pinterest board on the first selection attempt. A verified board cache is bundled for fallback.

The font files are bundled under their SIL Open Font License texts in `assets/fonts/`.

## Stable URLs

The scheduled prompt can load the kit through:

- Repository: `https://github.com/jwings1/morning-briefing-kit`
- Manifest: `https://raw.githubusercontent.com/jwings1/morning-briefing-kit/main/kit.json`
- Design specification: `https://raw.githubusercontent.com/jwings1/morning-briefing-kit/main/DESIGN_SYSTEM.md`

Board images remain the property of their respective creators. The selector downloads an original only for the generated personal briefing; this repository stores URLs and metadata, not the artwork files.
