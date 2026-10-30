# Morning briefing design system

This document is the visual source of truth. Content, facts, section inclusion, narration, and Drive delivery remain controlled by the scheduled task prompt.

## Output contract

- Produce one standalone HTML file in Italian.
- Inline the stylesheet, five WOFF2 fonts, the selected original image, and the generated abstract SVG.
- Use the semantic order in `templates/briefing-shell.html` so visual order and spoken DOM order agree.
- Keep the page background `#F0EEE6`, surrounding wash `#E8E4D8`, primary ink `#2E2C27`, and soft ink `#6B6A63`.
- Add `data-art-image-id` to the root HTML element and `art-board`, `art-source`, and palette metadata in the head.
- Mark the selected artwork and all decorative SVGs `aria-hidden="true"`; use empty image alt text. Decorative SVGs contain no `title`, `desc`, or text nodes.

## Artwork workflow

Run `scripts/select_bulletin_art.py` once. It reads only the public board's own feed, requests original files from `i.pinimg.com`, excludes the last seven successful selections, and falls back to `assets/board-cache.json` when the live board is unavailable. Inspect the result and reject images with screenshot controls or insufficient usable detail.

Run `scripts/art_palette.py` on the downloaded original. Add its CSS variables after the base theme. Preserve the source image bytes and aspect ratio.

Choose the SVG motif from the selected image's visual language:

- Repeated circles or cells: `chromatic-dots`.
- Luminous blocks or broad color transitions: `luminous-fields`.
- Vertical smears, strands, or repeated lines: `woven-striations`.

Call `graphic_from_artwork(image_path, motif)` from `scripts/abstract_graphics.py`, then inline the resulting SVG in `.greeting-graphic`. The motif spans edge to edge behind the greeting and haiku. It uses sampled colors, slow motion, and crisp vector shapes. Do not create sun, mountain, or generic landscape imagery.

## Theme choice

Select one layout from the artwork itself:

- `apertura`: use for square or wide images with a strong focal area. The image enters the opening and shares space with large sans typography.
- `margine`: use for portrait images or color fields. The opening reads like an asymmetric gallery spread with Instrument Serif.
- `corrente`: use for tall images or continuous textures. The image becomes a persistent side column on desktop and a full-width opening band on mobile.

Set the chosen name as the body class. Keep one original image in the opening and at most one quieter echo later on the page.

## Opening

The greeting and three-line haiku share the animated abstract backdrop. On mobile the SVG extends across the full 360-pixel viewport, past the 24-pixel reading gutters. The haiku is at least 15 pixels, medium or semibold, with generous line height. Choose a fixed foreground color that keeps at least 4.5:1 contrast throughout the animation, targeting 7:1. Do not add a blur, wash, panel, halo, outline, or shadow behind the haiku.

## Sections

After the opening, use this order:

1. Needs attention.
2. Resolved.
3. Consulente di carriera.
4. Consulente immobiliare.
5. Orbita.
6. Energia.

The page is editorial rather than card based. Use open space, hairline dividers, strong type hierarchy, and a solid reading surface. Do not use puzzle pieces, tiled content boxes, or dark metric panels.

## Energia

Create four custom inline SVG metrics: angular bolt, veined leaf, contoured droplet, and stacked token bars. Labels and values remain still. Animate only the icon drawings: pulse, sway, float with ripple, and staggered bar growth. Use the palette variables `--icon-energy`, `--icon-leaf`, `--icon-water`, and `--icon-tokens`.

The visual metrics have `aria-hidden="true"` and contain no `title` or `desc`. Put the complete spoken values and comparisons in the following paragraph.

## Motion and accessibility

- Keep travel distances small and cycles slow.
- Never distort or filter the original photograph.
- Under `prefers-reduced-motion: reduce`, disable every animation and display complete static shapes.
- Keep keyboard focus visible on links.
- Verify that the document has no horizontal overflow at 360 pixels.
- Render once at 360 × 780 and once at desktop width before delivery.

## Final assembly

Replace every placeholder in the shell, remove unused optional containers, inline all local dependencies, and extract visible text while ignoring style, script, and SVG. The extracted sequence must match the narration order exactly.
