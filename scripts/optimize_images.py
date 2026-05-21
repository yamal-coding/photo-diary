#!/usr/bin/env python3
"""
optimize_images.py – compress and optimize images for the photo-diary webapp.

Usage:
    python3 scripts/optimize_images.py <source_folder> <MM-YYYY>

Requirements:
    python3 -m pip install pillow
"""

import argparse
import json
import os
import re
import sys

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_DIMENSION = 1600          # longest side in pixels
JPEG_QUALITY = 82
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def require_pillow():
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        sys.exit(
            "Error: Pillow is not installed.\n"
            "Install it with:  python3 -m pip install pillow"
        )


def format_size(n_bytes: int) -> str:
    if n_bytes >= 1_000_000:
        return f"{n_bytes / 1_000_000:.1f} MB"
    if n_bytes >= 1_000:
        return f"{n_bytes / 1_000:.1f} KB"
    return f"{n_bytes} B"


def validate_month(month: str) -> bool:
    return bool(re.fullmatch(r"\d{2}-\d{4}", month))


def collect_source_images(source_folder: str) -> list[str]:
    """Return sorted list of absolute paths to supported images in source_folder."""
    entries = sorted(os.listdir(source_folder))
    result = []
    for name in entries:
        ext = os.path.splitext(name)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            result.append(os.path.join(source_folder, name))
    return result


def existing_dest_images(dest_folder: str) -> set[str]:
    """Return filenames already present in the destination folder."""
    if not os.path.isdir(dest_folder):
        return set()
    return {
        name
        for name in os.listdir(dest_folder)
        if os.path.splitext(name)[1].lower() in SUPPORTED_EXTENSIONS
    }


def next_sequence_number(existing_names: set[str]) -> int:
    """Return the next photo sequence number (1-based) that is not already used."""
    used = set()
    for name in existing_names:
        m = re.match(r"^photo(\d+)", name)
        if m:
            used.add(int(m.group(1)))
    n = 1
    while n in used:
        n += 1
    return n


def unique_dest_name(base_name: str, existing_names: set[str]) -> str:
    """
    Given a desired base_name like 'photo3.jpg', return a name that does not
    collide with existing_names. Appends -1, -2, … as needed.
    """
    if base_name not in existing_names:
        return base_name
    stem, ext = os.path.splitext(base_name)
    suffix = 1
    while True:
        candidate = f"{stem}-{suffix}{ext}"
        if candidate not in existing_names:
            return candidate
        suffix += 1


def optimize_image(src_path: str, dest_path: str):
    """Open, resize, strip metadata, and save as optimized JPEG."""
    from PIL import Image

    with Image.open(src_path) as img:
        # Normalise orientation from EXIF before stripping metadata
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # Convert to RGB (handles RGBA / P / L modes)
        if img.mode != "RGB":
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode in ("RGBA", "LA"):
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background

        # Resize if necessary, preserving aspect ratio
        w, h = img.size
        if max(w, h) > MAX_DIMENSION:
            if w >= h:
                new_w = MAX_DIMENSION
                new_h = round(h * MAX_DIMENSION / w)
            else:
                new_h = MAX_DIMENSION
                new_w = round(w * MAX_DIMENSION / h)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        # Save without any metadata
        img.save(
            dest_path,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
        )


# ---------------------------------------------------------------------------
# manifest helpers
# ---------------------------------------------------------------------------

def load_month_manifest(dest_folder: str) -> list[str]:
    path = os.path.join(dest_folder, "manifest.json")
    if os.path.isfile(path):
        with open(path) as f:
            data = json.load(f)
        return data.get("photos", [])
    return []


def save_month_manifest(dest_folder: str, photos: list[str]):
    path = os.path.join(dest_folder, "manifest.json")
    with open(path, "w") as f:
        json.dump({"photos": photos}, f, indent=4)
        f.write("\n")


def load_months_manifest() -> list[str]:
    path = os.path.join(REPO_ROOT, "months-manifest.json")
    if os.path.isfile(path):
        with open(path) as f:
            data = json.load(f)
        return data.get("months", [])
    return []


