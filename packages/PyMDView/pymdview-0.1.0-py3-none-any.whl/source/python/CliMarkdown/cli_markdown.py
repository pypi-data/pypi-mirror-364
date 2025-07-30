#!/usr/bin/env python3
"""
CLI Markdown Viewer - A command line tool to display Markdown files
"""

__VERSION__ = "0.1.0"
__AUTHOR__ = "Matt Lowe <marl.scot.1@googlemail.com"
__DESCRIPTION__ = "A command line tool to display Markdown files"
__LICENSE__ = "MIT License"
__PYTHON_REQUIRES__ = ">=3.6"

import os
import sys
import argparse
from typing import List, Optional, Tuple

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from markdown_it import MarkdownIt
except ImportError:
    print("Required packages not found. Please install with:")
    print("pip install rich markdown-it-py")
    sys.exit(1)

class MarkdownViewer:
    """
    A class to display and navigate through markdown files in the terminal.
    """
    def __init__(self, file_path: str):
        """
        Initialize the MarkdownViewer with a markdown file.

        Args:
            file_path: Path to the markdown file to display
        """
        self.file_path = file_path
        # Initialize console with explicit color system to ensure ANSI codes work properly
        self.console = Console(color_system="auto")
        self.terminal_width = self.console.width
        self.terminal_height = self.console.height

        # Content management
        self.content = self._load_content()
        self.rendered_lines = self._render_content()
        self.current_line = 0
        self.search_term = None
        self.search_results = []
        self.current_search_idx = -1

    def _load_content(self) -> str:
        """Load the markdown file content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

    def _render_content(self) -> List[str]:
        """Render the markdown content to rich text and split into lines."""
        # Create a new console with no color system override
        # This ensures ANSI escape codes are generated properly
        render_console = Console(color_system="auto", width=self.terminal_width, no_color=True)

        md = Markdown(self.content)
        with render_console.capture() as capture:
            render_console.print(md)

        rendered_text = capture.get()
        # Split the text into lines and remove any trailing empty lines
        lines = rendered_text.split('\n')
        return lines

    def redraw(self) -> None:
        """Redraw the content based on current terminal size."""
        # Store the current relative position (percentage through the document)
        if len(self.rendered_lines) > 0:
            relative_position = self.current_line / len(self.rendered_lines)
        else:
            relative_position = 0

        # Update terminal dimensions
        self.terminal_width = self.console.width
        self.terminal_height = self.console.height

        # Re-render content with new dimensions
        self.rendered_lines = self._render_content()

        # Restore the relative position
        if len(self.rendered_lines) > 0:
            self.current_line = int(relative_position * len(self.rendered_lines))
            # Ensure we don't go past the end of the document
            max_start_line = max(0, len(self.rendered_lines) - (self.terminal_height - 4))
            self.current_line = min(self.current_line, max_start_line)

        self.display_current_page()

    def display_current_page(self) -> None:
        """Display the current page of content."""
        # First move cursor to top-left corner
        print("\033[H", end="")
        sys.stdout.flush()
        # Then print a newline and carriage return to ensure we're at the beginning of a fresh line
        print("\r", end="")
        sys.stdout.flush()
        # Finally clear from cursor to end of screen
        print("\033[J", end="")
        sys.stdout.flush()  # Ensure the escape sequences are processed immediately

        # Check if terminal width has changed
        current_width = self.console.width
        current_height = self.console.height
        if current_width != self.terminal_width or current_height != self.terminal_height:
            # Store the current relative position (percentage through the document)
            if len(self.rendered_lines) > 0:
                relative_position = self.current_line / len(self.rendered_lines)
            else:
                relative_position = 0

            self.terminal_width = current_width
            self.terminal_height = current_height

            # Re-render content with new dimensions
            self.rendered_lines = self._render_content()

            # Restore the relative position
            if len(self.rendered_lines) > 0:
                self.current_line = int(relative_position * len(self.rendered_lines))
                # Ensure we don't go past the end of the document
                max_start_line = max(0, len(self.rendered_lines) - (self.terminal_height - 4))
                self.current_line = min(self.current_line, max_start_line)

        display_height = self.terminal_height - 4  # Reserve space for status line and reduce height by 2 lines
        end_line = min(self.current_line + display_height, len(self.rendered_lines))

        # Display content lines
        for line in self.rendered_lines[self.current_line:end_line]:
            # Use print instead of console.print to avoid potential issues with ANSI sequences
            print(line)

        # Display status line
        status = f"File: {self.file_path} | Line: {self.current_line+1}-{end_line} of {len(self.rendered_lines)} | ({self.terminal_width},{self.terminal_height})"
        if self.search_term:
            status += f" | Search: '{self.search_term}' ({self.current_search_idx+1}/{len(self.search_results)})" if self.search_results else f" | Search: '{self.search_term}' (No results)"

        # Use simple ASCII dash instead of Unicode character to avoid potential display issues
        print("-" * self.terminal_width)
        print(status)

    def scroll_down(self, lines: int = 1) -> None:
        """Scroll down by the specified number of lines."""
        max_start_line = max(0, len(self.rendered_lines) - (self.terminal_height - 4))
        self.current_line = min(self.current_line + lines, max_start_line)
        self.display_current_page()

    def scroll_up(self, lines: int = 1) -> None:
        """Scroll up by the specified number of lines."""
        self.current_line = max(0, self.current_line - lines)
        self.display_current_page()

    def page_down(self) -> None:
        """Scroll down by one page."""
        self.scroll_down(self.terminal_height - 5)

    def page_up(self) -> None:
        """Scroll up by one page."""
        self.scroll_up(self.terminal_height - 5)

    def search(self, term: str) -> None:
        """
        Search for a term in the rendered content.

        Args:
            term: The search term to look for
        """
        self.search_term = term
        self.search_results = []

        for i, line in enumerate(self.rendered_lines):
            if term.lower() in line.lower():
                self.search_results.append(i)

        if self.search_results:
            self.current_search_idx = 0
            self.goto_search_result()
        else:
            self.display_current_page()

    def goto_search_result(self) -> None:
        """Go to the current search result."""
        if not self.search_results:
            return

        self.current_line = self.search_results[self.current_search_idx]
        self.display_current_page()

    def next_search_result(self) -> None:
        """Go to the next search result."""
        if not self.search_results:
            return

        self.current_search_idx = (self.current_search_idx + 1) % len(self.search_results)
        self.goto_search_result()

    def prev_search_result(self) -> None:
        """Go to the previous search result."""
        if not self.search_results:
            return

        self.current_search_idx = (self.current_search_idx - 1) % len(self.search_results)
        self.goto_search_result()

    def run(self) -> None:
        """Run the interactive viewer."""
        import termios
        import tty
        import signal

        def handle_resize(signum, frame):
            self.redraw()

        # Set up signal handler for terminal resize
        signal.signal(signal.SIGWINCH, handle_resize)

        self.display_current_page()

        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            # Set terminal to raw mode
            tty.setraw(fd)

            while True:
                key = sys.stdin.read(1)

                if key == 'q':  # Quit
                    break
                elif key == 'j' or key == '\n':  # Scroll down
                    self.scroll_down()
                elif key == 'k':  # Scroll up
                    self.scroll_up()
                elif key == ' ' or key == 'f':  # Page down
                    self.page_down()
                elif key == 'b':  # Page up
                    self.page_up()
                elif key == 'g':  # Go to top
                    self.current_line = 0
                    self.display_current_page()
                elif key == 'G':  # Go to bottom
                    self.current_line = max(0, len(self.rendered_lines) - (self.terminal_height - 2))
                    self.display_current_page()
                elif key == '/':  # Search
                    # Restore terminal settings temporarily
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

                    # Display prompt and get search term
                    # First move cursor to top-left corner
                    print("\033[H", end="")
                    sys.stdout.flush()
                    # Then print a newline and carriage return to ensure we're at the beginning of a fresh line
                    print("\r", end="")
                    sys.stdout.flush()
                    # Finally clear from cursor to end of screen
                    print("\033[J", end="")
                    sys.stdout.flush()  # Ensure the escape sequences are processed immediately
                    search_term = input("Search: ")

                    # Set terminal back to raw mode
                    tty.setraw(fd)

                    if search_term:
                        self.search(search_term)
                elif key == 'n':  # Next search result
                    self.next_search_result()
                elif key == 'N':  # Previous search result
                    self.prev_search_result()
                elif key == 'r':  # Redraw
                    self.redraw()
                elif key == '\x03':  # Ctrl+C
                    break

        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # First move cursor to top-left corner
            print("\033[H", end="")
            sys.stdout.flush()
            # Then print a newline and carriage return to ensure we're at the beginning of a fresh line
            print("\r", end="")
            sys.stdout.flush()
            # Finally clear from cursor to end of screen
            print("\033[J", end="")
            sys.stdout.flush()  # Ensure the escape sequences are processed immediately

def display_keyboard_controls():
    """Display the keyboard navigation controls."""
    print("Keyboard Controls:")
    print("  j or Enter: Scroll down one line")
    print("  k: Scroll up one line")
    print("  Space or f: Page down")
    print("  b: Page up")
    print("  g: Go to the top of the document")
    print("  G: Go to the bottom of the document")
    print("  /: Search for text (press Enter after typing search term)")
    print("  n: Go to the next search result")
    print("  N: Go to the previous search result")
    print("  r: Redraw the screen (useful after terminal resize)")
    print("  q: Quit the viewer")
    print("  Ctrl+C: Quit the viewer")

def main():
    """Main entry point for the CLI markdown viewer."""
    parser = argparse.ArgumentParser(description='Display and navigate Markdown files in the terminal.')
    parser.add_argument('file', nargs='?', help='Path to the markdown file to display')
    parser.add_argument('-v', '--version', action='version', version=f'CLI Markdown Viewer {__VERSION__}')
    parser.add_argument('-k', '--keys', action='store_true', help='Display keyboard navigation controls')
    args = parser.parse_args()

    if args.keys:
        display_keyboard_controls()
        sys.exit(0)

    if not args.file:
        parser.print_help()
        sys.exit(0)

    viewer = MarkdownViewer(args.file)
    viewer.run()

if __name__ == '__main__':
    main()
