
import json
import os

THEMES = {}
CUSTOM_THEMES = {}  # Store custom themes separately

themes_dir = os.path.join(os.path.dirname(__file__), 'json')

def load_predefined_themes():
    """Load predefined themes from JSON files"""
    if os.path.exists(themes_dir):
        for filename in os.listdir(themes_dir):
            if filename.endswith('.json') and not filename.startswith('custom_'):
                theme_name = filename[:-5].capitalize()  # Remove .json and capitalize
                with open(os.path.join(themes_dir, filename), 'r') as f:
                    THEMES[theme_name] = json.load(f)

def load_custom_themes():
    """Load custom themes from custom_*.json files"""
    custom_themes = {}
    if os.path.exists(themes_dir):
        for filename in os.listdir(themes_dir):
            if filename.startswith('custom_') and filename.endswith('.json'):
                # Extract theme name from custom_{name}.json
                theme_name = filename[7:-5].capitalize()  # Remove 'custom_' and '.json'
                with open(os.path.join(themes_dir, filename), 'r') as f:
                    custom_themes[theme_name] = json.load(f)
    return custom_themes

def save_custom_theme(theme_name, theme_data):
    """Save a custom theme to a JSON file"""
    # Sanitize theme name for filename
    safe_name = theme_name.lower().replace(' ', '_').replace('-', '_')
    filename = f"custom_{safe_name}.json"
    filepath = os.path.join(themes_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(theme_data, f, indent=4)
    
    return filename

def get_all_themes():
    """Get all themes including custom ones"""
    all_themes = THEMES.copy()
    all_themes.update(CUSTOM_THEMES)
    return all_themes

# Load predefined themes on module import
load_predefined_themes()


# Manually add Ocean theme with ocean-themed colors
THEMES["Ocean"] = {
    "bg_color": "#001122",
    "border_color": "#004466",
    "title_color": "#00aaff",
    "text_color": "#66ddaa",
    "icon_color": "#2288cc",
    "font_family": "Segoe UI, Ubuntu, Sans-Serif",
    "title_font_size": 20,
    "text_font_size": 14
}

# Load custom themes on module import
CUSTOM_THEMES = load_custom_themes()
