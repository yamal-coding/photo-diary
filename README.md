# Photo Diary

A simple, static web-based photo diary organized by month.

## Photo Classification

Photos are grouped into monthly collections. Each month lives in a top-level folder named `MM-YYYY` (e.g., `04-2026`). Within a month folder, photos are stored flat — no sub-folders — and named sequentially: `photo1.jpg`, `photo2.jpg`, and so on.

## Manifest Files

The app relies on two levels of manifest to load content at runtime without any build step or filesystem scanning.

**`months-manifest.json`** (root level) — lists all available month folders in chronological order. The app reads this to power prev/next month navigation.

**`MM-YYYY/manifest.json`** (per month) — lists the photo filenames to display for that month, in order. Both manifests must be updated manually when adding new months or photos.

## Adding and Optimizing Photos

Use `scripts/optimize_images.py` to compress photos and add them to a month. The script resizes images to a max of 1600px on the longest side, converts them to JPEG, strips metadata, and updates both manifest files automatically. Existing images in the destination folder are never modified.

Install the dependency once:

```bash
python3 -m pip install pillow
```

Then run:

```bash
python3 scripts/optimize_images.py /path/to/source/photos MM-YYYY
```

For example, to add photos from `~/Desktop/may` to `05-2026`:

```bash
python3 scripts/optimize_images.py ~/Desktop/may 05-2026
```

The script prints a per-image breakdown and a final size comparison between the originals and the optimized outputs.

## Running Locally

From the project root, start a local HTTP server:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.
