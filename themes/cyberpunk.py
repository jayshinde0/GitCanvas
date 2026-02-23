import svgwrite
import random

def render(data):
    """
    Cyberpunk Theme
    Neon grid with glitch effects and holographic elements
    High activity creates intense neon glow
    """
    contributions = data['contributions'][-365:] if len(data['contributions']) > 365 else data['contributions']
    
    cols = 53
    rows = 7
    width = cols * 15 + 100
    height = rows * 15 + 120
    
    dwg = svgwrite.Drawing(size=("100%", "100%"), viewBox=f"0 0 {width} {height}")
    
    # Dark background
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="#0a0a0f"))
    
    # Grid lines for cyberpunk aesthetic
    for i in range(0, width, 20):
        dwg.add(dwg.line(start=(i, 0), end=(i, height), 
                        stroke="#1a1a2e", stroke_width=0.5, opacity=0.5))
    for i in range(0, height, 20):
        dwg.add(dwg.line(start=(0, i), end=(width, i), 
                        stroke="#1a1a2e", stroke_width=0.5, opacity=0.5))
    
    # Title with glitch effect
    dwg.add(dwg.text("CYBER_COMMITS.exe", insert=(width//2, 35), 
                     text_anchor="middle", font_size="24px", font_family="monospace",
                     fill="#00ff41", style="font-weight: bold; letter-spacing: 4px;"))
    
    # Glitch overlay for title
    dwg.add(dwg.text("CYBER_COMMITS.exe", insert=(width//2 + 2, 35), 
                     text_anchor="middle", font_size="24px", font_family="monospace",
                     fill="#ff00ff", opacity=0.3, style="font-weight: bold; letter-spacing: 4px;"))
    
    box_size = 12
    gap = 3
    start_x = 50
    start_y = 60
    
    max_count = max([day['count'] for day in contributions]) if contributions else 1
    
    for i, day in enumerate(contributions):
        msg_count = day['count']
        col = i // 7
        row = i % 7
        
        x = start_x + col * (box_size + gap)
        y = start_y + row * (box_size + gap)
        
        if msg_count == 0:
            # Low power mode
            dwg.add(dwg.rect(insert=(x, y), size=(box_size, box_size), 
                           fill="#1a1a2e", rx=1, opacity=0.5))
        else:
            intensity = msg_count / max_count
            
            # Neon colors based on intensity
            if intensity < 0.25:
                neon_color = "#00ffff"  # Cyan
                glow_color = "#0088aa"
            elif intensity < 0.5:
                neon_color = "#00ff41"  # Matrix green
                glow_color = "#00aa22"
            elif intensity < 0.75:
                neon_color = "#ff00ff"  # Magenta
                glow_color = "#aa00aa"
            else:
                neon_color = "#ff0080"  # Hot pink
                glow_color = "#aa0055"
            
            # Main block
            dwg.add(dwg.rect(insert=(x, y), size=(box_size, box_size), 
                           fill=neon_color, rx=2, opacity=0.8))
            
            # Glow effect for higher intensity
            if intensity > 0.5:
                dwg.add(dwg.rect(insert=(x-2, y-2), size=(box_size+4, box_size+4), 
                               fill="none", stroke=glow_color, stroke_width=2, 
                               rx=3, opacity=0.4))
                
            # Extra bright glow for maximum activity
            if intensity > 0.8:
                dwg.add(dwg.rect(insert=(x-3, y-3), size=(box_size+6, box_size+6), 
                               fill="none", stroke=neon_color, stroke_width=1, 
                               rx=4, opacity=0.3))
    
    # Add scanning line effect
    scan_y = start_y + (rows * (box_size + gap)) // 2
    dwg.add(dwg.line(start=(0, scan_y), end=(width, scan_y), 
                    stroke="#00ff41", stroke_width=2, opacity=0.2))
    
    # Add random glitch blocks
    random.seed(456)
    for _ in range(8):
        glitch_x = random.randint(0, width - 30)
        glitch_y = random.randint(0, height - 10)
        glitch_w = random.randint(10, 30)
        dwg.add(dwg.rect(insert=(glitch_x, glitch_y), size=(glitch_w, 2), 
                        fill="#ff00ff", opacity=0.3))
    
    # Digital display footer
    total_commits = sum([day['count'] for day in contributions])
    dwg.add(dwg.text(f">>> TOTAL_COMMITS: {total_commits} <<<", 
                     insert=(width//2, height - 15), 
                     text_anchor="middle", font_size="11px", font_family="monospace",
                     fill="#00ff41", style="font-weight: bold;"))
    
    # Corner brackets for HUD effect
    dwg.add(dwg.path(d=f"M 10 10 L 10 30 M 10 10 L 30 10", 
                    stroke="#00ffff", stroke_width=2, fill="none", opacity=0.6))
    dwg.add(dwg.path(d=f"M {width-10} 10 L {width-10} 30 M {width-10} 10 L {width-30} 10", 
                    stroke="#00ffff", stroke_width=2, fill="none", opacity=0.6))
    
    return dwg.tostring()