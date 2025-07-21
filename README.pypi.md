# 🔀 file-ext-sorter

A fast and flexible CLI tool to sort files into folders based on file extensions.

Organize messy download folders, group media by type, or archive project files — all with a single command.


<p align="center">
  <img src="https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/blob/main/assets/project-showcase.png?raw=true" alt="Project showcase image" width="700">
</p>

[![PyPI version](https://img.shields.io/pypi/v/file-ext-sorter)](https://pypi.org/project/file-ext-sorter/)
[![License](https://img.shields.io/github/license/oleksandr-romashko/goit-pythonweb-hw-04)](https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/blob/main/LICENSE)

---

## 📦 Installation

**Requires**: Python 3.8+
**Depends on**: aiofiles, aioshutil, colorama, tomli

Tested on Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 (beta).


Install globally using `pip`:

```bash
pip install file-ext-sorter
```

## 🚀 Usage

Run the CLI tool from anywhere on your system:

```bash
file-ext-sorter /path/to/source /path/to/output
```

It will:

1. Scan the source folder for all files (recursively)
2. Group them into subfolders based on their extensions (e.g., `.jpg`, `.mp4`, `.zip`, `.etc`.)
3. Move or copy them into the target folder

## 💡 Example

Command:

```bash
file-ext-sorter ./downloads ./sorted
```

Creates `sorted` folder with following files structure:

```bash
sorted/
├── pdf/
│   └── report.pdf
├── jpg/
│   └── image.jpg
├── zip/
│   └── archive.zip
```

## ❌ Uninstall

To remove the tool from your system:

```bash
pip uninstall file-ext-sorter
```

## 🐛 Report Issues

Found a bug or want to request a feature?

Please visit the [GitHub Issues page](https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/issues).

## ⚖️ License

This project is licensed under the [MIT License](https://github.com/oleksandr-romashko/goit-pythonweb-hw-04/blob/main/LICENSE).

## 🙏 Acknowledgements

Special thanks to the following open-source libraries:

* [aiopath](https://pypi.org/project/aiopath/)
* [aioshutil](https://pypi.org/project/aioshutil/)
* [colorama](https://pypi.org/project/colorama/)
