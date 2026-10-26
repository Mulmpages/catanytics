"""Terminal interface for recording a game of Catan.

Run with `python -m catanytics.tui [EN|DE]`.
"""

import sys
from datetime import datetime
from glob import glob
from typing import ClassVar

from rich.console import Group
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Label, Log

import catanytics.catan as C


class TUI_Error(Exception):
    """Raised for invalid input."""


class Analysis_Label(Label):
    """Sidebar panel with the game state and a per-player summary."""

    def __init__(self, tui: TUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tui = tui
        self.reload()

    def reload(self) -> None:
        try:
            lang = self.tui.catan.get_lang()
            state = self.tui.catan.get_state()
            turn = self.tui.catan.get_turn()
            dice = self.tui.catan.get_dice()
            player = self.tui.catan.get_player()

            t = Text()
            t += f"Language: {lang}\n"
            t += f"State: {state}\n"
            t += f"Turn: {turn}\n"
            t += f"Dice: {dice}\n"

            u = Table()
            u.add_column("Player")
            u.add_column("Settlements")
            u.add_column("Robber")
            u.add_column("Production")
            for p in self.tui.catan.get_players():
                a = Text(f"{p} ", style="bold green" if p == player else "")
                b = str(self.tui.catan.get_settlements(p, turn))
                c = str(self.tui.catan.get_robber(p, turn))
                d = str(self.tui.catan.get_production(p, turn))
                u.add_row(a, b, c, d)

            self.update(Group(t, u))
        except Exception as e:
            self.tui.history.write_line(f"Error: {e}")


class Hints_Label(Label):
    """Sidebar panel listing resource letters and commands in the current language."""

    def __init__(self, tui: TUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tui = tui
        self.reload()

    def reload(self) -> None:
        try:
            lang = self.tui.catan.get_lang()
            HINTS1 = [(r.repr(lang), r.repr_long(lang)) for r in C.Resource]
            EXAMPLE = None
            match lang:
                case C.Lang.EN:
                    EXAMPLE = "2WWL 5L 12B"
                case C.Lang.DE:
                    EXAMPLE = "2SSH 5H 12L"
                case _:
                    EXAMPLE = ""
            HINTS2 = [
                ("p+ PLAYER", "Add player"),
                ("p- PLAYER", "Remove player"),
                ("start", "Go to Settlement placement"),
                ("fin PLAYER", "Declare winner"),
                (f"s+ PLAYER {EXAMPLE}", "Add settlement"),
                (f"r+ PLAYER {EXAMPLE}", "Add blocked resources"),
                ("r0", "Clear blocked resources"),
                ("NUMBER", "Set dice roll and start the next turn"),
            ]
            t = Table(show_header=False)
            t.add_column(no_wrap=True)
            t.add_column(no_wrap=True)
            for h in HINTS1:
                t.add_row(*h)
            t.add_section()
            for h in HINTS2:
                t.add_row(*h)
            self.update(t)
        except Exception as e:
            self.tui.history.write_line(f"Error: {e}")


class History_Log(Log):
    """Log of entered commands, messages and errors."""

    def __init__(self, tui: TUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tui = tui


class Command_Input(Input):
    """Command line; passes each submitted line to `TUI.new_command()`."""

    def __init__(self, tui: TUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tui = tui

    @on(Input.Submitted)
    def submitted(self) -> None:
        self.tui.new_command(self.value)


class TUI(App):
    """Textual app that records a game in `self.catan` from typed commands."""

    CSS_PATH: ClassVar = "tui.tcss"
    TITLE: ClassVar = "Catanytics TUI"
    BINDINGS: ClassVar = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
        ("ctrl+l", "load", "Load"),
        ("ctrl+z", "undo", "Undo"),
        ("ctrl+t", "lang", "Switch Language"),
    ]

    def __init__(self, catan: C.Catan):
        super().__init__()
        self.catan = catan

    # Actions through Bindings
    def action_save(self) -> None:
        try:
            path = datetime.now().strftime(r"%Y-%m-%d_%H-%M-%S") + "_catan.json"
            self.catan.save(path)
            self.history.write_line(f"Saved as {path}")
        except Exception as e:
            self.history.write_line(f"Error: {e}")

    def action_load(self) -> None:
        try:
            path = max(glob("*_catan.json"))
            self.catan = C.Catan.load(path)
            self.analysis.reload()
            self.hints.reload()
            self.history.clear()
            self.history.write_line(f"Loaded from {path}")
        except Exception as e:
            self.history.write_line(f"Error: {e}")

    def action_undo(self) -> None:
        try:
            raise TUI_Error("Undo is not implemented")
        except Exception as e:
            self.history.write_line(f"Error: {e}")

    def action_lang(self) -> None:
        try:
            old_lang = self.catan.get_lang()
            new_lang = C.Lang.DE if old_lang == C.Lang.EN else C.Lang.EN
            self.catan.set_lang(new_lang)
            self.analysis.reload()
            self.hints.reload()
        except Exception as e:
            self.history.write_line(f"Error: {e}")

    # Layout
    def compose(self) -> ComposeResult:
        self.analysis = Analysis_Label(self, id="analysis")
        self.hints = Hints_Label(self, id="hints")
        self.history = History_Log(self, id="history")
        self.history.can_focus = False
        self.command = Command_Input(self, id="command")
        self.sidebar = Vertical(id="sidebar")
        self.sidebar.shrink = False

        yield Header(id="header")
        yield Footer(id="footer")
        with Container(id="content"):
            with self.sidebar:
                yield self.analysis
                yield self.hints
            with Vertical():
                yield self.history
                yield self.command

    # Callback Functions
    def new_command(self, cmd: str) -> None:
        """Run a command and log it; errors are logged instead of raised."""
        try:
            self.parse_command(cmd)
        except Exception as e:
            self.history.write_line(f"Error: {e} ('{cmd}')")
        else:
            self.command.clear()
            self.history.write_line(cmd)
            self.analysis.reload()

    def parse_command(self, cmd: str):
        """Apply one command to the game; the commands are listed in `Hints_Label`.

        Raises:
            Catan_Error: If the command or its arguments are invalid.
        """
        if cmd == None:
            raise TUI_Error("No command was given")
        tokens = cmd.split()
        if len(tokens) == 0:
            raise TUI_Error("No command was given")
        match tokens[0]:
            case "p+":
                if len(tokens) != 2:
                    raise TUI_Error("p+ takes exactly one argument")
                self.catan.add_player(tokens[1])
            case "p-":
                if len(tokens) != 2:
                    raise TUI_Error("p- takes exactly one argument")
                self.catan.remove_player(tokens[1])
            case "start":
                self.catan.start()
            case "fin":
                if len(tokens) != 2:
                    raise TUI_Error("fin takes exactly one argument")
                self.catan.finish(tokens[1])
            case "s+":
                if len(tokens) < 2:
                    raise TUI_Error("No player was given")
                player = tokens[1]
                resources = C.Player.read(" ".join(tokens[2:]), self.catan.get_lang())
                self.catan.add_settlement(player, resources)
            case "r+":
                if len(tokens) < 2:
                    raise TUI_Error("No player was given")
                player = tokens[1]
                resources = C.Player.read(" ".join(tokens[2:]), self.catan.get_lang())
                self.catan.add_robber(player, resources)
            case "r0":
                self.catan.remove_robber()
            case _:
                if tokens[0].isdigit():
                    dice = int(tokens[0])
                    self.catan.next_turn(dice)
                    return
                raise TUI_Error("Command not known")


if __name__ == "__main__":
    lang = C.Lang.EN
    if len(sys.argv) > 1:
        match sys.argv[1].upper():
            case "EN":
                lang = C.Lang.EN
            case "DE":
                lang = C.Lang.DE

    app = TUI(C.Catan(lang))
    app.run()
