import svgwrite
import random
def render(data,config):
    """
    Wednesday Theme - Gothic Academia
    Dar,minimal, eerie grayscale palette with subtle violet accents.
    """
    
    contributions = data['contributions'][-365:] if len(data['contributions'])>365 else data['contributions']
    
    cols =53
    rows=7
    width = cols*15+100
    height = rows*15+150
    
    dwg = svgwrite.Drawing(size=("100%","100%"),viewBox=f"0 0 {width} {height}")
    dwg.add(dwg.rect(insert=(0,0), size=("100%","100%"), fill=config["bg_color"]))
    
    random.seed(7)
    for _ in range(18):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(1, 2)
        dwg.add(dwg.circle(center=(x, y), r=r, fill=config["icon_color"], opacity=0.12))
    dwg.add(dwg.text(
        "GOTHIC ACTIVITY",
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
            fill = "#2c2c2c"
        elif count <= max_count * 0.5:
            fill = "#3a3a3a"
        elif count <= max_count * 0.75:
            fill = "#5a5a5a"
        else:
            fill = "#8a6cff"  # subtle gothic violet accent

        dwg.add(dwg.rect(
            insert=(x, y),
            size=(box_size, box_size),
            fill=fill,
            rx=1,
            ry=1
        ))

    dwg.add(dwg.rect(
        insert=(0.5, 0.5),
        size=(width - 1, height - 1),
        fill="none",
        stroke=config["border_color"],
        stroke_width=1
    ))

    return dwg.tostring()
    