from individual import Individual

CANVAS_WIDTH = 3200
CANVAS_HEIGHT = 800


def generate_svg(
    individual: Individual,
    width: int = CANVAS_WIDTH,
    height: int = CANVAS_HEIGHT,
    stroke_color: str = "#1a1a1a",
    stroke_width: float = 2.0,
) -> str:
    """Return SVG markup for *individual* as a string.

    The wave wraps around the canvas width (egg_width_mult × 1.6), producing
    multiple overlapping passes that create the organic dense-line pattern.
    Each wrap is a separate <polyline> element so the SVG path is clean.
    """
    segments = individual.compute_segments(canvas_width=width, canvas_height=height)

    paths = []
    for seg in segments:
        if len(seg) < 2:
            continue
        start = f"M {seg[0][0]:.2f},{seg[0][1]:.2f}"
        rest = " L ".join(f"{x:.2f},{y:.2f}" for x, y in seg[1:])
        d = f"{start} L {rest}"
        paths.append(
            f'  <path d="{d}"\n'
            f'    stroke="{stroke_color}" stroke-width="{stroke_width}"\n'
            f'    fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        )

    body = "\n".join(paths)

    num_layers = 9
    layer_colors = [
        "#e63946",  # 1 red
        "#f4a261",  # 2 orange
        "#e9c46a",  # 3 yellow
        "#2a9d8f",  # 4 green
        "#457b9d",  # 5 blue
        "#9b5de5",  # 6 purple
        "#f72585",  # 7 pink
        "#4cc9f0",  # 8 light blue
        "#8ecae6",  # 9 sky blue
    ]
    layers = []
    for i in range(num_layers, 0, -1):
        color = layer_colors[i - 1]
        content = f'\n{body}\n  ' if i == 1 else ''
        layers.append(
            f'  <g inkscape:label="{i}_Layer" inkscape:groupmode="layer" id="layer{i}"'
            f' inkscape:color="{color}" clip-path="url(#canvas)">{content}</g>'
        )
    layers_str = "\n".join(layers)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"\n'
        f'     width="{width}" height="{height}"\n'
        f'     viewBox="0 0 {width} {height}"\n'
        f'     overflow="hidden">\n'
        f'  <defs>\n'
        f'    <clipPath id="canvas">\n'
        f'      <rect width="{width}" height="{height}"/>\n'
        f'    </clipPath>\n'
        f'  </defs>\n'
        f'{layers_str}\n'
        f'</svg>\n'
    )


def save_svg(individual: Individual, filepath: str, **kwargs) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(generate_svg(individual, **kwargs))
