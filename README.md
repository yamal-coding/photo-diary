# Photo Diary

A simple, static web-based photo diary organized by month.

## Photo Classification

Photos are grouped into monthly collections. Each month lives in a top-level folder named `MM-YYYY` (e.g., `04-2026`). Within a month folder, photos are stored flat — no sub-folders — and named sequentially: `photo1.jpg`, `photo2.jpg`, and so on.

## Manifest Files

The app relies on two levels of manifest to load content at runtime without any build step or filesystem scanning.

**`months-manifest.json`** (root level) — lists all available month folders in chronological order. The app reads this to power prev/next month navigation.

**`MM-YYYY/manifest.json`** (per month) — lists the photo filenames to display for that month, in order. Both manifests must be updated manually when adding new months or photos.

## Running Locally

From the project root, start a local HTTP server:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.
