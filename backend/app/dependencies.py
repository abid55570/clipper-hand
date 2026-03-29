from app.db.session import get_async_session

# Re-export for convenience
get_db = get_async_session
