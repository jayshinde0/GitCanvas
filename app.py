import streamlit as st  # type: ignore
import base64
import os
from dotenv import load_dotenv
from roast_widget_streamlit import render_roast_widget
from generators import stats_card, lang_card, contrib_card, badge_generator, recent_activity_card, social_card, streak_card, repo_card
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
    st.markdown(item, unsafe_allow_html=True)

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
        
        # Color pickers for custom theme
        custom_theme_name = st.text_input("Theme Name", value="My Custom Theme")
        ct_bg = st.color_picker("Background", value=st.session_state.custom_theme_colors["bg_color"], key="ct_bg")
        ct_border = st.color_picker("Border", value=st.session_state.custom_theme_colors["border_color"], key="ct_border")
        ct_title = st.color_picker("Title", value=st.session_state.custom_theme_colors["title_color"], key="ct_title")
        ct_text = st.color_picker("Text", value=st.session_state.custom_theme_colors["text_color"], key="ct_text")
        ct_icon = st.color_picker("Icon", value=st.session_state.custom_theme_colors["icon_color"], key="ct_icon")
        
        if st.button("Save Custom Theme"):
            from themes.styles import save_custom_theme
            theme_data = {
                "bg_color": ct_bg,
                "border_color": ct_border,
                "title_color": ct_title,
                "text_color": ct_text,
                "icon_color": ct_icon,
                "font_family": "Segoe UI, Ubuntu, Sans-Serif",
                "title_font_size": 20,
                "text_font_size": 14
            }
            save_custom_theme(custom_theme_name, theme_data)
            st.success(f"Theme '{custom_theme_name}' saved! Refresh to see it in the theme list.")

    # GitHub Token for API access
    st.header("3. API Access (Optional)")
    github_token = st.text_input("GitHub Token", type="password", value=os.getenv("GITHUB_TOKEN", ""), 
                                  help="Required for private repos and higher rate limits")

# Data Loading
@st.cache_data
def load_data(user, token):
    d = github_api.get_live_github_data(user, token)
    if not d:
        st.warning("Using mock data (API limits).")
        d = github_api.get_mock_data(user)
    return d

data = load_data(username if username else "torvalds", github_token if github_token else None)

# Apply custom colors to current theme for python logic
current_theme_opts = all_themes.get(selected_theme, all_themes["Default"]).copy()
if custom_colors:
    current_theme_opts.update(custom_colors)


# --- Layout: Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Main Stats", "Languages", "Contributions", "Streak", "Top Repos", "Icons & Badges", "Social Links", "🔥 AI Roast"])

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

with tab4:
    st.subheader("GitHub Streak")
    st.caption("🔥 Track your contribution streaks! Shows current consecutive days and your all-time longest streak.")
    
    svg_bytes = streak_card.draw_streak_card(data, selected_theme, custom_colors)
    render_tab(svg_bytes, "streak", username, selected_theme, custom_colors, code_template="![GitHub Streak]({url})")

with tab5:
    st.subheader("Top Repositories")
    st.caption("⭐ Showcase your best work! Display your most popular repositories.")
    
    # Controls
    col_sort, col_limit = st.columns(2)
    with col_sort:
        sort_by = st.selectbox("Sort by", ["stars", "forks", "updated"], index=0, 
                               format_func=lambda x: {"stars": "⭐ Stars", "forks": "🍴 Forks", "updated": "🕐 Recently Updated"}[x])
    with col_limit:
        limit = st.selectbox("Number of repos", [3, 5, 10], index=1)
    
    # Fetch top repos data
    from utils.github_api import get_top_repositories
    top_repos = get_top_repositories(username, sort_by=sort_by, limit=limit)
    
    # Update data dict with repos
    repo_data = data.copy()
    repo_data["top_repos"] = top_repos
    
    # Render card
    svg_bytes = repo_card.draw_repo_card(repo_data, selected_theme, custom_colors, sort_by=sort_by, limit=limit)
    render_tab(svg_bytes, "repos", username, selected_theme, custom_colors, 
               code_template=f"[![Top Repos]({{url}})](https://github.com/{username})")

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

with tab7:
    st.subheader("Social Links")
    st.markdown("Add your social media links and contact information.")
    
    # Social media inputs
    col1, col2 = st.columns(2)
    with col1:
        twitter_url = st.text_input("Twitter URL", placeholder="https://twitter.com/username", key="twitter")
        linkedin_url = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/username", key="linkedin")
        website_url = st.text_input("Website URL", placeholder="https://example.com", key="website")
    with col2:
        email_url = st.text_input("Email", placeholder="email@example.com", key="email")
        youtube_url = st.text_input("YouTube URL", placeholder="https://youtube.com/channel/...", key="youtube")
    
    # Platform selection
    st.markdown("**Select which links to display:**")
    col_select1, col_select2, col_select3 = st.columns(3)
    with col_select1:
        show_twitter = st.checkbox("Twitter", value=True, key="show_twitter")
        show_linkedin = st.checkbox("LinkedIn", value=True, key="show_linkedin")
    with col_select2:
        show_website = st.checkbox("Website", value=True, key="show_website")
        show_email = st.checkbox("Email", value=True, key="show_email")
    with col_select3:
        show_youtube = st.checkbox("YouTube", value=True, key="show_youtube")
    
    # Custom icon color
    use_custom_icon_color = st.checkbox("Use custom icon color", value=False, key="use_custom_icon_color")
    custom_icon_color = None
    if use_custom_icon_color:
        custom_icon_color = st.color_picker("Icon Color", value=current_theme_opts.get('title_color', '#58a6ff'), key="custom_icon_color")
    
    # Build social data dict
    social_data = {
        "twitter": twitter_url if show_twitter else "",
        "linkedin": linkedin_url if show_linkedin else "",
        "website": website_url if show_website else "",
        "email": f"mailto:{email_url}" if show_email and email_url else "",
        "youtube": youtube_url if show_youtube else ""
    }
    
    # Build selected platforms list
    selected_platforms = []
    if show_twitter and twitter_url: selected_platforms.append("twitter")
    if show_linkedin and linkedin_url: selected_platforms.append("linkedin")
    if show_website and website_url: selected_platforms.append("website")
    if show_email and email_url: selected_platforms.append("email")
    if show_youtube and youtube_url: selected_platforms.append("youtube")
    
    # Generate social card
    svg_bytes = social_card.draw_social_card(
        social_data, 
        selected_theme, 
        custom_colors, 
        selected_platforms=selected_platforms,
        icon_color=custom_icon_color
    )
    
    # Render using the standard tab rendering
    render_tab(svg_bytes, "social", username, selected_theme, custom_colors, code_template="![Social Links]({url})")

with tab8:
    st.subheader("🔥 AI Profile Roast")
    st.markdown("Let AI roast your GitHub profile with humor!")
    
    if username:
        render_roast_widget(username)
    else:
        st.warning("Please enter a GitHub username in the sidebar.")
