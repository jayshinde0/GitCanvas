import svgwrite
import math

def render(data):
    """
    Pac-Man Theme - Wakka Wakka!
    Pac-Man eats through contributions. High activity = power pellets
    Animated ghosts chase through the grid
    """
    contributions = data['contributions'][-365:] if len(data['contributions']) > 365 else data['contributions']
    
    cols = 53
    rows = 7
    width = cols * 15 + 100
    height = rows * 15 + 100
    
    dwg = svgwrite.Drawing(size=("100%", "100%"), viewBox=f"0 0 {width} {height}")
    
    # Classic arcade black background
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="#000000"))
    
    # Title with arcade font style
    dwg.add(dwg.text("PAC-MAN COMMITS", insert=(width//2, 30), 
                     text_anchor="middle", font_size="22px", font_family="monospace",
                     fill="#ffff00", style="font-weight: bold;"))
    
    box_size = 12
    gap = 3
    start_x = 50
    start_y = 60
    
    max_count = max([day['count'] for day in contributions]) if contributions else 1
    
    # Draw maze-like grid lines
    for col in range(cols + 1):
        x = start_x - gap + col * (box_size + gap)
        dwg.add(dwg.line(start=(x, start_y - gap), end=(x, start_y + rows * (box_size + gap)), 
                        stroke="#1919a6", stroke_width=1, opacity=0.3))
    
    for row in range(rows + 1):
        y = start_y - gap + row * (box_size + gap)
        dwg.add(dwg.line(start=(start_x - gap, y), end=(start_x + cols * (box_size + gap), y), 
                        stroke="#1919a6", stroke_width=1, opacity=0.3))
    
    for i, day in enumerate(contributions):
        msg_count = day['count']
        col = i // 7
        row = i % 7
        
        x = start_x + col * (box_size + gap) + box_size//2
        y = start_y + row * (box_size + gap) + box_size//2
        
        if msg_count == 0:
            # Empty space - small dot
            dwg.add(dwg.circle(center=(x, y), r=2, fill="#333333"))
        elif msg_count >= max_count * 0.75:
            # Power pellet (high activity)
            dwg.add(dwg.circle(center=(x, y), r=6, fill="#ffb8ae"))
            # Pulsing effect
            dwg.add(dwg.circle(center=(x, y), r=8, fill="none", 
                             stroke="#ffb8ae", stroke_width=2, opacity=0.5))
        else:
            # Regular pellet
            intensity = msg_count / max_count
            if intensity < 0.33:
                fill_color = "#4169e1"  # Blue
            elif intensity < 0.66:
                fill_color = "#ff8c00"  # Orange
            else:
                fill_color = "#ffff00"  # Yellow
            
            dwg.add(dwg.circle(center=(x, y), r=4, fill=fill_color))
    
    # Draw Pac-Man character
    pacman_x = 30
    pacman_y = start_y + (rows * (box_size + gap)) // 2
    
    # Pac-Man body
    pacman_path = dwg.path(d=f"M {pacman_x} {pacman_y} " +
                          f"L {pacman_x + 15} {pacman_y - 10} " +
                          f"A 15 15 0 1 1 {pacman_x + 15} {pacman_y + 10} Z",
                          fill="#ffff00", stroke="#000000", stroke_width=1)
    dwg.add(pacman_path)
    
    # Pac-Man eye
    dwg.add(dwg.circle(center=(pacman_x + 8, pacman_y - 5), r=2, fill="#000000"))
    
    # Draw ghosts
    ghost_colors = ["#ff0000", "#ffb8ae", "#00ffff", "#ffb8ff"]
    for i, color in enumerate(ghost_colors):
        ghost_x = width - 80 + i * 18
        ghost_y = 50
        
        # Ghost body (rounded top, wavy bottom)
        ghost_body = dwg.path(
            d=f"M {ghost_x} {ghost_y + 10} " +
              f"A 8 8 0 0 1 {ghost_x + 16} {ghost_y + 10} " +
              f"L {ghost_x + 16} {ghost_y + 20} " +
              f"L {ghost_x + 13} {ghost_y + 17} " +
              f"L {ghost_x + 10} {ghost_y + 20} " +
              f"L {ghost_x + 7} {ghost_y + 17} " +
              f"L {ghost_x + 4} {ghost_y + 20} " +
              f"L {ghost_x} {ghost_y + 20} Z",
            fill=color, stroke="#000000", stroke_width=0.5
        )
        dwg.add(ghost_body)
        
        # Ghost eyes
        dwg.add(dwg.circle(center=(ghost_x + 5, ghost_y + 12), r=2, fill="#ffffff"))
        dwg.add(dwg.circle(center=(ghost_x + 11, ghost_y + 12), r=2, fill="#ffffff"))
        dwg.add(dwg.circle(center=(ghost_x + 5, ghost_y + 12), r=1, fill="#0000ff"))
        dwg.add(dwg.circle(center=(ghost_x + 11, ghost_y + 12), r=1, fill="#0000ff"))
    
    # Score text
    total_commits = sum([day['count'] for day in contributions])
    dwg.add(dwg.text(f"SCORE: {total_commits}", insert=(10, height - 15), 
                     font_size="12px", font_family="monospace",
                     fill="#ffff00", style="font-weight: bold;"))
    
    return dwg.tostring()