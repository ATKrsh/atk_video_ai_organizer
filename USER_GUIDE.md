# ATK Video AI Organizer — User Guide

## 1. Importing Videos

There are three ways to add videos to your library:

1. **+ Add Video**: Click the `+ Add Video` button in the header or Import tab to open the Windows file picker. You can select one or multiple video files (.mp4, .mov, .mkv, .avi, .webm, etc.).
2. **+ Add Folder**: Click `+ Add Folder` to select a folder. The application recursively scans all subfolders for videos.
3. **Drag & Drop**: Drag files or folders directly onto the drop zone in the Import screen.

### Import Preview
After selecting files or folders, an **Import Preview** dialog will display:
- Total videos discovered
- Total file size (GB)
- Estimated duration
- New videos vs already indexed duplicates vs corrupt files

Click **ADD TO LIBRARY** to confirm. Your original files will **NOT** be moved or copied.

---

## 2. Natural Language Semantic Search

Navigate to **Semantic Search** in the sidebar. You can type plain English or natural language queries:
- `"dog running outside"`
- `"man riding motorcycle at night"`
- `"find videos containing Hindi speech"`
- `"blue car"`

Each search result shows a **Match Score** and **Match Reasons** explaining why the video was matched (e.g. `✓ motorcycle detected`, `✓ riding activity`, `✓ transcript match`).

---

## 3. Duplicate Detection & Quality Scoring

Navigate to **Duplicates** and click **Find Duplicates Now**:
- **Exact Duplicates**: Identified via cryptographic SHA-256 hash.
- **Near Duplicates**: Identified via perceptual hashing (re-encoded or resized copies).
- **Semantic Duplicates**: Identified via vector embedding similarity.

Each duplicate group features a **"Keep (Highest Quality)"** badge on the file with the best resolution, bitrate, and sharpness. **No files are ever automatically deleted.**

---

## 4. Virtual Categories & Folder Watching

- **Categories**: Assign videos to categories (People, Animals, Vehicles, Memes, etc.) virtually.
- **Folder Watcher**: Enable folder monitoring in **Settings** so newly added videos in your watched folders are automatically detected and queued.
