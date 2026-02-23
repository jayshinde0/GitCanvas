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
    
    # Add CSS animations if enabled
    if animations_enabled:
        dwg.defs.add(dwg.style(CSS_ANIMATIONS))
        # Add counting script for number animation
        dwg.defs.add(dwg.script(content=COUNTING_SCRIPT))
    
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
    
    if animations_enabled:
        bg_rect = dwg.rect(**bg_params)
        bg_rect["class"] = "anim-border-pulse"
        dwg.add(bg_rect)
    else:
        dwg.add(dwg.rect(**bg_params))
    
    # Title with animation
    font_family = theme["font_family"]
    title_params = {
        "insert": (20, 35),
        "fill": theme["title_color"],
        "font_size": theme["title_font_size"],
        "font_family": font_family,
        "font_weight": "bold"
    }
    
    if animations_enabled:
        title_elem = dwg.text(f"{data['username']}'s Stats", **title_params)
        title_elem["class"] = "anim-slide-down"
        dwg.add(title_elem)
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
                icon = dwg.circle(**icon_params)
                icon["class"] = "anim-pulse"
                icon["style"] = f"animation-delay: {idx * 0.1}s"
                dwg.add(icon)
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
                label_elem = dwg.text(f"{label}:", **label_params)
                label_elem["class"] = "anim-fade-in"
                label_elem["style"] = f"animation-delay: {0.1 + idx * 0.15}s; animation-fill-mode: both;"
                dwg.add(label_elem)
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
                value_elem = dwg.text(f"{display_value}", **value_params)
                value_elem["class"] = "anim-slide-up stat-counter"
                value_elem["style"] = f"animation-delay: {0.2 + idx * 0.15}s; animation-fill-mode: both;"
                # Add data-target for JavaScript counter
                if numeric_value > 0:
                    value_elem["data-target"] = str(numeric_value)
                dwg.add(value_elem)
            else:
                dwg.add(dwg.text(f"{display_value}", **value_params))
                             
            current_y += item_height
            
    return dwg.tostring()
