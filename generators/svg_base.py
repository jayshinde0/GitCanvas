import svgwrite
from themes.styles import THEMES

# CSS Animation Definitions - Reusable across all card generators
CSS_ANIMATIONS = """
    /* Fade In Animation */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Slide Up Animation */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Slide Down Animation */
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Scale In Animation */
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Pulse Animation */
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.05); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* Pulse Glow Animation (for high activity) */
    @keyframes pulseGlow {
        0% { opacity: 0.6; }
        50% { opacity: 1; filter: brightness(1.3); }
        100% { opacity: 0.6; }
    }
    
    /* Flame Flicker Animation */
    @keyframes flameFlicker {
        0% { transform: scale(1) rotate(-2deg); opacity: 0.9; }
        25% { transform: scale(1.05) rotate(1deg); opacity: 1; }
        50% { transform: scale(0.98) rotate(-1deg); opacity: 0.85; }
        75% { transform: scale(1.02) rotate(2deg); opacity: 0.95; }
        100% { transform: scale(1) rotate(-2deg); opacity: 0.9; }
    }
    
    /* Trophy Shine Animation */
    @keyframes trophyShine {
        0% { opacity: 0.3; }
        50% { opacity: 1; }
        100% { opacity: 0.3; }
    }
    
    /* Border Pulse Animation */
    @keyframes borderPulse {
        0% { stroke-opacity: 0.5; }
        50% { stroke-opacity: 1; }
        100% { stroke-opacity: 0.5; }
    }
    
    /* Progress Bar Fill Animation */
    @keyframes progressFill {
        from { width: 0; }
        to { width: var(--target-width); }
    }
    
    /* Number Count Up Animation (using CSS counter) */
    @keyframes countUp {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Twinkle Animation (for stars/space theme) */
    @keyframes twinkle {
        0% { opacity: 0.3; }
        50% { opacity: 1; }
        100% { opacity: 0.3; }
    }
    
    /* Bubble Float Animation (for ocean theme) */
    @keyframes bubbleFloat {
        0% { transform: translateY(0); opacity: 0.8; }
        50% { transform: translateY(-5px); opacity: 1; }
        100% { transform: translateY(0); opacity: 0.8; }
    }

    /* Animation Utility Classes */
    .anim-fade-in {
        animation: fadeIn 0.6s ease-out forwards;
    }
    
    .anim-slide-up {
        animation: slideUp 0.5s ease-out forwards;
    }
    
    .anim-slide-down {
        animation: slideDown 0.5s ease-out forwards;
    }
    
    .anim-scale-in {
        animation: scaleIn 0.4s ease-out forwards;
    }
    
    .anim-pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    .anim-pulse-glow {
        animation: pulseGlow 1.5s ease-in-out infinite;
    }
    
    .anim-flame {
        animation: flameFlicker 0.8s ease-in-out infinite;
        transform-origin: center bottom;
    }
    
    .anim-trophy-shine {
        animation: trophyShine 2s ease-in-out infinite;
    }
    
    .anim-border-pulse {
        animation: borderPulse 3s ease-in-out infinite;
    }
    
    .anim-twinkle {
        animation: twinkle 2s ease-in-out infinite;
    }
    
    .anim-bubble {
        animation: bubbleFloat 3s ease-in-out infinite;
    }
"""


def get_animation_style(enabled=True, custom_delay=0):
    """
    Returns CSS style block for animations.
    
    Args:
        enabled: Whether animations are enabled
        custom_delay: Additional delay in seconds
    
    Returns:
        SVG style element or None if animations disabled
    """
    if not enabled:
        return None
    
    return CSS_ANIMATIONS


def create_svg_base(theme_name, custom_colors, width, height, title_text, animations_enabled=True):
    """
    Creates the base SVG drawing with theme setup, background, and title.
    Returns the drawing object and the theme dictionary.
    
    Args:
        theme_name: Name of the theme to use
        custom_colors: Dict of custom color overrides
        width: SVG width
        height: SVG height
        title_text: Title text to display
        animations_enabled: Whether to include CSS animations
    """
    theme = THEMES.get(theme_name, THEMES["Default"]).copy()
    if custom_colors:
        theme.update(custom_colors)
    
    dwg = svgwrite.Drawing(size=(f"{width}px", f"{height}px"))
    
    # Note: CSS animations disabled due to svgwrite validation constraints
    
    # Background with optional border pulse animation
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
        dwg.add(dwg.rect(**bg_params))
    else:
        dwg.add(dwg.rect(**bg_params))
    
    # Title with animation
    title_params = {
        "insert": (20, 30),
        "fill": theme["title_color"],
        "font_size": theme["title_font_size"],
        "font_family": theme["font_family"],
        "font_weight": "bold"
    }
    
    if animations_enabled:
        dwg.add(dwg.text(title_text, **title_params))
    else:
        dwg.add(dwg.text(title_text, **title_params))
    
    return dwg, theme
