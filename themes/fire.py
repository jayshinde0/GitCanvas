import svgwrite
import random

def render(data, config):
    """
    Fire Heatmap Theme
    Uses UI colors from config JSON and maps activity intensity to heat colors.
    """

    contributions = data['contributions'][-365:] if len(data['contributions']) > 365 else data['contributions']

    cols = 53
    rows = 7
    width = cols * 15 + 100
    height = rows * 15 + 150

    dwg = svgwrite.Drawing(size=("100%", "100%"), viewBox=f"0 0 {width} {height}")

    # Background
    dwg.add(dwg.rect(
        insert=(0, 0),
        size=("100%", "100%"),
        fill=config["bg_color"]
    ))

    # Subtle ember particles
    random.seed(42)
    for _ in range(25):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(1, 2)
        dwg.add(dwg.circle(
            center=(x, y),
            r=r,
            fill=config["icon_color"],
            opacity=0.15
        ))

    # Title
    dwg.add(dwg.text(
        "ACTIVITY HEATMAP",
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

        # Heat color mapping
        if count == 0:
            fill = "#1a1a1a"
            opacity = 0.4
        elif count <= max_count * 0.25:
            fill = "#5a1a00"  # ember
            opacity = 0.6
        elif count <= max_count * 0.5:
            fill = "#cc3d00"  # orange flame
            opacity = 0.8
        elif count <= max_count * 0.75:
            fill = "#ff2400"  # strong red
            opacity = 0.9
        else:
            fill = "#ffd000"  # peak heat (yellow)
            opacity = 1.0
            # glow border for peak intensity
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
            ry=2,
            opacity=opacity
        ))

    # Footer label
    dwg.add(dwg.text(
        "INTENSITY MODE",
        insert=(10, height - 10),
        font_size=config["text_font_size"],
        font_family=config["font_family"],
        fill=config["text_color"],
        opacity=0.6
    ))

    # Border (matches schema)
    dwg.add(dwg.rect(
        insert=(0.5, 0.5),
        size=(width - 1, height - 1),
        fill="none",
        stroke=config["border_color"],
        stroke_width=1
    ))

    return dwg.tostring()
