import streamlit as st  # type: ignore
import base64
import os
import streamlit.components.v1 as components
from dotenv import load_dotenv
from roast_widget_streamlit import render_roast_widget
from generators import stats_card, lang_card, contrib_card, badge_generator, recent_activity_card, streak_card, repo_card, social_card
from utils import github_api
from themes.styles import THEMES, get_all_themes, CUSTOM_THEMES
from generators.visual_elements import (
    emoji_element,
    gif_element,
    sticker_element
)

# Initialize canvas in session state
if "canvas" not in st.session_state:
    st.session_state["canvas"] = []

for item in st.session_state["canvas"]:
    components.html(item, height=150)

# Load environment variables
load_dotenv()

st.set_page_config(page_title="GitCanvas Builder", page_icon="🛠️", layout="wide")

# Custom CSS for bigger code boxes and cleaner UI
st.markdown("""
<style>
    /* Make the code block width full and text bigger */
    code {
        font-size: 1.1rem !important;
        font-family: 'Courier New', monospace !important;
        white-space: pre-wrap !important; /* Allow wrapping so it doesn't hide */
    }
    .stTextArea textarea {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: monospace;
    }
    /* Style for tool icons grid */
    .icon-btn {
        border: 1px solid #333;
        border-radius: 8px;
        padding: 5px;
        text-align: center;
        background: #111;
        cursor: pointer;
    }
    .icon-btn:hover {
        background: #222;
        border-color: #555;
    }
</style>
""", unsafe_allow_html=True)

st.title("GitCanvas: Profile Architect 🛠️")
st.markdown("### Design your GitHub Stats. Copy the Code. Done.")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("1. Identify")
    username = st.text_input("GitHub Username", value="torvalds")
    
    st.header("2. Global Style")
    
    # Get all themes including custom ones
    all_themes = get_all_themes()
    
    # Separate predefined and custom themes for better organization
    predefined_themes = [k for k in all_themes.keys() if k not in CUSTOM_THEMES]
    custom_theme_names = list(CUSTOM_THEMES.keys())
    
    # Combine with custom themes at the end
    theme_options = predefined_themes + custom_theme_names
    
    selected_theme = st.selectbox("Select Theme", theme_options)
    
    # Customization Expander
    # Ensure custom_colors exists even if the expander isn't opened
    custom_colors = {}
    with st.expander("Customize Colors", expanded=False):
        st.caption("Override theme defaults")
        default_theme = all_themes.get(selected_theme, all_themes["Default"]).copy() # Copy to avoid mutating global
        
        # Helper to get color safely
        def get_col(key): return default_theme.get(key, "#000000")
        
        # Use theme-specific keys so each theme maintains its own customization
        custom_bg = st.color_picker("Background", value=get_col("bg_color"), key=f"customize_bg_{selected_theme}")
        custom_title = st.color_picker("Title Text", value=get_col("title_color"), key=f"customize_title_{selected_theme}")
        custom_text = st.color_picker("Body Text", value=get_col("text_color"), key=f"customize_text_{selected_theme}")
        custom_border = st.color_picker("Border", value=get_col("border_color"), key=f"customize_border_{selected_theme}")
        
        # Build custom colors dict if changed
        custom_colors = {}
        if custom_bg != get_col("bg_color"): custom_colors["bg_color"] = custom_bg
        if custom_title != get_col("title_color"): custom_colors["title_color"] = custom_title
        if custom_text != get_col("text_color"): custom_colors["text_color"] = custom_text
        if custom_border != get_col("border_color"): custom_colors["border_color"] = custom_border

    # Custom Theme Creator Section
    with st.expander("🎨 Custom Theme Creator", expanded=False):
        st.caption("Create and save your own custom theme")
        
        # Initialize session state for custom theme colors if not exists
        if "custom_theme_colors" not in st.session_state:
            st.session_state.custom_theme_colors = {
                "bg_color": "#0d1117",
                "border_color": "#30363d",
                "title_color": "#58a6ff",
                "text_color": "#c9d1d9",
                "icon_color": "#58a6ff",
            }
        
        theme_name = st.text_input("Theme Name", placeholder="My Awesome Theme", key="new_theme_name")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.custom_theme_colors["bg_color"] = st.color_picker("Background", st.session_state.custom_theme_colors["bg_color"], key="creator_bg")
            st.session_state.custom_theme_colors["border_color"] = st.color_picker("Border", st.session_state.custom_theme_colors["border_color"], key="creator_border")
        with col2:
            st.session_state.custom_theme_colors["title_color"] = st.color_picker("Title", st.session_state.custom_theme_colors["title_color"], key="creator_title")
            st.session_state.custom_theme_colors["text_color"] = st.color_picker("Text", st.session_state.custom_theme_colors["text_color"], key="creator_text")
        
        if st.button("💾 Save Theme", use_container_width=True):
            if theme_name:
                from themes.styles import save_custom_theme
                filename = save_custom_theme(theme_name, st.session_state.custom_theme_colors)
                st.success(f"Theme '{theme_name}' saved! Refresh to see it in the theme list.")
            else:
                st.error("Please enter a theme name")

    github_token = st.text_input("GitHub Token (enter your token to view actual data)", type="password", help="Enter your GitHub token to fetch contribution data")
    
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    st.info("💡 Tip: Use the 'Badges' tab to add your tech stack icons!")

