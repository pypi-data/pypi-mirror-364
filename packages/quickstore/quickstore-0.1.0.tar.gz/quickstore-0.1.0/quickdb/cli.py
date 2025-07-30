import argparse
from quickstore.db import quickstore
from quickstore.filedb import FileDB
import os
import shutil
import hashlib

def main():
    parser = argparse.ArgumentParser(description="quickstore CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Set command
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("key")
    set_parser.add_argument("value")
    set_parser.add_argument("--ttl", type=int, default=None)

    # Get command
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("key")

    # Delete command
    del_parser = subparsers.add_parser("delete")
    del_parser.add_argument("key")

    # List command
    list_parser = subparsers.add_parser("list")

    # Search command (placeholder)
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")

    # Store file command
    storefile_parser = subparsers.add_parser("storefile")
    storefile_parser.add_argument("filepath")

    # Get file command
    getfile_parser = subparsers.add_parser("getfile")
    getfile_parser.add_argument("filename")

    # Delete file command
    deletefile_parser = subparsers.add_parser("deletefile")
    deletefile_parser.add_argument("filename")

    # List files command
    listfiles_parser = subparsers.add_parser("listfiles")

    # Search files command
    searchfiles_parser = subparsers.add_parser("searchfiles")
    searchfiles_parser.add_argument("query")

    # Wipe command
    wipe_parser = subparsers.add_parser("wipe")

    # Set password command
    setpass_parser = subparsers.add_parser("setpass")
    setpass_parser.add_argument("username")
    setpass_parser.add_argument("password")

    # Remove password command
    removepass_parser = subparsers.add_parser("removepass")

    # Edit file command
    editfile_parser = subparsers.add_parser("editfile")
    editfile_parser.add_argument("filename")
    editfile_parser.add_argument("--content", type=str, default=None, help="New content as string")
    editfile_parser.add_argument("--from-file", type=str, default=None, help="Path to file with new content")
    editfile_parser.add_argument("--append", action="store_true", help="Append content instead of overwriting")

    args = parser.parse_args()
    db = quickstore()
    filedb = FileDB()

    if args.command == "set":
        db.set(args.key, args.value, ttl=args.ttl)
        print(f"Set {args.key}")
    elif args.command == "get":
        value = db.get(args.key)
        print(value if value is not None else "Key not found")
    elif args.command == "delete":
        db.delete(args.key)
        print(f"Deleted {args.key}")
    elif args.command == "list":
        print(db.list_keys())
    elif args.command == "search":
        results = db.search(args.query)
        print(results if results else "No matches found")
    elif args.command == "storefile":
        filedb.store_file(args.filepath)
        print(f"Stored file: {args.filepath}")
    elif args.command == "getfile":
        path = filedb.get_file(args.filename)
        print(path if path else "File not found")
    elif args.command == "deletefile":
        filedb.delete_file(args.filename)
        print(f"Deleted file: {args.filename}")
    elif args.command == "listfiles":
        print(filedb.list_files())
    elif args.command == "searchfiles":
        matches = filedb.search_files(args.query)
        print(matches if matches else "No matches found")
    elif args.command == "setpass":
        auth = {"username": args.username, "password": hashlib.sha256(args.password.encode()).hexdigest()}
        with open("quickstore_auth.json", "w") as f:
            import json
            json.dump(auth, f)
        print("Credentials set.")
    elif args.command == "removepass":
        if os.path.exists("quickstore_auth.json"):
            os.remove("quickstore_auth.json")
            print("Credentials removed.")
        else:
            print("No credentials set.")
    elif args.command == "wipe":
        # Check for credentials
        auth_path = "quickstore_auth.json"
        if os.path.exists(auth_path):
            import json
            with open(auth_path) as f:
                auth = json.load(f)
            user = input("Username: ").strip()
            pw = input("Password: ").strip()
            if user != auth["username"] or hashlib.sha256(pw.encode()).hexdigest() != auth["password"]:
                print("Authentication failed. Wipe cancelled.")
                return
        confirm = input("Are you sure you want to wipe ALL quickstore data and files? This cannot be undone. (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Wipe cancelled.")
            return
        # Delete key-value DB
        if os.path.exists("quickstore.json"):
            os.remove("quickstore.json")
            print("Deleted quickstore.json")
        # Delete file metadata
        if os.path.exists("filemeta.json"):
            os.remove("filemeta.json")
            print("Deleted filemeta.json")
        # Delete all files in quickstore/files/
        if os.path.exists("quickstore/files"):
            import shutil
            shutil.rmtree("quickstore/files")
            print("Deleted quickstore/files directory")
        # Advanced cleanup: build, dist, .egg-info
        for folder in ["build", "dist", "quickstore.egg-info"]:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
                print(f"Deleted {folder} directory")
        # Recursively delete all __pycache__ folders
        for root, dirs, files in os.walk("."):
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                import shutil
                shutil.rmtree(pycache_path)
                print(f"Deleted {pycache_path}")
        print("Database and file storage wiped.")
    elif args.command == "editfile":
        allowed_ext = (".txt", ".json", ".csv")
        if not args.filename.lower().endswith(allowed_ext):
            print("Editing is only allowed for text, JSON, or CSV files.")
            return
        path = filedb.get_file(args.filename)
        if not path or not os.path.exists(path):
            print("File not found in DB.")
            return
        if args.content is not None:
            new_content = args.content
        elif args.from_file is not None:
            if not os.path.exists(args.from_file):
                print("Source file not found.")
                return
            with open(args.from_file, "r", encoding="utf-8") as f:
                new_content = f.read()
        else:
            print("Provide --content or --from-file.")
            return
        mode = "a" if args.append else "w"
        with open(path, mode, encoding="utf-8") as f:
            f.write(new_content)
        action = "Appended to" if args.append else "Edited"
        print(f"{action} file: {args.filename}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 