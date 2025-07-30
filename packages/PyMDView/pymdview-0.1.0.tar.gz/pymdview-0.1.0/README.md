# CLI Markdown Viewer

A pure Python command line tool to display Markdown files in the terminal with rich formatting.

## Features

- Display Markdown files with syntax highlighting and formatting
- Navigate through documents with keyboard shortcuts
- Search for text within documents
- Auto-format output for the console width
- Handle console resizing
- Similar interface to the Linux 'less' command

## Installation

### From Source

1. Clone this repository:
   ```
   git clone <repository-url>
   cd CliMarkdown
   ```

2. Install the package:
   ```
   pip install -e .
   ```

## Usage

```
mdview <markdown-file>
```

### Keyboard Controls

- `j` or `Enter`: Scroll down one line
- `k`: Scroll up one line
- `Space` or `f`: Page down
- `b`: Page up
- `g`: Go to the top of the document
- `G`: Go to the bottom of the document
- `/`: Search for text (press Enter after typing search term)
- `n`: Go to the next search result
- `N`: Go to the previous search result
- `r`: Redraw the screen (useful after terminal resize)
- `q`: Quit the viewer
- `Ctrl+C`: Quit the viewer

## Dependencies

- [rich](https://github.com/Textualize/rich) - For console output with formatting
- [markdown-it-py](https://github.com/executablebooks/markdown-it-py) - For Markdown parsing

## Future Enhancements

- Support for additional markup formats
- Customizable color schemes
- Bookmarks within documents
- Table of contents navigation

- look at using - [asciidoctor-py3](https://github.com/asciidoctor/asciidoctor-py3) - For AsciiDoc support
