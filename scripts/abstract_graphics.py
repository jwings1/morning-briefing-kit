"""Vector compositions echoing the selected artwork's shapes and sampled colors."""
from PIL import Image


def graphic_from_artwork(path, motif):
    image = Image.open(path).convert('RGB')

    def sample(x, y):
        pixel = image.getpixel((min(image.width - 1, int(x * image.width)), min(image.height - 1, int(y * image.height))))
        return '#' + ''.join(f'{channel:02x}' for channel in pixel)

    shapes = []
    defs = ''
    if motif == 'chromatic-dots':
        # Follow the photograph's circular grid and horizontal color changes.
        for row in range(8):
            dots = []
            for col in range(15):
                x, y = col * 25 - 5, row * 27 + 7
                color = sample((col + .5) / 15, (row + .5) / 8 * .84)
                radius = 8 + ((col * 7 + row * 3) % 5) * .65
                delay = -(row * .8 + col * .27)
                dots.append(f'<circle class="abstract-dot" cx="{x}" cy="{y}" r="{radius:.2f}" fill="{color}" style="animation-delay:{delay:.2f}s"/>')
                if (col + row) % 4 == 0:
                    dots.append(f'<circle cx="{x}" cy="{y}" r="{radius + 2:.2f}" fill="none" stroke="{color}" stroke-width=".6" opacity=".7"/>')
            shapes.append(f'<g class="abstract-row" style="animation-delay:{-row * 1.3}s">{"".join(dots)}</g>')
    elif motif == 'luminous-fields':
        # Translate the luminous rectangular field into interleaved color veils.
        stops = ''.join(f'<stop offset="{i * 25}%" stop-color="{sample(.16 + i * .17, .44)}"/>' for i in range(5))
        defs = f'<linearGradient id="field-spectrum">{stops}</linearGradient><filter id="field-diffusion" x="-35%" y="-35%" width="170%" height="170%"><feGaussianBlur stdDeviation="12"/></filter>'
        shapes.append('<g filter="url(#field-diffusion)"><rect class="abstract-field" x="-25" y="16" width="410" height="190" rx="40" fill="url(#field-spectrum)" opacity=".7"/>')
        for i, (x, y, w, h) in enumerate([(-20, 65, 75, 140), (58, -20, 80, 215), (150, 10, 72, 235), (235, -12, 68, 205), (300, 42, 80, 190)]):
            color = sample(.17 + i * .16, .22 if i % 2 else .78)
            shapes.append(f'<rect class="abstract-field offset" x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="{color}" style="animation-delay:{-i * 2.1}s"/>')
        shapes.append('</g>')
    elif motif == 'woven-striations':
        # The source has fine vertical smears beneath a descending diagonal edge.
        defs = '<clipPath id="striations-edge"><path d="M-15 42C90 56 190 92 375 135V235H-15Z"/></clipPath>'
        shapes.append('<g clip-path="url(#striations-edge)">')
        for i in range(110):
            color = sample((i + .5) / 110, .86)
            shapes.append(f'<path class="abstract-thread" d="M{i * 3.5 - 12:.1f} 0v238" stroke="{color}" stroke-width="{2.1 + i % 3 * .5:.1f}" style="animation-delay:{-i * .16:.2f}s"/>')
        shapes.append('</g>')
        for i in range(5):
            y = 42 + i * 5
            shapes.append(f'<path class="abstract-filament" pathLength="1" d="M-15 {y}C90 {y + 14} 190 {y + 50} 375 {y + 93}" fill="none" stroke="{sample(.14 + i * .16, .39)}" stroke-width="{1.3 if i % 2 else 2.4}" style="animation-delay:{-i * 2}s"/>')
    else:
        raise ValueError(f'Unknown artwork motif: {motif}')
    return f'<svg xmlns="http://www.w3.org/2000/svg" class="abstract-art" data-motif="{motif}" viewBox="0 0 360 230" aria-hidden="true" focusable="false"><defs>{defs}</defs>{"".join(shapes)}</svg>'
