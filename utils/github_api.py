import requests
import os

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

if load_dotenv:
    load_dotenv()



def fetch_github_graphql(username, token=None):
    if not token:
        token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None

    query = """
    query ($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        GITHUB_GRAPHQL_URL,
        json={"query": query, "variables": {"login": username}},
        headers=headers,
        timeout=10
    )

    if resp.status_code != 200:
        return None
    

    return resp.json()

def parse_graphql_contributions(graphql_json):
    weeks = (
        graphql_json["data"]["user"]
        ["contributionsCollection"]
        ["contributionCalendar"]
        ["weeks"]
    )

    contributions = []
    contribution_weeks = []
    for week in weeks:
        week_days = []
        for day in week["contributionDays"]:
            day_entry = {
                "date": day["date"],
                "count": day["contributionCount"]
            }
            contributions.append(day_entry)
            week_days.append(day_entry)
        contribution_weeks.append(week_days)

    total_commits = (
        graphql_json["data"]["user"]
        ["contributionsCollection"]
        ["totalCommitContributions"]
    )

    return contributions, total_commits, contribution_weeks


def get_github_headers(token=None):
    """
    Build headers for GitHub REST API requests.
    Uses Authorization header if GITHUB_TOKEN is set.
    """
    headers = {
        "Accept": "application/vnd.github+json"
    }

    if not token:
        token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers

def get_live_github_data(username, token=None):
    """
    Fetches real data from GitHub API. 
    Notes: 
    - Unauthenticated requests are rate-limited (60/hr).
    - For a real production app, we need a token or use GraphQL.
    - For this MVP, we scrape or use public endpoints where possible to avoid token complexity for the user usage.
    """
    try:
        # User details
        user_url = f"https://api.github.com/users/{username}"
        headers = get_github_headers(token)
        user_resp = requests.get(user_url, headers=headers)

        if user_resp.status_code != 200:
            return None
        user_data = user_resp.json()
        
        # Repos for stars count (limited to first 100 public repos for basic sum without pagination for MVP speed)
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
        repos_resp = requests.get(repos_url, headers=headers)
        repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
        
        # Validate response is a list
        if not isinstance(repos_data, list):
            # API returned an error dict instead of list
            print(f"Repos API Error: {repos_data}")
            repos_data = []
        
        # Store all repos including forks for frontend (let user decide)
        all_repos = repos_data.copy()
        
        # For stats calculation, filter out forks
        repos_data_no_forks = [repo for repo in repos_data if not repo.get("fork", False)]
        
        # For stats calculation, filter out forks
        repos_data_no_forks = [repo for repo in repos_data if not repo.get("fork", False)]
        
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos_data_no_forks)
        
        # Languages (Approximation from top repos, excluding forks)
        languages = {}
        for repo in repos_data_no_forks[:10]: # Check top 10 non-fork repos
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Top repositories - include ALL repos (user can filter in UI if needed)
        top_repos = [{
            "name": repo.get("name", ""),
            "description": repo.get("description", ""),
            "language": repo.get("language", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "updated_at": repo.get("updated_at", ""),
            "is_fork": repo.get("fork", False)
        } for repo in sorted(all_repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:10]]
        
        print(f"Fetched {len(all_repos)} total repos ({len(repos_data_no_forks)} non-forks) for {username}, top_repos count: {len(top_repos)}")

        # Ensure total_commits is always an integer
        total_commits = 0 

        try:
            contrib_url = f"https://github-contributions-api.jogruber.de/v4/{username}"
            contrib_resp = requests.get(contrib_url)
            if contrib_resp.status_code == 200:
                c_data = contrib_resp.json()
                if 'total' in c_data and isinstance(c_data['total'], dict):
                    # Sum all year totals into a single integer
                    total_commits = sum(c_data['total'].values())
            # If the response isn't 200, it stays as 0
        except Exception as ex:
            print(f"Contrib API Error: {ex}")
            total_commits = 0 # Safety fallback

        data = {
            "username": username,
            "total_stars": total_stars,
            "total_commits": total_commits,
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "created_at": user_data.get("created_at", ""),
            "top_languages": top_langs,
            "top_repos": top_repos,
        }

        # --- Optional GraphQL enrichment ---
        graphql_data = fetch_github_graphql(username, token)
        if graphql_data:
            try:
                contributions, gql_total_commits, contribution_weeks = parse_graphql_contributions(graphql_data)
                data["contributions"] = contributions
                data["total_commits"] = gql_total_commits
                data["contribution_weeks"] = contribution_weeks
            except Exception:
                pass  # Never break REST fallback

        if "contributions" not in data:
            # Fallback to empty list; UI should handle missing contribution data gracefully.
            data["contributions"] = []

        return data

            
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_mock_data(username):
    """Returns dummy data for layout testing/building without hitting API limits"""
    return {
        "username": username,
        "total_stars": 120,
        "total_commits": 450,
        "public_repos": 25,
        "followers": 85,
        "created_at": "2015-06-15T00:00:00Z",
        "top_languages": [("Python", 10), ("JavaScript", 5), ("Rust", 2)],
        "contributions":[
            {"date": f"2025-01-{i+1:02d}", "count": (i * 3) % 10}
            for i in range(80)
        ],
        "top_repos": [
            {"name": "awesome-project", "description": "A cool project", "language": "Python", "stars": 150, "forks": 30, "updated_at": "2025-01-15"},
            {"name": "web-app", "description": "Modern web application", "language": "JavaScript", "stars": 89, "forks": 12, "updated_at": "2025-01-20"},
            {"name": "api-service", "description": "RESTful API service", "language": "Go", "stars": 65, "forks": 8, "updated_at": "2025-01-18"},
            {"name": "cli-tool", "description": "Command line utility", "language": "Rust", "stars": 42, "forks": 5, "updated_at": "2025-01-10"},
            {"name": "mobile-app", "description": "Cross-platform mobile app", "language": "TypeScript", "stars": 28, "forks": 3, "updated_at": "2025-01-12"}
        ]

    }


def filter_contributions_by_date(contributions, date_range):
    """
    Filter contributions by date range.
    
    Args:
        contributions: List of contribution dicts with 'date' and 'count' keys
        date_range: Dict with 'start' and 'end' date strings (YYYY-MM-DD format)
                    or None for all time
    
    Returns:
        Filtered list of contributions
    """
    if not contributions or not date_range:
        return contributions
    
    start_date = date_range.get('start')
    end_date = date_range.get('end')
    
    if not start_date or not end_date:
        return contributions
    
    try:
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return contributions
    
    filtered = []
    for item in contributions:
        item_date = item.get('date')
        if not item_date:
            continue
        try:
            parsed_date = datetime.strptime(item_date, "%Y-%m-%d").date()
            if start <= parsed_date <= end:
                filtered.append(item)
        except (ValueError, TypeError):
            continue
    
    return filtered


def get_date_range_from_option(date_option, custom_start=None, custom_end=None):
    """
    Get date range based on predefined options or custom range.
    
    Args:
        date_option: One of 'all_time', 'last_6_months', 'current_year', 'custom'
        custom_start: Start date for custom range (YYYY-MM-DD)
        custom_end: End date for custom range (YYYY-MM-DD)
    
    Returns:
        Dict with 'start' and 'end' date strings, or None for all time
    """
    from datetime import datetime, timedelta
    
    today = datetime.utcnow().date()
    
    if date_option == 'all_time' or date_option == 'all':
        return None
    
    elif date_option == 'last_6_months' or date_option == '6months':
        start = today - timedelta(days=180)
        return {
            'start': start.strftime("%Y-%m-%d"),
            'end': today.strftime("%Y-%m-%d")
        }
    
    elif date_option == 'current_year' or date_option == 'year':
        start = datetime(today.year, 1, 1).date()
        return {
            'start': start.strftime("%Y-%m-%d"),
            'end': today.strftime("%Y-%m-%d")
        }
    
    elif date_option == 'custom' and custom_start and custom_end:
        return {
            'start': custom_start,
            'end': custom_end
        }
    
    return None
