from typing import Any, List, Optional

import click
from rich.align import Align
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class BaseSelect:
    """Base class for select components with shared functionality."""

    def __init__(
        self,
        options: List[str] = [],
        title: str = "",
        color: str = "bold magenta",
        align: str = "left",
        selection: str = "→",
        highlight: str = "green",
    ):
        self.options = options
        self.index = 0
        self.title = title
        self.color = color
        self.align = align
        self.selection = selection
        self.highlight = highlight

    def _get_click(self) -> Optional[str]:
        match click.getchar():
            case "\r":
                return "enter"
            case "\x1b[B" | "s" | "S" | "àP":
                return "down"
            case "\x1b[A" | "w" | "W" | "àH":
                return "up"
            case "\x1b[D" | "a" | "A" | "àK":
                return "left"
            case "\x1b[C" | "d" | "D" | "àM":
                return "right"
            case "\x1b":
                return "exit"
            case _:
                return None

    def _set_index(self, key: str) -> None:
        if key == "down":
            self.index += 1
        elif key == "up":
            self.index -= 1

        if self.index > len(self.options) - 1:
            self.index = 0
        elif self.index < 0:
            self.index = len(self.options) - 1

    def _clear(self) -> None:
        for _ in range(len(self.options) + 5):
            print("\x1b[A\x1b[K", end="")

    @property
    def _usage_info(self) -> Text:
        """Return usage information text for the select menu."""
        return Text("Use ↑/↓ to navigate, ENTER to submit", "dim")

    @property
    def _layout(self) -> Group:
        """Generate the display group for the menu.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _layout")

    @property
    def _panel_width(self) -> int:
        """Return the width of the panel."""
        # Calculate minimum width needed for the usage text
        usage_width = len(self._usage_info.plain) + 2
        # Get the max width of options
        options_width = (
            max((len(option) for option in self.options), default=0) + 5
        )  # +5 for marker and spacing
        # Use the larger of the two widths, plus some padding
        return max(usage_width, options_width) + 4

    def prompt(self) -> Any:
        """Display the menu and handle user input.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement prompt")


class Select(BaseSelect):
    def __init__(
        self,
        options: List[str] = [],
        start_index: int = 0,
        title: str = "",
        color: str = "bold magenta",
        align: str = "left",
        selection: str = "→",
        highlight: str = "green",
    ):
        super().__init__(
            options=options,
            title=title,
            color=color,
            align=align,
            selection=selection,
            highlight=highlight,
        )
        self.index = start_index

    @property
    def _layout(self) -> Group:
        menu = Text(justify="left")

        selected = Text(self.selection + " ", self.highlight)
        not_selected = Text(" " * (len(self.selection) + 1))

        for idx, option in enumerate(self.options):
            if idx == self.index:
                menu.append(
                    Text.assemble(selected, Text(option + "\n", self.highlight))
                )
            else:
                menu.append(Text.assemble(not_selected, option + "\n"))

        menu.rstrip()

        menu = Panel(menu, padding=1, width=self._panel_width)
        menu.title = Text(self.title, self.color)
        menu.subtitle = self._usage_info

        return Group(Align(menu, self.align))

    def prompt(self) -> str:
        with Live(self._layout, auto_refresh=False, screen=False) as live:
            live.update(self._layout, refresh=True)
            while True:
                try:
                    key = self._get_click()
                    if key == "enter":
                        break
                    elif key == "exit":
                        exit()

                    self._set_index(key)
                    live.update(self._layout, refresh=True)
                except (KeyboardInterrupt, EOFError):
                    exit()

        self._clear()

        return self.options[self.index]


class MultiSelect(BaseSelect):
    def __init__(
        self,
        options: List[str] = [],
        start_indices: Optional[List[int]] = None,
        title: str = "",
        color: str = "bold magenta",
        align: str = "left",
        selection: str = "→",
        highlight: str = "green",
        selected_marker: str = "●",
        unselected_marker: str = "○",
    ):
        super().__init__(
            options=options,
            title=title,
            color=color,
            align=align,
            selection=selection,
            highlight=highlight,
        )
        self.selected_indices = start_indices or []
        self.selected_marker = selected_marker
        self.unselected_marker = unselected_marker

    def _get_click(self) -> Optional[str]:
        # Override to add space key handling
        match click.getchar():
            case "\r":
                return "enter"
            case "\x1b[B" | "s" | "S" | "àP":
                return "down"
            case "\x1b[A" | "w" | "W" | "àH":
                return "up"
            case "\x1b[D" | "a" | "A" | "àK":
                return "left"
            case "\x1b[C" | "d" | "D" | "àM":
                return "right"
            case " ":
                return "space"
            case "\x1b":
                return "exit"
            case _:
                return None

    def _toggle_selection(self) -> None:
        if self.index in self.selected_indices:
            self.selected_indices.remove(self.index)
        else:
            self.selected_indices.append(self.index)

    @property
    def _usage_info(self) -> Text:
        """Return usage information text for the multi-select menu."""
        return Text("Use ↑/↓ to navigate, SPACE to toggle, ENTER to submit", "dim")

    @property
    def _layout(self) -> Group:
        menu = Text(justify="left")

        cursor_selected = Text(self.selection + " ", self.highlight)
        cursor_not_selected = Text(" " * (len(self.selection) + 1))

        for idx, option in enumerate(self.options):
            # Determine if this option is selected
            marker = (
                self.selected_marker
                if idx in self.selected_indices
                else self.unselected_marker
            )

            # Determine if cursor is on this item
            if idx == self.index:
                menu.append(
                    Text.assemble(
                        cursor_selected, Text(f"{marker} {option}\n", self.highlight)
                    )
                )
            else:
                menu.append(Text.assemble(cursor_not_selected, f"{marker} {option}\n"))

        menu.rstrip()

        menu = Panel(menu, padding=1, width=self._panel_width)
        menu.title = Text(self.title, self.color)
        menu.subtitle = self._usage_info

        return Group(Align(menu, self.align))

    def prompt(self) -> List[str]:
        with Live(self._layout, auto_refresh=False, screen=False) as live:
            live.update(self._layout, refresh=True)
            while True:
                try:
                    key = self._get_click()
                    if key == "enter":
                        break
                    elif key == "exit":
                        exit()
                    elif key == "space":
                        self._toggle_selection()
                        live.update(self._layout, refresh=True)
                    else:
                        self._set_index(key)
                        live.update(self._layout, refresh=True)
                except (KeyboardInterrupt, EOFError):
                    exit()

        self._clear()

        # Return the selected options
        return [self.options[i] for i in self.selected_indices]
