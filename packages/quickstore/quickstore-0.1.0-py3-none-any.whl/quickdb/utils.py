# Utility functions for quickstore

def is_expired(entry, now):
    if "ttl" in entry:
        return now - entry["created_at"] > entry["ttl"]
    return False 