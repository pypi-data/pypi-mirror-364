import pickle
from typing import Any, Optional
from pathlib import Path
from datetime import datetime
import json
import argparse
import sys
import os

def print_banner(title: str = "", width: int = 50):
    """
    Prints a banner with a centered title and horizontal lines.
    """
    print("\n" + "═" * width)
    if title:
        print(title.center(width))
        print("═" * width)

class DBDB:
    """
    A file-based key-value store with data persistence, backup, JSON export,
    and simple metadata tracking (created/updated time).
    """

    def __init__(self, filename: str) -> None:
        if os.path.isabs(filename):
            self.filename = Path(filename)
        else:
            db_folder = Path.cwd() / "database"
            db_folder.mkdir(parents=True, exist_ok=True)
            self.filename = db_folder / filename
        self._load()

    def _load(self) -> None:
        try:
            with self.filename.open('rb') as f:
                self.data = pickle.load(f)
            if not isinstance(self.data, dict) or "store" not in self.data:
                self.data = {
                    "store": self.data if isinstance(self.data, dict) else {},
                    "meta": {
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                }
        except FileNotFoundError:
            self.data = {
                "store": {},
                "meta": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            }

    def _commit(self) -> None:
        with self.filename.open('wb') as f:
            pickle.dump(self.data, f)

    def put(self, key: Any, value: Any) -> None:
        self.data['store'][key] = value
        self.data["meta"]["updated_at"] = datetime.now().isoformat()
        self._commit()

    def get(self, key: Any) -> Optional[Any]:
        return self.data['store'].get(key)

    def delete(self, key: Any) -> None:
        if key in self.data['store']:
            del self.data['store'][key]
        self.data["meta"]["updated_at"] = datetime.now().isoformat()
        self._commit()

    def list_keys(self) -> list:
        return list(self.data['store'].keys())

    def exist(self, key: Any) -> bool:
        return key in self.data['store']

    def size(self) -> int:
        return len(self.data['store'])

    def clear(self) -> None:
        self.data['store'].clear()
        self.data["meta"]["updated_at"] = datetime.now().isoformat()
        self._commit()

    def get_created_time(self) -> str:
        return self.data['meta']['created_at']

    def get_updated_time(self) -> str:
        return self.data['meta']['updated_at']

    def backup(self, filename: str) -> None:
        if os.path.isabs(filename):
            backup_path = Path(filename)
        else:
            backup_dir = Path.cwd() / "BackUp"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / filename
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with open(backup_path, 'wb') as f:
            pickle.dump(self.data, f)

    def export_json(self, export_filename: str) -> None:
        if os.path.isabs(export_filename):
            export_path = Path(export_filename)
        else:
            export_path = Path.cwd() / export_filename
        
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with export_path.open('w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

def interactive_menu():
    db = DBDB("mydb.dat")

    while True:
        print("\n📁 DBDB MENU")
        print("1. Put key-value")
        print("2. Get a value")
        print("3. Delete a key")
        print("4. List all keys")
        print("5. Check if key exists")
        print("6. Check Length of DB")
        print("7. Get creation time")
        print("8. Get updation time")
        print("9. Export to JSON")
        print("10. Backup DB")
        print("11. Clear database")
        print("12. Exit")

        choice = input("Select an option (1-12): ")

        if choice == "1":
            key = input("Enter key: ")
            value = input("Enter value: ")
            db.put(key, value)
            print_banner("✅ Saved")

        elif choice == "2":
            key = input("Enter key to get: ")
            value = db.get(key)
            print_banner("📦 Retrieved Value")
            print(value)

        elif choice == "3":
            key = input("Enter key to delete: ")
            db.delete(key)
            print_banner("🗑️ Deleted")

        elif choice == "4":
            print_banner("🔑 All Keys")
            print(db.list_keys())

        elif choice == "5":
            key = input("Enter key to check: ")
            print_banner("🔍 Existence Check")
            print("Exists:", db.exist(key))

        elif choice == "6":
            print_banner("📏 Database Size")
            print(f"Total entries: {db.size()}")

        elif choice == "7":
            print_banner("📅 Created At")
            print(db.get_created_time())

        elif choice == "8":
            print_banner("🕒 Last Updated At")
            print(db.get_updated_time())

        elif choice == "9":
            name = input("Export filename (e.g. db.json): ")
            db.export_json(name)
            print_banner("📤 Exported to JSON")

        elif choice == "10":
            name = input("Backup filename (e.g. backup.dat): ")
            db.backup(name)
            print_banner("💾 Backup Saved")

        elif choice == "11":
            confirm = input("Are you sure? This will clear the database! (yes/no): ")
            if confirm.lower() == "yes":
                db.clear()
                print_banner("🧹 Database Cleared")

        elif choice == "12":
            print_banner("👋 Goodbye! I hope you found it useful.")
            break

        else:
            print_banner("❌ Invalid Input. Try Again.")

def main():
    parser = argparse.ArgumentParser(description="DBDB Command-Line Interface")
    parser.add_argument("command", choices=[
        "backup", "clear", "creation_time", "delete", "exist",
        "export_json", "get", "list", "put", "size", "updation_time"
    ])
    parser.add_argument("key", nargs="?", default=None)
    parser.add_argument("value", nargs="?", default=None)
    parser.add_argument("--db", default="mydb.dat", help="Database file name")

    args = parser.parse_args()
    db = DBDB(args.db)

    if args.command == "put" and args.key and args.value:
        db.put(args.key, args.value)
        print_banner("✅ Success")

    elif args.command == "get" and args.key:
        print_banner("📦 Value")
        print(db.get(args.key))

    elif args.command == "delete" and args.key:
        db.delete(args.key)
        print_banner("🗑️ Deleted")

    elif args.command == "list":
        print_banner("🔑 All Keys")
        print(db.list_keys())

    elif args.command == "exist" and args.key:
        print_banner("🔍 Existence Check")
        print(db.exist(args.key))

    elif args.command == "size":
        print_banner("📏 Total Entries")
        print(f"{db.size()}")

    elif args.command == "creation_time":
        print_banner("📅 Created At")
        print(db.get_created_time())

    elif args.command == "updation_time":
        print_banner("🕒 Last Updated At")
        print(db.get_updated_time())

    elif args.command == "clear":
        confirm = input("⚠ This will delete all data. Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            db.clear()
            print_banner("🧹 Database Cleared")
        else:
            print_banner("❌ Aborted")

    elif args.command == "backup" and args.key:
        db.backup(args.key)
        print_banner("💾 Backup Created Successfully")

    elif args.command == "export_json" and args.key:
        db.export_json(args.key)
        print_banner("📤 Exported Successfully")

    else:
        print_banner("❌ Invalid command or missing arguments")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        mode = input("Choose mode: [1] CLI  [2] Interactive Menu: ")
        if mode == "2":
            interactive_menu()
        elif mode == "1":
            print_banner("➡ You chose CLI mode. Restart program in terminal")
            print("👉 Example usage:")
            print("   python dbdb_project.py put <your_key> <your_value>")
            print("   python dbdb_project.py get <your_key>")
            print("   python dbdb_project.py delete <your_key>")
            print("   python dbdb_project.py list")
            print("   python dbdb_project.py size")
            print("   python dbdb_project.py updation_time")
            print("   python dbdb_project.py creation_time")
            print("   python dbdb_project.py clear")
            print("   python dbdb_project.py export_json <filename.json>")
            print("   python dbdb_project.py backup <filename.dat>")
        else:
            print_banner("❌ Invalid mode. Exiting.")
