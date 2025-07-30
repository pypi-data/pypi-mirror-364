import json
import time
import os
from typing import Any, Dict, Optional

class quickstore:
    def __init__(self, db_path: str = "quickstore.json"):
        self.db_path = db_path
        self._db = {}
        self._load()

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        entry = {"value": value, "created_at": time.time()}
        if ttl is not None:
            entry["ttl"] = ttl
        self._db[key] = entry
        self._save()

    def get(self, key: str) -> Optional[Any]:
        self._expire_keys()
        entry = self._db.get(key)
        if entry:
            return entry["value"]
        return None

    def delete(self, key: str):
        if key in self._db:
            del self._db[key]
            self._save()

    def list_keys(self):
        self._expire_keys()
        return list(self._db.keys())

    def search(self, query: str) -> dict:
        self._expire_keys()
        q = query.lower()
        return {k: v["value"] for k, v in self._db.items() if q in k.lower() or q in str(v["value"]).lower()}

    def _expire_keys(self):
        now = time.time()
        expired = [k for k, v in self._db.items() if "ttl" in v and now - v["created_at"] > v["ttl"]]
        for k in expired:
            del self._db[k]
        if expired:
            self._save()

    def _save(self):
        with open(self.db_path, "w") as f:
            json.dump(self._db, f)

    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                self._db = json.load(f)
        else:
            self._db = {} 