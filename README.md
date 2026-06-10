# Folder Cleaner

A small, dependency-free Python utility that keeps your Downloads folder
(or any folder) tidy by sorting files into category-based subfolders.
Works on Windows, Linux and macOS.

<p align="left">
  <a href="https://www.python.org/"><img src="https://skillicons.dev/icons?i=python" alt="Python" /></a>
  <a href="https://github.com/"><img src="https://skillicons.dev/icons?i=github" alt="GitHub" /></a>
  <a href="https://www.linux.org/"><img src="https://skillicons.dev/icons?i=linux" alt="Linux" /></a>
  <a href="https://www.apple.com/macos/"><img src="https://skillicons.dev/icons?i=apple" alt="macOS" /></a>
  <a href="https://www.microsoft.com/windows/"><img src="https://skillicons.dev/icons?i=windows" alt="Windows" /></a>
  <a href="https://code.visualstudio.com/"><img src="https://skillicons.dev/icons?i=vscode" alt="VS Code" /></a>
</p>

## Features

- **Automatic classification** — files are sorted into `Documents`, `Images`,
  `Videos`, `Audio`, `Archives`, `Installers`, `Code`, or `Other` based on
  their extension.
- **Two modes** — run a one-shot pass, or run in the background and organize
  new files as they appear.
- **Zero dependencies** — uses only the Python standard library.
- **Cross-platform** — detects the user's Downloads folder on Windows, Linux
  and macOS.
- **Safe by default** — never overwrites a file; appends ` (1)`, ` (2)`, …
  to resolve name conflicts.
- **Resilient** — locked or permission-denied files are logged and skipped
  instead of aborting the run.
- **Custom categories** — override or extend the default mapping via
  `config.json`.
- **No leftover state** — files already inside a category subfolder are
  left untouched.

## Project layout

```
Folder-Cleaner/
├── folder_cleaner.py        # CLI entry point
├── organizer.py            # Classification and move logic
├── watcher.py              # Watch mode (background thread)
├── categories.py           # Extension -> category mapping
├── paths.py                # Cross-platform folder detection
├── logger.py               # Console + file logging
├── config.json             # User configuration
└── test_folder_cleaner.py  # Unit tests (stdlib only)
```

## Installation

Clone the repository and make sure you have Python 3.8+ available. No
`pip install` is required.

```bash
git clone https://github.com/<your-username>/Folder-Cleaner.git
cd Folder-Cleaner
```

## Usage

```bash
# One pass over the target folder (manual mode)
python folder_cleaner.py

# Watch mode: keep organizing new files in the background
python folder_cleaner.py --watch

# Custom interval and config file
python folder_cleaner.py --watch --interval 30 --config my_config.json

# Print the category that an extension maps to
python folder_cleaner.py --category .PDF
```

Stop the watcher at any time with `Ctrl+C`.

## Configuration (`config.json`)

| Key                 | Description                                            | Default            |
| ------------------- | ------------------------------------------------------ | ------------------ |
| `target_folder`     | `"auto"` uses the OS Downloads folder, or absolute path | `"auto"`           |
| `auto_mode`         | Start in watch mode when launching without `--watch`  | `false`            |
| `watch_interval`    | Seconds between passes in watch mode                   | `10`               |
| `log_file`          | Path to the log file                                   | `folder_cleaner.log`    |
| `log_level`         | `DEBUG` / `INFO` / `WARNING` / `ERROR`                 | `INFO`             |
| `ignore_hidden`     | Skip files whose name starts with `.`                  | `true`             |
| `custom_categories` | `{".ext": "Category"}` overrides / extends the defaults | `{}`               |

Example with a custom mapping:

```json
{
  "target_folder": "auto",
  "auto_mode": true,
    "watch_interval": 30,
    "custom_categories": {
        ".psd": "Design",
        ".blend": "Design",
        ".fig": "Design"
    }
}
```

## Behavior

- **No overwrites.** If the destination exists, the file is renamed to
  `name (1).ext`, then `name (2).ext`, and so on.
- **Case-insensitive.** `.PDF`, `.Pdf` and `.pdf` all map to `Documents`.
- **Smart folder skipping.** Subfolders that match a known category name
  are ignored, so the tool never re-processes its own output.
- **No crashes on locked files.** Permission errors and in-use files are
  logged and the run continues.
- **Empty or missing extension** falls into `Other`.

## Running the tests

```bash
python -m unittest test_folder_cleaner.py -v
```

The test suite has no external dependencies and uses `tempfile` to
create throwaway folders.

## License

This project is released under the MIT License. See `LICENSE` for details.
