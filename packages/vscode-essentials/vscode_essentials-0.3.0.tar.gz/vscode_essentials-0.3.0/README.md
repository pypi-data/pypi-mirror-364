# vscode-essentials

Essential utilities for VS Code development.

## Installation

```bash
pip install vscode-essentials
```

## Usage

```python
from vscode_essentials import hello_world

print(hello_world())
```

## Development

To install in development mode:

```bash
pip install -e .
```

## Building and Publishing

1. Install build tools:
   ```bash
   pip install build twine
   ```

2. Build the package:
   ```bash
   python -m build
   ```

3. Upload to PyPI (test first):
   ```bash
   # Test PyPI first
   twine upload --repository testpypi dist/*
   
   # Then to real PyPI
   twine upload dist/*
   ```

## License

MIT License - see LICENSE file for details.
