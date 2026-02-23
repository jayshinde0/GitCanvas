import svgwrite
import random

def render(data, config):
    """
    Squid Game Theme - Survival Contrast
    Dark UI with neon pink intensity mapping.
    """

    contributions = data['contributions'][-365:] if len(data['contributions']) > 365 else data['contributions']

    cols = 53
    rows = 7
    width = cols * 15 + 100
    height = rows * 15 + 150

    dwg = svgwrite.Drawing(size=("100%", "100%"), viewBox=f"0 0 {width} {height}")

    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill=config["bg_color"]))

    # Neon particles
    random.seed(21)
    for _ in range(20):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(1, 2)
        dwg.add(dwg.circle(center=(x, y), r=r, fill=config["icon_color"], opacity=0.18))

    # Title
    dwg.add(dwg.text(
        "SURVIVAL ACTIVITY",
        insert=(width // 2, 30),
        text_anchor="middle",
        font_size=config["title_font_size"],
        font_family=config["font_family"],
        fill=config["title_color"],
        style="letter-spacing: 2px; font-weight: bold;"
    ))

    box_size = 12
    gap = 3
    start_x = 50
    start_y = 60

    max_count = max([day['count'] for day in contributions]) if contributions else 1

    for i, day in enumerate(contributions):
        count = day['count']
        col = i // 7
        row = i % 7

        x = start_x + col * (box_size + gap)
        y = start_y + row * (box_size + gap)

        if count == 0:
            fill = "#1a1a1a"
        elif count <= max_count * 0.25:
            fill = "#3b0a1a"
        elif count <= max_count * 0.5:
            fill = "#7a1036"
        elif count <= max_count * 0.75:
            fill = "#c2185b"
        else:
            fill = "#ff2e88"
            dwg.add(dwg.rect(
                insert=(x - 1, y - 1),
                size=(box_size + 2, box_size + 2),
                fill="none",
                stroke=config["title_color"],
                stroke_width=1.2,
                opacity=0.7
            ))

        dwg.add(dwg.rect(
            insert=(x, y),
            size=(box_size, box_size),
            fill=fill,
            rx=2,
            ry=2
        ))

    # Border
    dwg.add(dwg.rect(
        insert=(0.5, 0.5),
        size=(width - 1, height - 1),
        fill="none",
        stroke=config["border_color"],
        stroke_width=1
    ))

    return dwg.tostring()