# Data Loading
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(user, token=None, _cache_version="v2"):  # Added version to force cache invalidation
    d = github_api.get_live_github_data(user, token)
    if not d:
        st.warning("Using mock data (API limits).")
        d = github_api.get_mock_data(user)
    return d

data = load_data(username if username else "torvalds", github_token if github_token else None)

# Ensure backward compatibility with old cached data
if "top_repos" not in data:
    data["top_repos"] = []

# Apply custom colors to current theme for python logic
current_theme_opts = all_themes.get(selected_theme, all_themes["Default"]).copy()
if custom_colors:
    current_theme_opts.update(custom_colors)

# --- Layout: Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(["Main Stats", "Languages", "Top Repositories", "Contributions", "🔥 GitHub Streak", "🔗 Social Links", "Icons & Badges", "🔥 AI Roast", "Recent Activity", "✨ Visual Elements"])

def show_code_area(code_content, label="Markdown Code"):
    st.markdown(f"**{label}** (Copy below)")
    st.text_area(label, value=code_content, height=100, label_visibility="collapsed")

def render_tab(svg_bytes, endpoint, username, selected_theme, custom_colors, hide_params=None, code_template=None, excluded_languages=None):
    col1, col2 = st.columns([1.5, 1])
    with col1:
        # Render SVG
        b64 = base64.b64encode(svg_bytes.encode('utf-8')).decode("utf-8")
        st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" style="max-width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-radius: 10px;"/>', unsafe_allow_html=True)

        st.download_button(
            label="Download SVG",
            data=svg_bytes.encode("utf-8"),
            file_name=f"{endpoint}_{username}.svg",
            mime="image/svg+xml",
            use_container_width=True
        )

        png_bytes = None
        try:
            import cairosvg  # Local import to avoid startup crash if cairo libs are missing.
            png_bytes = cairosvg.svg2png(bytestring=svg_bytes.encode("utf-8"))
        except Exception:
            png_bytes = None

        if png_bytes:
            # Download PNG button
            st.download_button(
                label="Download PNG",
                data=png_bytes,
                file_name=f"{endpoint}_{username}.png",
                mime="image/png",
                use_container_width=True
            )

    with col2:
        st.subheader("Integration")
        # Construct URL
        params = []
        if hide_params:
            for key, value in hide_params.items():
                if not value:
                    params.append(f"hide_{key}=true")

        if selected_theme != "Default":
            params.append(f"theme={selected_theme}")
        for k, v in custom_colors.items():
            params.append(f"{k}={v.replace('#', '')}")
        
        # Add exclude parameter for languages endpoint
        if excluded_languages and endpoint == "languages":
            # Remove spaces and add to params
            params.append(f"exclude={excluded_languages.replace(' ', '')}")

        query_str = "&".join(params)
        if query_str:
            query_str = "?" + query_str

        url = f"https://gitcanvas-api.vercel.app/api/{endpoint}{query_str}&username={username}"
        if code_template:
            code = code_template.format(url=url, username=username)
        else:
            code = f"![{endpoint.title()}]({url})"

        show_code_area(code)

with tab1:
    st.subheader("Stats Card")
    # Options
    c1, c2, c3, c4 = st.columns(4)
    show_stars = c1.checkbox("Stars", True)
    show_commits = c2.checkbox("Commits", True)
    show_repos = c3.checkbox("Repos", True)
    show_followers = c4.checkbox("Followers", True)

    show_ops = {"stars": show_stars, "commits": show_commits, "repos": show_repos, "followers": show_followers}

    # Pass selected_theme string to support theme-specific logic (e.g. Glass)
    svg_bytes = stats_card.draw_stats_card(data, selected_theme, show_ops, custom_colors)
    render_tab(svg_bytes, "stats", username, selected_theme, custom_colors, hide_params=show_ops, code_template=f"[![{username}'s Stats]({{url}})](https://github.com/{{username}})")

