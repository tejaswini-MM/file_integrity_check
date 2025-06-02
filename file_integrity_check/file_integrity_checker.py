import hashlib
import os
import json

def calculate_hash(filepath, algo='sha256'):
    h = hashlib.new(algo)
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None

def generate_hashes(directory, hash_file='hashes.json', algo='sha256'):
    hashes = {}
    for root, _, files in os.walk(directory):
        for name in files:
            if name == hash_file or name.endswith('.py'):
                continue
            full_path = os.path.join(root, name)
            hash_value = calculate_hash(full_path, algo)
            if hash_value:
                hashes[full_path] = hash_value
    with open(hash_file, 'w') as f:
        json.dump(hashes, f, indent=4)
    print(f"✅ Hashes generated and saved to {hash_file}")

def check_integrity(directory, hash_file='hashes.json', algo='sha256'):
    try:
        with open(hash_file, 'r') as f:
            old_hashes = json.load(f)
    except FileNotFoundError:
        print("⚠️ No hash record found. Please run generate_hashes() first.")
        return

    current_hashes = {}
    modified, new, deleted = [], [], []

    for root, _, files in os.walk(directory):
        for name in files:
            if name == hash_file or name.endswith('.py'):
                continue
            full_path = os.path.join(root, name)
            hash_value = calculate_hash(full_path, algo)
            current_hashes[full_path] = hash_value

            if full_path not in old_hashes:
                new.append(full_path)
            elif old_hashes[full_path] != hash_value:
                modified.append(full_path)

    for old_path in old_hashes:
        if old_path not in current_hashes:
            deleted.append(old_path)

    if modified: print("🔄 Modified Files:\n", *modified, sep="\n- ")
    if new: print("🆕 New Files:\n", *new, sep="\n- ")
    if deleted: print("❌ Deleted Files:\n", *deleted, sep="\n- ")

    if not (modified or new or deleted):
        print("✅ No changes detected. All files are intact.")

# TESTING CALLS
generate_hashes(".")     # Scans current folder
check_integrity(".")     # Checks file integrity
