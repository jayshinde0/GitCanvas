import svgwrite
import math
import random

def render(data):
    """
    Cricket Theme - Stadium with Cricket Field
    Contributions are runs scored on the cricket field
    High activity = sixes and boundaries
    """
    contributions = data['contributions'][-365:] if len(data['contributions']) > 365 else data['contributions']
    
    cols = 53
    rows = 7
    width = cols * 15 + 120
    height = rows * 15 + 160
    
    dwg = svgwrite.Drawing(size=("100%", "100%"), viewBox=f"0 0 {width} {height}")
    
    # Cricket field gradient background
    gradient = dwg.defs.add(dwg.radialGradient(id="cricket_field", cx="50%", cy="50%"))
    gradient.add_stop_color(offset="0%", color="#2d7a2d")
    gradient.add_stop_color(offset="100%", color="#1a5f1a")
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="url(#cricket_field)"))
    
    # Stadium lights
    for i in range(4):
        light_x = 50 + i * (width - 100) / 3
        light_y = 20
        # Light pole
        dwg.add(dwg.line(start=(light_x, light_y), end=(light_x, light_y - 15), 
                        stroke="#8b8b8b", stroke_width=2))
        # Light glow
        dwg.add(dwg.circle(center=(light_x, light_y - 15), r=6, fill="#ffeb3b", opacity=0.8))
        dwg.add(dwg.circle(center=(light_x, light_y - 15), r=10, fill="#ffeb3b", opacity=0.3))
    
    # Title
    dwg.add(dwg.text("CRICKET STADIUM", insert=(width//2, 35), 
                     text_anchor="middle", font_size="24px", font_family="monospace",
                     fill="#ffffff", style="font-weight: bold; letter-spacing: 3px;"))
    
    box_size = 12
    gap = 3
    start_x = 60
    start_y = 70
    
    max_count = max([day['count'] for day in contributions]) if contributions else 1
    
    # Draw cricket pitch boundary circle
    pitch_center_x = start_x + (cols * (box_size + gap)) // 2
    pitch_center_y = start_y + (rows * (box_size + gap)) // 2
    dwg.add(dwg.circle(center=(pitch_center_x, pitch_center_y), r=80, 
                      fill="none", stroke="#ffffff", stroke_width=2, opacity=0.3))
    
    # Draw contribution boxes as cricket scoreboard
    for i, day in enumerate(contributions):
        msg_count = day['count']
        col = i // 7
        row = i % 7
        
        x = start_x + col * (box_size + gap)
        y = start_y + row * (box_size + gap)
        
        if msg_count == 0:
            # Duck (out for zero)
            dwg.add(dwg.rect(insert=(x, y), size=(box_size, box_size), 
                           fill="#8b4513", rx=2, opacity=0.3))
            # Add small "0"
            dwg.add(dwg.text("0", insert=(x + box_size//2, y + box_size//2 + 3), 
                           font_size="8px", fill="#ffffff", text_anchor="middle", opacity=0.5))
        else:
            intensity = msg_count / max_count
            
            # Color based on cricket scoring
            if intensity < 0.25:
                # Single run
                fill_color = "#90ee90"  # Light green
                score_type = "1"
            elif intensity < 0.5:
                # Two runs
                fill_color = "#7fbf7f"  # Medium green
                score_type = "2"
            elif intensity < 0.75:
                # Four (boundary)
                fill_color = "#ffd700"  # Gold
                score_type = "4"
            else:
                # Six (over boundary)
                fill_color = "#ff6b35"  # Orange-red
                score_type = "6"
            
            # Draw the run box
            dwg.add(dwg.rect(insert=(x, y), size=(box_size, box_size), 
                           fill=fill_color, rx=2, opacity=0.8))
            
            # Add score number
            dwg.add(dwg.text(score_type, insert=(x + box_size//2, y + box_size//2 + 3), 
                           font_size="8px", fill="#000000", text_anchor="middle", 
                           font_weight="bold", opacity=0.7))
            
            # Glow effect for sixes
            if intensity >= 0.75:
                dwg.add(dwg.rect(insert=(x-1, y-1), size=(box_size+2, box_size+2), 
                               fill="none", stroke="#ff6b35", stroke_width=1, 
                               rx=3, opacity=0.6))
    
    # Draw cricket bat and ball
    bat_x = width - 90
    bat_y = height - 80
    
    # Cricket bat
    # Handle
    dwg.add(dwg.rect(insert=(bat_x, bat_y - 40), size=(6, 40), 
                    fill="#8b4513", rx=2))
    # Blade
    dwg.add(dwg.rect(insert=(bat_x - 8, bat_y), size=(22, 50), 
                    fill="#d2691e", rx=3))
    # Grip details
    for i in range(5):
        grip_y = bat_y - 35 + i * 7
        dwg.add(dwg.line(start=(bat_x, grip_y), end=(bat_x + 6, grip_y), 
                        stroke="#000000", stroke_width=1))
    
    # Cricket ball (red)
    ball_x = bat_x + 40
    ball_y = bat_y + 20
    dwg.add(dwg.circle(center=(ball_x, ball_y), r=8, fill="#cc0000"))
    # Seam
    dwg.add(dwg.path(
        d=f"M {ball_x - 3} {ball_y - 8} Q {ball_x} {ball_y - 6} {ball_x + 3} {ball_y - 8}",
        fill="none", stroke="#ffffff", stroke_width=1.5
    ))
    dwg.add(dwg.path(
        d=f"M {ball_x - 3} {ball_y + 8} Q {ball_x} {ball_y + 6} {ball_x + 3} {ball_y + 8}",
        fill="none", stroke="#ffffff", stroke_width=1.5
    ))
    
    # Wickets (stumps)
    wicket_x = 30
    wicket_y = height - 70
    stump_width = 3
    stump_height = 35
    stump_gap = 6
    
    # Three stumps
    for i in range(3):
        stump_x = wicket_x + i * stump_gap
        dwg.add(dwg.rect(insert=(stump_x, wicket_y), size=(stump_width, stump_height), 
                        fill="#f5deb3"))
    
    # Bails on top
    dwg.add(dwg.rect(insert=(wicket_x - 2, wicket_y - 3), 
                    size=(stump_gap * 2 + stump_width + 4, 3), 
                    fill="#8b4513", rx=1))
    
    # Scoreboard
    scoreboard_x = 20
    scoreboard_y = height - 30
    total_commits = sum([day['count'] for day in contributions])
    
    # Scoreboard background
    dwg.add(dwg.rect(insert=(scoreboard_x, scoreboard_y), size=(180, 25), 
                    fill="#000000", rx=5, opacity=0.7))
    
    # Score text
    dwg.add(dwg.text(f"RUNS: {total_commits}", insert=(scoreboard_x + 10, scoreboard_y + 17), 
                     font_size="14px", font_family="monospace",
                     fill="#00ff00", style="font-weight: bold;"))
    
    # Boundary rope (decorative)
    rope_points = []
    num_points = 20
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi
        rope_x = pitch_center_x + 100 * math.cos(angle)
        rope_y = pitch_center_y + 60 * math.sin(angle)
        rope_points.append((rope_x, rope_y))
    
    for i in range(len(rope_points)):
        p1 = rope_points[i]
        p2 = rope_points[(i + 1) % len(rope_points)]
        dwg.add(dwg.line(start=p1, end=p2, stroke="#ffffff", 
                        stroke_width=2, stroke_dasharray="5,5", opacity=0.4))
    
    # Add cricket field markings (pitch)
    pitch_width = 8
    pitch_length = 60
    pitch_x = pitch_center_x - pitch_width // 2
    pitch_y = pitch_center_y - pitch_length // 2
    
    dwg.add(dwg.rect(insert=(pitch_x, pitch_y), size=(pitch_width, pitch_length), 
                    fill="#c19a6b", opacity=0.5))
    
    # Crease lines
    dwg.add(dwg.line(start=(pitch_x - 10, pitch_y), end=(pitch_x + pitch_width + 10, pitch_y), 
                    stroke="#ffffff", stroke_width=2, opacity=0.6))
    dwg.add(dwg.line(start=(pitch_x - 10, pitch_y + pitch_length), 
                    end=(pitch_x + pitch_width + 10, pitch_y + pitch_length), 
                    stroke="#ffffff", stroke_width=2, opacity=0.6))
    
    return dwg.tostring()