with tab2:
    st.subheader("Top Languages")
    
    # Get available languages from data
    available_languages = [lang for lang, _ in data.get("top_languages", [])]
    
    # Use st.pills() for better UX - click to toggle, no dropdown to close
    excluded_languages = st.pills(
        "Languages to Exclude:",
        options=available_languages,
        default=[],
        selection_mode="multi",
        help="Click to toggle languages you want to hide from your stats"
    )
    
    # Convert list to comma-separated string for URL generation
    excluded_languages_str = ",".join(excluded_languages) if excluded_languages else None
    
    # Generate card with exclusions - Pass selected_theme string
    svg_bytes = lang_card.draw_lang_card(data, selected_theme, custom_colors, excluded_languages=excluded_languages)
    render_tab(svg_bytes, "languages", username, selected_theme, custom_colors, code_template="![Top Langs]({url})", excluded_languages=excluded_languages_str)

with tab3:
    st.subheader("Top Repositories")
    
    # Sorting options
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        sort_by = st.selectbox("Sort by:", ["stars", "forks", "updated"], index=0, 
                              format_func=lambda x: {"stars": "⭐ Most Starred", "forks": "🔱 Most Forked", "updated": "🕐 Recently Updated"}[x])
    with col2:
        repo_limit = st.slider("Number of repos:", min_value=3, max_value=10, value=5)
    with col3:
        exclude_forks = st.checkbox("Exclude forks", value=False, help="Hide forked repositories")
    
    # Filter data based on user preference
    filtered_data = data.copy()
    if exclude_forks and "top_repos" in filtered_data:
        filtered_data["top_repos"] = [r for r in filtered_data["top_repos"] if not r.get("is_fork", False)]
    
    # Generate card - Pass selected_theme string
    svg_bytes = repo_card.draw_repo_card(filtered_data, selected_theme, custom_colors, sort_by=sort_by, limit=repo_limit)
    render_tab(svg_bytes, "repos", username, selected_theme, custom_colors, code_template="![Top Repos]({url})")

with tab4:
    st.subheader("Contribution Graph")
    st.caption(f"Theme: **{selected_theme}**")
    if selected_theme == "Gaming": st.caption("🐍 Snake Mode: The snake grows as it eats commits.")
    elif selected_theme == "Space": st.caption("🚀 Space Mode: Spaceship traversing the contribution galaxy.")
    elif selected_theme == "Marvel": st.caption("💎 Infinity Mode: Collecting Stones based on activity.")
    elif selected_theme == "Ocean": st.caption("🌊 Ocean Mode: Fish and bubbles swim through underwater contributions.")
    elif selected_theme == "Glass": st.caption("💎 GlassMorphism: Translucent Glass based theme card.")

    # Pass selected_theme string
    svg_bytes = contrib_card.draw_contrib_card(data, selected_theme, custom_colors)
    render_tab(svg_bytes, "contributions", username, selected_theme, custom_colors, code_template="![Contributions]({url})")

with tab5:
    st.subheader("GitHub Streak")
    st.caption("🔥 Track your contribution streaks! Shows current consecutive days and your all-time longest streak.")
    
    svg_bytes = streak_card.draw_streak_card(data, selected_theme, custom_colors)
    render_tab(svg_bytes, "streak", username, selected_theme, custom_colors, code_template="![GitHub Streak]({url})")

with tab6:
    st.subheader("🔗 Social Links")
    st.markdown("Add badges for your social media profiles and connect with your audience!")
    
    # Social platform selection
    st.markdown("#### Select Platforms")
    available_platforms = list(social_card.SOCIAL_PLATFORMS.keys())
    selected_platforms = st.multiselect(
        "Choose platforms to display:",
        available_platforms,
        default=["twitter", "linkedin"],
        format_func=lambda x: social_card.SOCIAL_PLATFORMS[x]["name"]
    )
    
    # Input fields for each selected platform
    social_data = {}
    if selected_platforms:
        st.markdown("#### Enter Your Handles/URLs")
        cols = st.columns(2)
        for idx, platform in enumerate(selected_platforms):
            with cols[idx % 2]:
                placeholder = social_card.SOCIAL_PLATFORMS[platform]["placeholder"]
                social_data[platform] = st.text_input(
                    social_card.SOCIAL_PLATFORMS[platform]["name"],
                    placeholder=placeholder,
                    key=f"social_{platform}"
                )
    
    # Generate preview and code
    if selected_platforms and any(social_data.values()):
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown("#### Preview")
            try:
                svg_bytes = social_card.draw_social_card(
                    social_data,
                    selected_theme,
                    custom_colors,
                    selected_platforms
                )
                b64 = base64.b64encode(svg_bytes.encode('utf-8')).decode("utf-8")
                st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" style="max-width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-radius: 10px;"/>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error rendering social card: {e}")
        
        with col2:
            st.markdown("#### Markdown Code")
            # Generate individual badge code
            badge_code = ""
            for platform in selected_platforms:
                if social_data.get(platform):
                    platform_config = social_card.SOCIAL_PLATFORMS[platform]
                    badge_url = social_card.generate_social_badge_url(
                        platform,
                        social_data[platform],
                        platform_config["color"],
                        platform_config["logo"]
                    )
                    badge_code += f"[![{platform_config['name']}]({badge_url})](https://your-profile-url)\n"
            
            st.text_area("Copy the code below:", value=badge_code, height=200, label_visibility="collapsed")
    else:
        st.info("👆 Select platforms and enter your handles to generate social badges")

