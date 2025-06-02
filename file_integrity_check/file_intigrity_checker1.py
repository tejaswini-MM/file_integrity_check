import hashlib
import os
import json
import sys

HASH_FILE = "hashes.json"
EXCLUDE_EXTENSIONS = ['.py']

def normalize_path(path):
    return os.path.normpath(path).replace('\\', '/')

def calculate_hash(filepath, algo='sha256'):
    h = hashlib.new(algo)
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None

def generate_hashes(directory, hash_file=HASH_FILE, algo='sha256'):
    hashes = {}
    for root, _, files in os.walk(directory):
        for name in files:
            if name == hash_file or any(name.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                continue
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, directory)
            rel_path = normalize_path(rel_path)
            hash_value = calculate_hash(full_path, algo)
            if hash_value:
                hashes[rel_path] = hash_value
    with open(hash_file, 'w') as f:
        json.dump(hashes, f, indent=4)
    print(f"✅ Baseline hashes generated and saved to '{hash_file}'")

def check_integrity(directory, hash_file=HASH_FILE, algo='sha256'):
    try:
        with open(hash_file, 'r') as f:
            old_hashes_raw = json.load(f)
        old_hashes = {normalize_path(k): v for k, v in old_hashes_raw.items()}
    except FileNotFoundError:
        print(f"⚠️ No baseline hash file found ('{hash_file}'). Please run 'generate' first.")
        return

    current_hashes = {}
    modified, new, deleted = [], [], []

    for root, _, files in os.walk(directory):
        for name in files:
            if name == hash_file or any(name.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                continue
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, directory)
            rel_path = normalize_path(rel_path)
            hash_value = calculate_hash(full_path, algo)
            current_hashes[rel_path] = hash_value

            if rel_path not in old_hashes:
                new.append(rel_path)
            elif old_hashes[rel_path] != hash_value:
                modified.append(rel_path)

    for old_path in old_hashes:
        if old_path not in current_hashes:
            deleted.append(old_path)

    if modified:
        print("🔄 Modified Files:")
        for path in modified:
            print(f"- {path}")
            print(f"  Old Hash: {old_hashes[path]}")
            print(f"  New Hash: {current_hashes[path]}")
    if new:
        print("\n🆕 New Files:")
        for path in new:
            print(f"- {path} (Hash: {current_hashes[path]})")
    if deleted:
        print("\n❌ Deleted Files:")
        for path in deleted:
            print(f"- {path} (Old Hash: {old_hashes[path]})")

    if not (modified or new or deleted):
        print("✅ No changes detected. All files are intact.")

def print_usage():
    print("Usage:")
    print("  python file_monitor.py generate  # Generate baseline hashes")
    print("  python file_monitor.py check     # Check for changes")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "generate":
        generate_hashes(".")
    elif command == "check":
        check_integrity(".")
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
