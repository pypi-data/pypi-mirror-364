# Streamlit Crepe Documentation

Rich markdown editor component for Streamlit applications, powered by Milkdown Crepe.

## Overview

Streamlit Crepe provides a WYSIWYG markdown editor with:
- 📝 Rich text editing with live preview
- 🧮 LaTeX mathematical formulas
- 💻 Code blocks with syntax highlighting
- 📊 Interactive table editing
- 🖼️ Image upload with automatic compression
- 🔗 Smart link editing

## Installation

```bash
pip install streamlit-crepe
```

## Quick Start

```python
import streamlit as st
from streamlit_crepe import st_milkdown

# Basic editor
content = st_milkdown("# Hello World")
st.markdown(content)
```

## API Reference

### `st_milkdown()`

```python
st_milkdown(
    default_value: str = "",
    height: Optional[int] = None,
    min_height: int = 400,
    placeholder: str = "",
    readonly: bool = False,
    features: Optional[Dict[str, bool]] = None,
    throttle_delay: int = 250,
    key: Optional[str] = None
) -> str
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `default_value` | `str` | `""` | Initial markdown content |
| `height` | `int` | `None` | Fixed height in pixels (auto if None) |
| `min_height` | `int` | `400` | Minimum height in pixels (auto mode only) |
| `placeholder` | `str` | `""` | Placeholder text |
| `readonly` | `bool` | `False` | Read-only mode |
| `features` | `dict` | See below | Feature configuration |
| `throttle_delay` | `int` | `250` | Update delay in milliseconds |
| `key` | `str` | `None` | Unique component key |

#### Default Features

```python
{
    "codeblock": True,   # Code blocks
    "math": True,        # LaTeX formulas
    "table": True,       # Interactive tables
    "image": True,       # Image uploads
    "link": True         # Link editing
}
```

## Examples

### Basic Usage (Auto Height)

```python
content = st_milkdown(
    default_value="# My Document\n\nStart writing...",
    min_height=300,  # Minimum height in auto mode
    key="editor"
)
```

### Fixed Height

```python
content = st_milkdown(
    default_value="# My Document\n\nStart writing...",
    height=400,  # Fixed height overrides min_height
    key="editor"
)
```

### Height Behavior

- **Auto height** (default): Editor adjusts to content size, respects `min_height`
- **Fixed height**: Editor has fixed size, `min_height` is ignored
- Use auto height for dynamic content, fixed height for consistent layouts

### Math Editor

```python
content = st_milkdown(
    default_value="""# Math Document

Inline: $E = mc^2$

Block:
$$\\int_0^1 x^2 dx = \\frac{1}{3}$$
""",
    features={"math": True, "codeblock": False, "table": False, "image": False, "link": True}
)
```

### Code Editor

```python
content = st_milkdown(
    default_value="""# Code Documentation

```python
def hello():
    print("Hello, World!")
```
""",
    features={"codeblock": True, "math": False, "table": False, "image": False, "link": True}
)
```

### Multiple Editors

```python
col1, col2 = st.columns(2)

with col1:
    notes = st_milkdown("# Notes", key="notes")

with col2:
    docs = st_milkdown("# Documentation", key="docs")
```

## Image Handling

Images are automatically:
- Compressed to max 800px width/height
- Reduced to max 500KB file size
- Embedded as base64 in markdown
- Processed asynchronously (non-blocking)

## Performance Tips

1. **Disable unused features**:
   ```python
   features = {"codeblock": True, "math": False, "table": False, "image": False, "link": True}
   ```

2. **Adjust throttle for large docs**:
   ```python
   st_milkdown(content, throttle_delay=500)
   ```

3. **Use unique keys**:
   ```python
   editor1 = st_milkdown(content1, key="editor1")
   editor2 = st_milkdown(content2, key="editor2")
   ```

## Troubleshooting

### Editor Not Showing
1. Build frontend: `python build_frontend.py`
2. Check browser console for errors
3. Restart Streamlit

### Content Not Updating
1. Use unique `key` for each editor
2. Lower `throttle_delay` if needed
3. Check for JavaScript errors

### Image Issues
1. Check file size (will compress to 500KB)
2. Use supported formats: PNG, JPEG, GIF, WebP
3. Check browser console for errors

## Development

### Build Frontend
```bash
python build_frontend.py
```

### Run Tests
```bash
cd tests
python run_tests.py
```

## Migration from 0.0.x

**Removed**:
- `theme` parameter (use CSS instead)
- `toolbar` parameter (features control UI)
- `image_upload_mode` (always base64)
- `on_image_upload` (automatic compression)

**Updated**:
- `features` simplified to 5 core features
- `throttle_delay` default: 500ms → 250ms

```python
# Old
st_milkdown(theme="dark", toolbar={"bold": True})

# New
st_milkdown(features={"codeblock": True, "math": True})
```