with tab7:
    st.subheader("Tech Stack Badges")
    st.markdown("Click detailed settings to customize. Copy the code block to your README.")
    
    col_tools, col_preview = st.columns([2, 1.5])
    
    with col_tools:
        # Badge Settings
        badge_style = st.selectbox("Badge Style", ["for-the-badge", "flat", "flat-square", "plastic", "social"], index=0)
        
        # Categories
        for category, tools in badge_generator.TECH_STACK.items():
            st.markdown(f"**{category}**")
            
            # Better UI: Multi-selects per category
            selected = st.multiselect(f"Select {category}", list(tools.keys()), key=f"sel_{category}")
            if selected:
                if "badges" not in st.session_state: st.session_state.badges = []
                pass

    with col_preview:
        st.subheader("Stack Preview")
        
        # Gather all selected
        all_selected_badges = []
        for category, tools in badge_generator.TECH_STACK.items():
            # We access the key we generated above
            val = st.session_state.get(f"sel_{category}", [])
            for item in val:
                conf = tools[item]
                all_selected_badges.append((item, conf))
        
        if not all_selected_badges:
            st.info("Select tools from the left to generate badges.")
        else:
            # Render Preview
            md_output = ""
            should_match = st.checkbox("Match Theme Color", value=False, key="match_theme_global")
            for name, conf in all_selected_badges:
                final_color = conf['color']
                if should_match:
                    final_color = current_theme_opts['title_color'].replace("#", "")
                
                url = badge_generator.generate_badge_url(name, final_color, conf['logo'], style=badge_style)
                st.markdown(f"![{name}]({url})")
                md_output += f"![{name}]({url}) "
            
            st.markdown("---")
            show_code_area(md_output, label="Badge Code")

# AI ROAST TAB
with tab8:
    st.subheader("🔥 AI Profile Roast")

    st.markdown("Let AI roast your GitHub profile with humor!")
    
    if username:
        render_roast_widget(username)
    else:
        st.warning("Please enter a GitHub username in the sidebar.")

with tab9:
    st.subheader("Recent Activity")
    st.markdown("Shows your last 3 PR or Issue events from GitHub.")

    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.caption("Theme: **{}**".format(selected_theme))
        try:
            # Pass selected_theme string
            svg_bytes = recent_activity_card.draw_recent_activity_card({'username': username}, selected_theme, custom_colors, token=github_token)
        except Exception as e:
            st.error(f"Error rendering recent activity: {e}")
            svg_bytes = recent_activity_card._render_svg_lines([f"Error: {e}"], THEMES.get(selected_theme, THEMES['Default']))

        b64 = base64.b64encode(svg_bytes.encode('utf-8')).decode("utf-8")
        st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" style="max-width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-radius: 10px;"/>', unsafe_allow_html=True)

    with col2:
        st.subheader("Integration")
        params = []
        if selected_theme != "Default": params.append(f"theme={selected_theme}")
        for k, v in custom_colors.items():
            params.append(f"{k}={v.replace('#', '')}")
        if github_token:
            params.append(f"token={github_token}")

        query_str = "&".join(params)
        if query_str: query_str = "?" + query_str

        url = f"https://gitcanvas-api.vercel.app/api/recent{query_str}&username={username}"
        code = f"![Recent Activity]({url})"
        show_code_area(code)

with tab10:
    st.subheader("✨ Visual Elements")
    st.markdown("Add emojis, GIFs, or stickers to your canvas")

    element_type = st.selectbox(
        "Choose element type",
        ["Emoji", "GIF", "Sticker"]
    )

    value = st.text_input(
        "Enter value",
        placeholder="🔥 or https://gif-url"
    )

    if st.button("Add to Canvas"):
        if element_type == "Emoji":
            svg = emoji_element(value)
        elif element_type == "GIF":
            svg = gif_element(value)
        else:
            svg = sticker_element(value)

        st.session_state["canvas"].append(svg)
