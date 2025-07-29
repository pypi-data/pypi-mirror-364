# 🔀 file-ext-sorter

[![PyPI version](https://img.shields.io/pypi/v/file-ext-sorter)](https://pypi.org/project/file-ext-sorter/)
[![Python versions](https://img.shields.io/pypi/pyversions/file-ext-sorter)](https://pypi.org/project/file-ext-sorter/)
[![License](https://img.shields.io/pypi/l/file-ext-sorter)](https://pypi.org/project/file-ext-sorter/)

A command-line tool that groups files into folders based on their file extensions.

Organize messy download folders, group media by type, quickly analyze and find files by type or archive project files — all with a single command.

#### Main Features

- 🔀 **Automatic file grouping** by file extensions:
    - 🗐 Handles duplicate names and naming conflicts
    - 👁️‍🗨️ Supports dry-run mode for safe preview
- 🚀 **Asynchronous performance**
- 🎒 **Minimal and portable**: no databases, no external frameworks
- 🐍 **Compatible with Python 3.8-3.14+**
- 📦 **PyPI**: install globally and use as a CLI command

<p align="center">
  <img src="https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/blob/main/assets/project-showcase.png?raw=true" alt="Project showcase image" width="700">
</p>

---

## 📦 Installation

**Requires**: Python 3.8+  
**Dependencies**: `aiofiles`, `aioshutil`, `colorama`, `tomli`

Install from PyPI:

```bash
pip install file-ext-sorter
```

## 🚀 Usage

```bash
file-ext-sorter <source_dir> <output_dir> [--dry-run] [--debug]
```

Optional flags:
* `--dry-run`: show what would be done without actually copying files
* `--debug`: verbose debug output

It will:

1. Scan the source folder for all files (recursively).
2. Group them into subfolders based on their extensions (e.g., `.jpg`, `.mp4`, `.zip`, `.etc`.)
3. Copy them into subfolders within the output directory, grouped by extension.

> **Note**: This tool **copies** files by default to preserve the original source directory. No files are deleted or moved.

## 💡 Example

Source folder files state:

```bash
source/
├── image.png
├── doc.txt
├── archive.zip
└── video.mp4
```

Use `file-ext-sorter` tool:

```bash
file-ext-sorter ./source ./output
```

After running file-ext-sorter:

```bash
output/
├── png/
│   └── image.png
├── txt/
│   └── doc.txt
├── zip/
│   └── archive.zip
└── mp4/
    └── video.mp4
```

### 🆘 Command Help

Run this to see available options:

```bash
file-ext-sorter --help
```

<details> <summary>Click to expand help output</summary>

```bash
 
🔀 FILE SORTER

Sort and organize your files by extension

v0.1.0

This CLI tool scans a source directory and copies files into subfolders in the output directory based on file extensions.

Notes on terminology:
  duplicate - file with the same file name and content (skipped from copying)
  conflict - file with the same file name and different content (resolved by new name)

Usage:    file-ext-sorter <source> <output>
Example:  file-ext-sorter ./path/to/source/folder ./path/to/output/folder

Positional arguments:
  source  folder to scan and sort files from (should exist)
  output  folder to sort files into (may not exist)

Options:
  -h, --help  show this help message and exit
  --dry-run   preview the scan and sort result without copying any files.
  --debug     enable debug logging to console
  --version   show the version number and exit
```
</details> 

## ❌ Uninstall

To remove the tool from your system:

```bash
pip uninstall file-ext-sorter
```

### 📷 App Screenshots

**1. Help menu** (`--help`)

![help menu screenshot](https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/raw/main/assets/results/example-usage-help.png)

**2. Run on sample files**

![normal run screenshot](https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/raw/main/assets/results/example-usage-test-files.png)

**3. Dry-run mode** (preview the scan and sort result without actual files copying)

![dry-run screenshot](https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/raw/main/assets/results/example-usage-test-files-dry-run.png)

## 🐛 Report Issues

Found a bug or want to request a feature?

Please visit the [GitHub Issues page](https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/issues).

## 💡 Contributing

Ideas, bugs, or feature requests? Pull requests are welcome!
For major changes, please open an issue first to discuss what you'd like to change.

## ⚖️ License

MIT — see [LICENSE](https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/blob/main/LICENSE).

## 🙏 Acknowledgements

Special thanks to the following open-source libraries:

* [aiopath](https://pypi.org/project/aiopath/)
* [aioshutil](https://pypi.org/project/aioshutil/)
* [colorama](https://pypi.org/project/colorama/)
