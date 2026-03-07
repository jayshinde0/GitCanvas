import hashlib
from fastapi import FastAPI, Response, Query, Request
from generators import stats_card, lang_card, contrib_card, recent_activity_card, trophy_card, streak_card, repo_card
from utils import github_api
from utils.validators import (
    validate_username,
    validate_theme,
    validate_hex_color,
    validate_sort_by,
    validate_limit,
    validate_date
)
from typing import Optional

app = FastAPI()

# Implements HTTP conditional requests for CDN-safe SVG caching

def svg_response(svg_content: str, request: Request):
    etag = hashlib.md5(svg_content.encode("utf-8")).hexdigest()

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=14400, s-maxage=14400",
            "ETag": etag,
            "Vary": "Accept-Encoding",
            # Security headers to prevent XSS
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src data:",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN"
        }
    )



@app.get("/")
def read_root():
    return {"message": "GitCanvas API is running"}

def parse_colors(bg_color, title_color, text_color, border_color):
    """Helper to construct custom color dict with validation."""
    colors = {}
    
    # Validate and add colors
    if bg_color:
        validated_bg = validate_hex_color(bg_color)
        if validated_bg:
            colors["bg_color"] = validated_bg
            
    if title_color:
        validated_title = validate_hex_color(title_color)
        if validated_title:
            colors["title_color"] = validated_title
            
    if text_color:
        validated_text = validate_hex_color(text_color)
        if validated_text:
            colors["text_color"] = validated_text
            
    if border_color:
        validated_border = validate_hex_color(border_color)
        if validated_border:
            colors["border_color"] = validated_border
    
    return colors if colors else None

@app.get("/api/stats")
async def get_stats(
    request: Request,
    username: str, 
    theme: str = "Default", 
    hide_stars: bool = False,
    hide_commits: bool = False,
    hide_repos: bool = False,
    hide_followers: bool = False,
    animations_enabled: bool = True,
    bg_color: Optional[str] = None,
    title_color: Optional[str] = None,
    text_color: Optional[str] = None,
    border_color: Optional[str] = None,
    animations_enabled: bool = True
):
    # Validate inputs
    username = validate_username(username)
    theme = validate_theme(theme)
    
    data = github_api.get_live_github_data(username) or github_api.get_mock_data(username)
    
    show_options = {
        "stars": not hide_stars,
        "commits": not hide_commits,
        "repos": not hide_repos,
        "followers": not hide_followers
    }
    
    custom_colors = parse_colors(bg_color, title_color, text_color, border_color)
    svg_content = stats_card.draw_stats_card(data, theme, show_options=show_options, custom_colors=custom_colors, animations_enabled=animations_enabled)
    return svg_response(svg_content , request)


@app.get("/api/languages")
async def get_languages(
    request: Request,
    username: str,
    theme: str = "Default",
    exclude: Optional[str] = None,
    excluded_languages: Optional[str] = None,
    bg_color: Optional[str] = None,
    title_color: Optional[str] = None,
    text_color: Optional[str] = None,
    border_color: Optional[str] = None
):
    # Validate inputs
    username = validate_username(username)
    theme = validate_theme(theme)
    
    data = github_api.get_live_github_data(username) or github_api.get_mock_data(username)
    custom_colors = parse_colors(bg_color, title_color, text_color, border_color)
    
    # Parse exclude parameter into list of languages
    excluded_languages_list = []
    # Support both 'exclude' and 'excluded_languages' parameters
    param_value = exclude or excluded_languages
    if param_value:
        excluded_languages_list = [lang.strip() for lang in param_value.split(',') if lang.strip()]
    
    svg_content = lang_card.draw_lang_card(data, theme, custom_colors=custom_colors, excluded_languages=excluded_languages_list)
    return svg_response(svg_content , request)


@app.get("/api/contributions")
async def get_contributions(
    request: Request,
    username: str,
    theme: str = "Default",
    animations_enabled: bool = True,
    date_range: Optional[str] = None,
    bg_color: Optional[str] = None,
    title_color: Optional[str] = None,
    text_color: Optional[str] = None,
    border_color: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    animations_enabled: bool = True
):
    # Validate inputs
    username = validate_username(username)
    theme = validate_theme(theme)
    start_date = validate_date(start_date)
    end_date = validate_date(end_date)
    
    data = github_api.get_live_github_data(username) or github_api.get_mock_data(username)
    custom_colors = parse_colors(bg_color, title_color, text_color, border_color)
    
    # Build date_range dict if dates are provided
    date_range = None
    if start_date and end_date:
        date_range = {
            'start': start_date,
            'end': end_date
        }
    
    svg_content = contrib_card.draw_contrib_card(data, theme, custom_colors=custom_colors, date_range=date_range, animations_enabled=animations_enabled)
    return svg_response(svg_content , request)


@app.get("/api/recent")
async def get_recent(
    request: Request,
    username: str,
    theme: str = "Default",
    token: Optional[str] = None,
    bg_color: Optional[str] = None,
    title_color: Optional[str] = None,
    text_color: Optional[str] = None,
    border_color: Optional[str] = None
):
    # Validate inputs
    username = validate_username(username)
    theme = validate_theme(theme)
    
    custom_colors = parse_colors(bg_color, title_color, text_color, border_color)
    svg_content = recent_activity_card.draw_recent_activity_card({'username': username}, theme, custom_colors=custom_colors, token=token)
    return svg_response(svg_content, request)


@app.get("/api/trophy")
async def get_trophy(
    request: Request,
    username: str,
    theme: str = "Default",
    bg_color: Optional[str] = None,
    title_color: Optional[str] = None,
    text_color: Optional[str] = None,
    border_color: Optional[str] = None
):
    # Validate inputs
    username = validate_username(username)
    theme = validate_theme(theme)
    
    data = github_api.get_live_github_data(username) or github_api.get_mock_data(username)
    custom_colors = parse_colors(bg_color, title_color, text_color, border_color)
    svg_content = trophy_card.draw_trophy_card(data, theme, custom_colors=custom_colors)
    return svg_response(svg_content, request)


@app.get("/api/streak")
async def get_streak(
    request: Request,
    username: str,
    theme: str = "Default",
    bg_color: Optional[str] = None,
    title_color: Optional[str] = None,
    text_color: Optional[str] = None,
    border_color: Optional[str] = None
):
    # Validate inputs
    username = validate_username(username)
    theme = validate_theme(theme)
    
    data = github_api.get_live_github_data(username) or github_api.get_mock_data(username)
    custom_colors = parse_colors(bg_color, title_color, text_color, border_color)
    svg_content = streak_card.draw_streak_card(data, theme, custom_colors=custom_colors)
    return svg_response(svg_content, request)


@app.get("/api/repos")
async def get_repos(
    request: Request,
    username: str,
    theme: str = "Default",
    sort_by: str = "stars",
    limit: int = 5,
    bg_color: Optional[str] = None,
    title_color: Optional[str] = None,
    text_color: Optional[str] = None,
    border_color: Optional[str] = None
):
    # Validate inputs
    username = validate_username(username)
    theme = validate_theme(theme)
    sort_by = validate_sort_by(sort_by)
    limit = validate_limit(limit, min_val=1, max_val=10)
    
    data = github_api.get_live_github_data(username) or github_api.get_mock_data(username)
    custom_colors = parse_colors(bg_color, title_color, text_color, border_color)
    svg_content = repo_card.draw_repo_card(data, theme, custom_colors=custom_colors, sort_by=sort_by, limit=limit)
    return svg_response(svg_content, request)
