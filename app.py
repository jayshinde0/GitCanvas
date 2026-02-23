import streamlit as st  # type: ignore
import base64
import os
import streamlit.components.v1 as components
from dotenv import load_dotenv
from roast_widget_streamlit import render_roast_widget
from generators import stats_card, lang_card, contrib_card, badge_generator, recent_activity_card, streak_card, repo_card, trophy_card
from utils import github_api
from themes.styles import THEMES, CUSTOM_THEMES, save_custom_theme, load_custom_themes, get_all_themes


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
    
    # Animation Toggle
    animations_enabled = st.checkbox("✨ Enable Animations", value=True, help="Toggle CSS animations on SVG cards")
    
    # Customization Expander
    # Ensure custom_colors exists even if the expander isn't opened
    custom_colors = {}
    with st.expander("Customize Colors", expanded=False):
        st.caption("Override theme defaults")
        default_theme = all_themes.get(selected_theme, all_themes["Default"]).copy() # Copy to avoid mutating global
        
        # Helper to get color safely
        def get_col(key): return default_theme.get(key, "#000000")
        
        custom_bg = st.color_picker("Background", value=get_col("bg_color"))
        custom_title = st.color_picker("Title Text", value=get_col("title_color"))
        custom_text = st.color_picker("Body Text", value=get_col("text_color"))
        custom_border = st.color_picker("Border", value=get_col("border_color"))
        
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
                "icon_color": "#8b949e"
            }
        col1, col2 = st.columns(2)
        with col1:
            new_bg = st.color_picker("Background", value=st.session_state.custom_theme_colors["bg_color"], key="new_bg")
            new_title = st.color_picker("Title Color", value=st.session_state.custom_theme_colors["title_color"], key="new_title")
            new_icon = st.color_picker("Icon Color", value=st.session_state.custom_theme_colors["icon_color"], key="new_icon")
        with col2:
            new_border = st.color_picker("Border Color", value=st.session_state.custom_theme_colors["border_color"], key="new_border")
            new_text = st.color_picker("Text Color", value=st.session_state.custom_theme_colors["text_color"], key="new_text")
        
        # Update session state
        st.session_state.custom_theme_colors = {
            "bg_color": new_bg,
            "border_color": new_border,
            "title_color": new_title,
            "text_color": new_text,
            "icon_color": new_icon,
            "font_family": "Segoe UI, Ubuntu, Sans-Serif",
            "title_font_size": 20,
            "text_font_size": 14
        }
        
        # Theme name input
        custom_theme_name = st.text_input("Theme Name", placeholder="e.g., My Awesome Theme", key="custom_theme_name")
        
        # Save button
        if st.button("💾 Save Theme", use_container_width=True, key="save_theme_btn"):
            if custom_theme_name.strip():
                try:
                    filename = save_custom_theme(custom_theme_name, st.session_state.custom_theme_colors)
                    st.success(f"Theme '{custom_theme_name}' saved successfully!")
                    
                    # Reload custom themes
                    from themes.styles import CUSTOM_THEMES as ct
                    ct.clear()
                    ct.update(load_custom_themes())
                    
                    # Force rerun to update theme dropdown
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving theme: {str(e)}")
            else:
                st.warning("Please enter a theme name.")
        
        # Show saved custom themes
        if custom_theme_names:
            st.markdown("**Your Custom Themes:**")
            for theme_name in custom_theme_names:
                col_theme, col_del = st.columns([3, 1])
                with col_theme:
                    st.markdown(f"• {theme_name}")
                with col_del:
                    if st.button("🗑️", key=f"del_{theme_name}", help=f"Delete {theme_name}"):
                        # Delete the custom theme file
                        try:
                            safe_name = theme_name.lower().replace(' ', '_').replace('-', '_')
                            filename = f"custom_{safe_name}.json"
                            filepath = os.path.join(os.path.dirname(__file__), "themes", "json", filename)
                            if os.path.exists(filepath):
                                os.remove(filepath)
                                st.success(f"Theme '{theme_name}' deleted!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting theme: {str(e)}")

    if st.button("Refresh Data", use_container_width=True):

        st.cache_data.clear()
        st.success("Cache cleared! Data will be refreshed on next interaction.")
        st.rerun()
        
    st.info("💡 Tip: Use the 'Badges' tab to add your tech stack icons!")

# Data Loading
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(user, token=None):
    d = github_api.get_live_github_data(user, token)
    if not d:
        st.warning("Using mock data (API limits).")
        d = github_api.get_mock_data(user)

data = load_data(username if username else "torvalds", github_token if github_token else None)

# Ensure backward compatibility with old cached data
if "top_repos" not in data:
    data["top_repos"] = []

# Apply custom colors to current theme for python logic
current_theme_opts = all_themes.get(selected_theme, all_themes["Default"]).copy()
if custom_colors:
    current_theme_opts.update(custom_colors)


