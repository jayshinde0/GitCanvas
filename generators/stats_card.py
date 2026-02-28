import math
import random
import svgwrite
from themes.styles import THEMES
from .svg_base import create_svg_base, CSS_ANIMATIONS

# JavaScript for number counting animation
COUNTING_SCRIPT = """
<script type="text/javascript">
<![CDATA[
    function animateCounters() {
        var counters = document.querySelectorAll('.stat-counter');
        counters.forEach(function(counter, index) {
            var target = parseInt(counter.getAttribute('data-target'));
            var duration = 1500;
            var start = performance.now();
            var startVal = 0;
            
            function updateCounter(currentTime) {
                var elapsed = currentTime - start;
                var progress = Math.min(elapsed / duration, 1);
                var easeOut = 1 - Math.pow(1 - progress, 3);
                var current = Math.floor(startVal + (target - startVal) * easeOut);
                
                counter.textContent = current.toLocaleString();
                
                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target.toLocaleString();
                }
            }
            
            setTimeout(function() {
                requestAnimationFrame(updateCounter);
            }, index * 200);
        });
    }
    
    document.addEventListener('DOMContentLoaded', animateCounters);
]]>
</script>
"""

def draw_stats_card(data, theme_name="Default", show_options=None, custom_colors=None, animations_enabled=True):
    """
    Generates the Main Stats Card SVG.
    data: dict with user stats
    theme_name: string key from THEMES
    show_options: dict with toggles (e.g. {'stars': True, 'prs': False})
    animations_enabled: bool to enable/disable CSS animations
    """
    if show_options is None:
        show_options = {"stars": True, "commits": True, "repos": True, "followers": True}

    # FIXED: Handle both string theme name and pre-resolved theme dict
    if isinstance(theme_name, dict):
        # Already a theme dictionary (e.g., current_theme_opts from app.py)
        theme = theme_name.copy()
    else:
        # Convert theme_name string to actual theme dictionary
        theme = THEMES.get(theme_name, THEMES["Default"]).copy()
        
        # Apply custom colors if provided
        if custom_colors:
            theme.update(custom_colors)

    width = 450
    # Calculate height dynamically based on visible items
    base_height = 50
    item_height = 25
    visible_items = sum(1 for k, v in show_options.items() if v)
    height = base_height + (visible_items * item_height) + 10
    
    dwg = svgwrite.Drawing(size=("100%", "100%"), viewBox=f"0 0 {width} {height}")
    
    # Add CSS animations if enabled (basic support only)
    # Note: Advanced animation features disabled due to svgwrite validation constraints
    
    # Background (with optional border pulse)
    bg_params = {
        "insert": (0, 0), 
        "size": ("100%", "100%"), 
        "rx": 10, 
        "ry": 10, 
        "fill": theme["bg_color"], 
        "stroke": theme["border_color"], 
        "stroke_width": 2
    }
    
    # Background (no animation)
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
    elif theme_name == "Cyberpunk":
        # Grid overlay
        for i in range(0, width, 30):
            dwg.add(dwg.line(start=(i, 0), end=(i, height), 
                           stroke="#1a1a2e", stroke_width=0.3, opacity=0.4))
        for i in range(0, height, 30):
            dwg.add(dwg.line(start=(0, i), end=(width, i), 
                           stroke="#1a1a2e", stroke_width=0.3, opacity=0.4))
        
        # Scan line effect
        scan_y = height / 2
        dwg.add(dwg.line(start=(0, scan_y), end=(width, scan_y), 
                        stroke="#00ff41", stroke_width=2, opacity=0.15))
        
        # Glitch rectangles
        random.seed(456)
        for _ in range(4):
            gx = random.randint(0, width - 40)
            gy = random.randint(0, height - 10)
            gw = random.randint(15, 40)
            dwg.add(dwg.rect(insert=(gx, gy), size=(gw, 2), 
                           fill="#ff00ff", opacity=0.25))
        
        # Corner brackets (HUD style)
        bracket_size = 15
        dwg.add(dwg.path(d=f"M 10 10 L 10 {10+bracket_size} M 10 10 L {10+bracket_size} 10", 
                        stroke="#00ffff", stroke_width=2, fill="none", opacity=0.5))
        dwg.add(dwg.path(d=f"M {width-10} 10 L {width-10} {10+bracket_size} M {width-10} 10 L {width-10-bracket_size} 10", 
                        stroke="#00ffff", stroke_width=2, fill="none", opacity=0.5))

    # Title
    font_family = theme["font_family"]
    title_params = {
        "insert": (20, 35),
        "fill": theme["title_color"],
        "font_size": theme["title_font_size"],
        "font_family": font_family,
        "font_weight": "bold"
    }
    
    if animations_enabled:
        dwg.add(dwg.text(f"{data['username']}'s Stats", **title_params))
    else:
        dwg.add(dwg.text(f"{data['username']}'s Stats", **title_params))
    
    # Stats with animations
    start_y = 65
    current_y = start_y
    text_color = theme["text_color"]
    font_size = theme["text_font_size"]
    
    # Logic to handle N/A display for commits
    commit_val = data.get('total_commits', 0)
    display_commits = str(commit_val) if commit_val > 0 else "N/A"

    stats_map = [
        ("stars", "Total Stars", f"{data.get('total_stars', 0)}", data.get('total_stars', 0)),
        ("commits", "Total Commits (Year)", display_commits, commit_val if commit_val > 0 else 0),
        ("repos", "Public Repos", f"{data.get('public_repos', 0)}", data.get('public_repos', 0)),
        ("followers", "Followers", f"{data.get('followers', 0)}", data.get('followers', 0))
    ]
    
    for idx, (key, label, display_value, numeric_value) in enumerate(stats_map):
        if show_options.get(key, True):
            # Icon (with optional pulse animation)
            icon_params = {
                "center": (30, current_y - 5),
                "r": 4,
                "fill": theme["icon_color"]
            }
            
            if animations_enabled:
                dwg.add(dwg.circle(**icon_params))
            else:
                dwg.add(dwg.circle(**icon_params))
            
            # Label with fade-in animation
            label_params = {
                "insert": (45, current_y),
                "fill": text_color,
                "font_size": font_size,
                "font_family": font_family
            }
            
            if animations_enabled:
                dwg.add(dwg.text(f"{label}:", **label_params))
            else:
                dwg.add(dwg.text(f"{label}:", **label_params))
            
            # Value with slide-up animation and counting effect
            value_params = {
                "insert": (width - 40, current_y),
                "fill": text_color,
                "font_size": font_size,
                "font_family": font_family,
                "text_anchor": "end",
                "font_weight": "bold"
            }
            
            if animations_enabled:
                dwg.add(dwg.text(f"{display_value}", **value_params))
            else:
                dwg.add(dwg.text(f"{display_value}", **value_params))
                             
            current_y += item_height
            
    return dwg.tostring()