def save_months_manifest(months: list[str]):
    path = os.path.join(REPO_ROOT, "months-manifest.json")
    with open(path, "w") as f:
        json.dump({"months": months}, f, indent=2)
        f.write("\n")


def month_sort_key(month: str) -> tuple[int, int]:
    """Sort key for MM-YYYY strings, oldest first."""
    mm, yyyy = month.split("-")
    return (int(yyyy), int(mm))


def ensure_month_in_root_manifest(month: str):
    months = load_months_manifest()
    if month not in months:
        months.append(month)
        months.sort(key=month_sort_key)
        save_months_manifest(months)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    require_pillow()

    parser = argparse.ArgumentParser(
        description="Compress and optimize images for the photo-diary webapp."
    )
    parser.add_argument("source_folder", help="Path to the folder containing source images")
    parser.add_argument("month", help="Target month in MM-YYYY format")
    args = parser.parse_args()

    source_folder = os.path.abspath(args.source_folder)
    month = args.month

    # --- validation ---
    if not os.path.isdir(source_folder):
        sys.exit(f"Error: source folder does not exist: {source_folder}")
    if not validate_month(month):
        sys.exit(f"Error: month must be in MM-YYYY format, got: {month!r}")

    dest_folder = os.path.join(REPO_ROOT, month)
    os.makedirs(dest_folder, exist_ok=True)

    # --- collect source images ---
    source_images = collect_source_images(source_folder)
    if not source_images:
        sys.exit(f"No supported images found in {source_folder}")

    # --- existing destination state ---
    existing_names = existing_dest_images(dest_folder)
    existing_manifest = load_month_manifest(dest_folder)

    # Start sequence numbering after whatever is already in the destination
    seq = next_sequence_number(existing_names)

    # Working set of all names (existing + newly added) for collision detection
    all_dest_names = set(existing_names)

    new_filenames: list[str] = []
    skipped: list[str] = []
    total_original_bytes = 0
    total_optimized_bytes = 0

    print(f"\nSource:      {source_folder}")
    print(f"Destination: {dest_folder}")
    print(f"Images found: {len(source_images)}\n")

    for src_path in source_images:
        src_name = os.path.basename(src_path)
        desired_name = f"photo{seq}.jpg"
        dest_name = unique_dest_name(desired_name, all_dest_names)
        dest_path = os.path.join(dest_folder, dest_name)

        try:
            original_size = os.path.getsize(src_path)
            optimize_image(src_path, dest_path)
            optimized_size = os.path.getsize(dest_path)

            total_original_bytes += original_size
            total_optimized_bytes += optimized_size
            all_dest_names.add(dest_name)
            new_filenames.append(dest_name)

            reduction = (1 - optimized_size / original_size) * 100 if original_size else 0
            print(
                f"  {src_name:40s}  →  {dest_name}  "
                f"({format_size(original_size)} → {format_size(optimized_size)}, "
                f"{reduction:.0f}% smaller)"
            )
        except Exception as exc:
            print(f"  SKIP  {src_name}: {exc}")
            skipped.append(src_name)

        seq += 1

    if not new_filenames:
        print("No images were processed.")
        return

    # --- update manifests ---
    updated_manifest = existing_manifest + new_filenames
    save_month_manifest(dest_folder, updated_manifest)
    ensure_month_in_root_manifest(month)

    # --- summary ---
    saved_bytes = total_original_bytes - total_optimized_bytes
    reduction_pct = (saved_bytes / total_original_bytes * 100) if total_original_bytes else 0.0

    print(f"\nProcessed {len(new_filenames)} image(s) into {month}/")
    if skipped:
        print(f"Skipped {len(skipped)} file(s): {', '.join(skipped)}")
    print()
    print(f"  Original size:   {format_size(total_original_bytes)}")
    print(f"  Optimized size:  {format_size(total_optimized_bytes)}")
    print(f"  Saved:           {format_size(saved_bytes)}")
    print(f"  Reduction:       {reduction_pct:.1f}%")
    print()


if __name__ == "__main__":
    main()
