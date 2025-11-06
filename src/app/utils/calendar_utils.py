import secrets


def generate_calendar_url() -> str:
    '''
    Generate a unique calendar URL for a watchlist.
    
    Returns:
        str: A unique calendar URL token.
    '''
    # Generate a cryptographically secure random token
    token = secrets.token_urlsafe(32)
    calendar_url = f"https://calendar.example.com/{token}"
    return calendar_url
