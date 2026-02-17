import math
import random
import svgwrite
from themes.styles import THEMES

def draw_stats_card(data, theme_name="Default", show_options=None, custom_colors=None):
    """
    Generates the Main Stats Card SVG.
    data: dict with user stats
    theme_name: string key from THEMES
    show_options: dict with toggles (e.g. {'stars': True, 'prs': False})
    """
    if show_options is None:
        show_options = {"stars": True, "commits": True, "repos": True, "followers": True}
        
    theme = THEMES.get(theme_name, THEMES["Default"]).copy()
    if custom_colors:
        theme.update(custom_colors)

    
    width = 450
    # Calculate height dynamically based on visible items
    base_height = 50
    item_height = 25
    visible_items = sum(1 for k, v in show_options.items() if v)
    height = base_height + (visible_items * item_height) + 10
    
    dwg = svgwrite.Drawing(size=("100%", "100%"), viewBox=f"0 0 {width} {height}")
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=10, ry=10, 
                     fill=theme["bg_color"], stroke=theme["border_color"], stroke_width=2))
    if theme_name == "Stranger_things":
        # Floating particles in background
        random.seed(42)
        for i in range(12):
            x = random.randint(20, width-20)
            y = random.randint(20, height-20)
            r = random.randint(1, 2)
            dwg.add(dwg.circle(center=(x, y), r=r, fill="#ffffff", opacity=0.2))
        
        # Mini demogorgon in corner
        demo_x = width - 40
        demo_y = 35
        dwg.add(dwg.circle(center=(demo_x, demo_y), r=12, fill="#330000", opacity=0.5))
        
        # Petals
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            x1 = demo_x + 9 * math.cos(rad)
            y1 = demo_y + 9 * math.sin(rad)
            x2 = demo_x + 15 * math.cos(rad)
            y2 = demo_y + 15 * math.sin(rad)
            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke="#ff0000", stroke_width=1, opacity=0.4))
        
        # Red glow around border
        dwg.add(dwg.rect(insert=(2, 2), size=(width-4, height-4), rx=9, ry=9, 
                        fill="none", stroke="#ff0000", stroke_width=1, opacity=0.3))
    elif theme_name == "Pacman":
        # Pac-Man character
        pac_x = width - 45
        pac_y = 30
        pacman_path = dwg.path(d=f"M {pac_x} {pac_y} " +
                              f"L {pac_x + 12} {pac_y - 10} " +
                              f"A 12 12 0 1 1 {pac_x + 12} {pac_y + 10} Z",
                              fill="#ffff00", stroke="#000000", stroke_width=0.5)
        dwg.add(pacman_path)
        dwg.add(dwg.circle(center=(pac_x + 8, pac_y - 3), r=2, fill="#000000"))
        
        # Pellets trail
        pellet_y = height - 15
        for i in range(5):
            pellet_x = 30 + i * 20
            dwg.add(dwg.circle(center=(pellet_x, pellet_y), r=3, fill="#ffff00"))
        
        # Ghost
        ghost_x = 25
        ghost_y = 25
        ghost_body = dwg.path(
            d=f"M {ghost_x} {ghost_y + 5} " +
              f"A 7 7 0 0 1 {ghost_x + 14} {ghost_y + 5} " +
              f"L {ghost_x + 14} {ghost_y + 14} " +
              f"L {ghost_x + 11} {ghost_y + 11} " +
              f"L {ghost_x + 7} {ghost_y + 14} " +
              f"L {ghost_x + 3} {ghost_y + 11} " +
              f"L {ghost_x} {ghost_y + 14} Z",
            fill="#ff0000", opacity=0.7
        )
        dwg.add(ghost_body)
        
        # Ghost eyes
        dwg.add(dwg.circle(center=(ghost_x + 5, ghost_y + 8), r=2, fill="#ffffff"))
        dwg.add(dwg.circle(center=(ghost_x + 10, ghost_y + 8), r=2, fill="#ffffff"))

    # Title
    font_family = theme["font_family"]
    dwg.add(dwg.text(f"{data['username']}'s Stats", insert=(20, 35), 
                     fill=theme["title_color"], font_size=theme["title_font_size"], font_family=font_family, font_weight="bold"))
    
    # Stats
    start_y = 65
    current_y = start_y
    text_color = theme["text_color"]
    font_size = theme["text_font_size"]
    
    # Logic to handle N/A display for commits if the value is 0 (API error)
    commit_val = data.get('total_commits', 0)
    # If commit_val is 0, we show "N/A", otherwise we show the number
    display_commits = str(commit_val) if commit_val > 0 else "N/A"

    stats_map = [
        ("stars", "Total Stars", f"{data.get('total_stars', 0)}"),
        ("commits", "Total Commits", display_commits),
        ("repos", "Public Repos", f"{data.get('public_repos', 0)}"),
        ("followers", "Followers", f"{data.get('followers', 0)}")
    ]
    
    for key, label, value in stats_map:
        if show_options.get(key, True):
            # Icon approximation (Circle)
            dwg.add(dwg.circle(center=(30, current_y - 5), r=4, fill=theme["icon_color"]))
            
            # Label
            dwg.add(dwg.text(f"{label}:", insert=(45, current_y), 
                             fill=text_color, font_size=font_size, font_family=font_family))
            
            # Value (Right aligned roughly)
            dwg.add(dwg.text(f"{value}", insert=(width - 40, current_y), 
                             fill=text_color, font_size=font_size, font_family=font_family, text_anchor="end", font_weight="bold"))
                             
            current_y += item_height
            
    return dwg.tostring()
