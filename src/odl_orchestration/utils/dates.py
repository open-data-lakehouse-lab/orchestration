from datetime import datetime

def get_current_date_str() -> str:
    """Returns current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

def get_timestamp_id() -> str:
    """Returns a timestamp-based ID."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")
