import os
import shutil
import json
import time

class FileDB:
    def __init__(self, files_dir="quickstore/files", meta_path="filemeta.json"):
        self.files_dir = files_dir
        self.meta_path = meta_path
        os.makedirs(self.files_dir, exist_ok=True)
        self._load_meta()

    def _load_meta(self):
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r") as f:
                self.meta = json.load(f)
        else:
            self.meta = {}

    def _save_meta(self):
        with open(self.meta_path, "w") as f:
            json.dump(self.meta, f)

    def store_file(self, filepath):
        filename = os.path.basename(filepath)
        dest_path = os.path.join(self.files_dir, filename)
        shutil.copy2(filepath, dest_path)
        stat = os.stat(dest_path)
        self.meta[filename] = {
            "original_name": filename,
            "size": stat.st_size,
            "stored_at": time.time(),
            "path": dest_path
        }
        self._save_meta()

    def get_file(self, filename):
        entry = self.meta.get(filename)
        if entry and os.path.exists(entry["path"]):
            return entry["path"]
        return None

    def delete_file(self, filename):
        entry = self.meta.get(filename)
        if entry and os.path.exists(entry["path"]):
            os.remove(entry["path"])
            del self.meta[filename]
            self._save_meta()

    def list_files(self):
        return list(self.meta.keys())

    def search_files(self, query):
        q = query.lower()
        return [fname for fname, meta in self.meta.items()
                if q in fname.lower() or q in meta.get('original_name', '').lower()] 

    def edit_file(self, filename, content=None, from_file=None, append=False):
        allowed_ext = (".txt", ".json", ".csv")
        if not filename.lower().endswith(allowed_ext):
            raise ValueError("Editing is only allowed for text, JSON, or CSV files.")
        path = self.get_file(filename)
        if not path or not os.path.exists(path):
            raise FileNotFoundError("File not found in DB.")
        if content is not None:
            new_content = content
        elif from_file is not None:
            if not os.path.exists(from_file):
                raise FileNotFoundError("Source file not found.")
            with open(from_file, "r", encoding="utf-8") as f:
                new_content = f.read()
        else:
            raise ValueError("Provide content or from_file.")
        mode = "a" if append else "w"
        with open(path, mode, encoding="utf-8") as f:
            f.write(new_content)
        return path 

    def wipe(self, require_auth=True):
        """
        Wipe all quickstore data: key-value DB, file metadata, stored files, and cleanup build artifacts.
        If require_auth is True and credentials are set, will prompt for username/password.
        """
        auth_path = "quickstore_auth.json"
        if require_auth and os.path.exists(auth_path):
            import json, hashlib
            user = input("Username: ").strip()
            pw = input("Password: ").strip()
            with open(auth_path) as f:
                auth = json.load(f)
            if user != auth["username"] or hashlib.sha256(pw.encode()).hexdigest() != auth["password"]:
                print("Authentication failed. Wipe cancelled.")
                return False
        # Delete key-value DB
        if os.path.exists("quickstore.json"):
            os.remove("quickstore.json")
        # Delete file metadata
        if os.path.exists("filemeta.json"):
            os.remove("filemeta.json")
        # Delete all files in quickstore/files/
        if os.path.exists("quickstore/files"):
            shutil.rmtree("quickstore/files")
        # Advanced cleanup: build, dist, .egg-info
        for folder in ["build", "dist", "quickstore.egg-info"]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
        # Recursively delete all __pycache__ folders
        for root, dirs, files in os.walk("."):
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                shutil.rmtree(pycache_path)
        print("Database and file storage wiped.")
        return True

    def setpass(self, username, password):
        """
        Set or update DB credentials (username, password). Password is stored as SHA-256 hash.
        """
        import hashlib, json
        auth = {"username": username, "password": hashlib.sha256(password.encode()).hexdigest()}
        with open("quickstore_auth.json", "w") as f:
            json.dump(auth, f)
        print("Credentials set.")

    def removepass(self):
        """
        Remove DB credentials (quickstore_auth.json).
        """
        if os.path.exists("quickstore_auth.json"):
            os.remove("quickstore_auth.json")
            print("Credentials removed.")
        else:
            print("No credentials set.") 