# --- Layout: Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(["Main Stats", "Languages", "Top Repositories", "Contributions", "🔥 GitHub Streak", "Icons & Badges", "🔥 AI Roast", "Recent Activity", "✨ Visual Elements", "🏆 GitHub Trophy"])

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
    svg_bytes = stats_card.draw_stats_card(data, selected_theme, show_ops, custom_colors, animations_enabled)
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

    # Date Range Selector
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    
    col_date1, col_date2 = st.columns([1, 1])
    with col_date1:
        date_option = st.selectbox(
            "Date Range",
            ["All Time", "Last 6 Months", "Current Year", "Custom Range"],
            index=0,
            help="Select the date range for contributions"
        )
    
    # Initialize date_range
    date_range = None
    
    if date_option == "Custom Range":
        with col_date2:
            custom_start = st.date_input("Start Date", value=today - timedelta(days=180))
            custom_end = st.date_input("End Date", value=today)
        date_range = {
            'start': custom_start.strftime("%Y-%m-%d"),
            'end': custom_end.strftime("%Y-%m-%d")
        }
    elif date_option == "Last 6 Months":
        date_range = {
            'start': (today - timedelta(days=180)).strftime("%Y-%m-%d"),
            'end': today.strftime("%Y-%m-%d")
        }
    elif date_option == "Current Year":
        date_range = {
            'start': datetime(today.year, 1, 1).date().strftime("%Y-%m-%d"),
            'end': today.strftime("%Y-%m-%d")
        }
    # All Time returns None, showing all contributions

    # Pass selected_theme string and date_range
    svg_bytes = contrib_card.draw_contrib_card(data, selected_theme, custom_colors, date_range=date_range, animations_enabled=animations_enabled)
    render_tab(svg_bytes, "contributions", username, selected_theme, custom_colors, code_template="![Contributions]({url})")

with tab5:
    st.subheader("GitHub Streak")
    st.caption("🔥 Track your contribution streaks! Shows current consecutive days and your all-time longest streak.")
    
    svg_bytes = streak_card.draw_streak_card(data, selected_theme, custom_colors)
    render_tab(svg_bytes, "streak", username, selected_theme, custom_colors, code_template="![GitHub Streak]({url})")

with tab6:
    st.subheader("Tech Stack Badges")
    st.markdown("Click detailed settings to customize. Copy the code block to your README.")
    
    col_tools, col_preview = st.columns([2, 1.5])
    
    with col_tools:
        # Badge Settings
        badge_style = st.selectbox("Badge Style", ["for-the-badge", "flat", "flat-square", "plastic", "social"], index=0)
        
        # Categories
        for category, tools in badge_generator.TECH_STACK.items():
            st.markdown(f"**{category}**")
            cols = st.columns(4)
            for i, (tool_name, specs) in enumerate(tools.items()):
                # Checkbox to include
                # If we want a click-to-add flow without rerun, we need session state lists
                # Let's use Multiselect for efficiency or columns of checkboxes
                # A Multiselect for each category is cleaner
                pass
            
            # Better UI: Multi-selects per category
            selected = st.multiselect(f"Select {category}", list(tools.keys()), key=f"sel_{category}")
            if selected:
                # Add to a session state list for the preview? 
                # Actually just rendering them below is fine.
                if "badges" not in st.session_state: st.session_state.badges = []
                # append is tricky with immediate reruns. 
                # Let's just gather all selected options from all multiselects at render time.
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
                # Allow user to override color?
                # For now use default brand color
                all_selected_badges.append((item, conf))
        
        if not all_selected_badges:
            st.info("Select tools from the left to generate badges.")
        else:
            # Render Preview
            md_output = ""
            # Making Global Variable, if user wants to match the theme:   
            should_match = st.checkbox("Match Theme Color", value=False, key="match_theme_global")
            for name, conf in all_selected_badges:
                # Logic to use custom color if user wants consistency?
                # User asked for customization.
                # Let's add a "Override All Colors" checkbox
                
                final_color = conf['color']
                # Using the variable we captured before:
                if should_match:
                    final_color = current_theme_opts['title_color'].replace("#", "")
                
                url = badge_generator.generate_badge_url(name, final_color, conf['logo'], style=badge_style)
                st.markdown(f"![{name}]({url})")
                md_output += f"![{name}]({url}) "
            
            st.markdown("---")
            show_code_area(md_output, label="Badge Code")

# NEW TAB 7: AI ROAST
with tab7:
    st.subheader("🔥 AI Profile Roast")

    st.markdown("Let AI roast your GitHub profile with humor!")
    
    if username:
        render_roast_widget(username)
    else:
        st.warning("Please enter a GitHub username in the sidebar.")

with tab8:
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

with tab9:
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

# NEW TAB 10: Trophy Card
with tab10:
    st.subheader("🏆 GitHub Trophy")
    st.markdown("Display your achievements including stars, forks, followers, and repository quality tier!")
    
    # Get created_at from GitHub API data if available
    trophy_data = data.copy()
    # Try to get created_at from user data if available
    if "created_at" not in trophy_data:
        # Add a default for testing
        trophy_data["created_at"] = "2010-01-01T00:00:00Z"
    
    svg_bytes = trophy_card.draw_trophy_card(trophy_data, selected_theme, custom_colors)
    render_tab(svg_bytes, "trophy", username, selected_theme, custom_colors, code_template="![GitHub Trophy]({url})")
