# crow

[![License](https://img.shields.io/github/license/shaperones0/crow)](https://img.shields.io/github/license/shaperones0/crow)

Page delivery engine with Hot-Reloading.

Dynamic notes/documentation/wiki project management system with live-editing capabilities
and automatic rebuild functionality. Designed for programmers who need just the baseline.

- **GitHub repository**: <https://github.com/shaperones0/crow/>
- **Documentation** *Coming Soon*

## Overview

This project provides a nano-engine for managing HTML content with real-time editing support. It automatically detects changes in project structure or individual files and efficiently rebuilds only what's necessary. The system includes:

- Project structure monitoring
- Automatic rebuild triggers
- Live content rendering

Also check out booknest (Coming Soon!) for fully fledged note-taking framework.

## Features

- 🔄 **Automatic Rebuilding**: Detects file changes and rebuilds only affected components
- ⚡ **Live Updates**: Query rendered content with built-in change detection
- 🧩 **Renderer Agnostic**: Works with any compliant rendering engine
- 📁 **Project Structure Tracking**: Monitors file system changes using hash-based detection
- ⏱️ **Efficient Rendering**: Only re-renders modified pages
- 📊 **Metadata Management**: Tracks page information and modification timestamps

## Installation

```bash
pip install git+https://github.com/shaperones0/crow.git
```

*Requirements: Python 3.8+*

## Usage

### Basic Setup
```python
from pathlib import Path
from crow import LiveProject, BaseRenderer

class MyRenderer(BaseRenderer):
    def build(self, pages):
        # Setup logic, table of contents, search index, etc.

    def render(self, source, page):
        # Rendering logic
        return rendered_html

# Setup live project
project = LiveProject(
    root_path=Path("src"),
    build_path=Path("build"),
    renderer=MyRenderer()
)

# Query pages later in your app (e.g. Flask)
@app.route('/p/<string:title')
def page(title: str):
    content = project.get_rendered_content(title)
    if content is None:
        return 'Not found :(', 404
    return content
```

### Getting Rendered Content
```python
content = project.get_rendered_content("homepage")
# Every page available to the project was rendered and saved
```

### CLI Usage (Example) (Not implemented yet :/)
```bash
python -m crow --root src --build-dir build
```

### Production usage

This engine should **NEVER** be used with:
1) untrusted source content (generally bad)
2) live source editing from large number of people (frequent
changes will result in frequent rendering of whole project structure)

Recommended use cases:
* maintaining personal note vault / wiki / documentation, with <3 editors
* generating static websites from said notes

## Configuration

The `LiveProject` accepts these main parameters:
- `root_path`: Source directory for files you write
- `build_path`: Output directory for rendered content
- `renderer`: Custom rendering implementation
- `glob`: File pattern for source discovery (default: `**/*.html`)
- `output_extension`: Output file extension (default: `html`)

## Contributing

This project is powered by [uv](https://docs.astral.sh/uv/). Make sure it's installed.

```bash
git clone https://github.com/shaperones0/crow.git
cd crow
make install
```
See other commands in `Makefile` for more.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements

- [Natural Sorting](https://github.com/SethMMorton/natsort) for intuitive file ordering
- Python's `pathlib` for cross-platform path management
