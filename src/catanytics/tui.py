import sys
from typing import ClassVar

from rich.console import Group
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Label, RichLog

from catanytics import data, language
from catanytics.catan import Catan, Catan_Error


class Analysis_Label(Label):
    def __init__(self, tui: TUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tui = tui
        self.reload()

    def reload(self) -> None:
        lang = language.get()
        state = self.tui.catan.get_state()
        turn = self.tui.catan.get_turn()
        dice = self.tui.catan.get_dice()
        player = self.tui.catan.get_player()

        t = Text()
        t += f"Language: {lang}\n"
        t += f"State: {state.name}\n"
        t += f"Turn: {turn}\n"
        t += f"Dice: {dice}\n"

        u = Table()
        u.add_column("Player")
        u.add_column("Settlements")
        u.add_column("Robber")
        u.add_column("Production")
        for p in self.tui.catan.players:
            a = Text(f"{p} ", style="bold green" if p == player else "")
            b = str(self.tui.catan.get_settlements(p, turn))
            c = str(self.tui.catan.get_robber(p, turn))
            d = str(self.tui.catan.get_production(p, turn))
            u.add_row(a, b, c, d)

        self.update(Group(t, u))


class Hints_Label(Label):
    def __init__(self, tui: TUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tui = tui
        self.reload()

    def reload(self) -> None:
        HINTS1 = [(str(r), r.long_name()) for r in data.Resource]
        EXAMPLE = "2WWL 5L 12B" if language.get() == "en" else "2SSH 5H 12L"
        HINTS2 = [
            ("p+ PLAYER", "Add player"),
            ("p- PLAYER", "Remove player"),
            ("start", "Go to Settlement placement"),
            ("fin PLAYER", "Declare winner"),
            (f"s+ PLAYER {EXAMPLE}", "Add settlement"),
            (f"r+ PLAYER {EXAMPLE}", "Add blocked resources"),
            ("r0", "Clear blocked eesources"),
            (">", "Progress to next turn"),
            ("NUMBER", "Set result of dice roll"),
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


class History_RichLog(RichLog):
    def __init__(self, tui: TUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tui = tui


class Command_Input(Input):
    def __init__(self, tui: TUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tui = tui

    @on(Input.Submitted)
    def submitted(self) -> None:
        self.tui.new_command(self.value)


class TUI(App):
    CSS_PATH: ClassVar = "tui.tcss"
    TITLE: ClassVar = "Catanytics TUI"
    BINDINGS: ClassVar = [
        ("Ctrl+q", "quit", "Quit"),
        ("Ctrl+s", "save", "Save"),
        ("Ctrl+l", "load", "Load"),
        ("Ctrl+z", "undo", "Undo"),
        ("Ctrl+t", "lang", "Switch Language"),
    ]

    def __init__(self, catan: Catan):
        super().__init__()
        self.catan = catan

    # Actions through Bindings
    def action_save(self) -> None:
        path = "catan.json"
        self.catan.save(path)
        self.history.write(f"Saved as {path}")

    def action_load(self) -> None:
        path = "catan.json"
        self.catan = Catan.load(path)
        self.analysis.reload()
        self.history.clear()
        self.history.write(f"Loaded from {path}")

    def action_undo(self) -> None:
        self.history.write("action_undo() is not implemented!")

    def action_lang(self) -> None:
        language.cycle()
        self.analysis.reload()
        self.hints.reload()

    # Layout
    def compose(self) -> ComposeResult:
        self.analysis = Analysis_Label(self, id="analysis")
        self.hints = Hints_Label(self, id="hints")
        self.history = History_RichLog(self, id="history")
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
        try:
            self.parse_command(cmd)
        except Catan_Error as e:
            self.history.write(f"Error: {e} ('{cmd}')")
        else:
            self.command.clear()
            self.history.write(cmd)
            self.analysis.reload()

    def parse_command(self, cmd: str) -> bool:
        tokens = cmd.split(" ")
        match tokens[0]:
            case "p+":
                self.catan.add_player(tokens[1])
            case "p-":
                self.catan.remove_player(tokens[1])
            case "start":
                self.catan.start()
            case "fin":
                self.catan.finish(tokens[1])
            case "s+":
                player = tokens[1]
                data_player = data.Player.read(" ".join(tokens[2:]))
                self.catan.add_settlement(player, data_player)
            case "r+":
                player = tokens[1]
                data_player = data.Player.read(" ".join(tokens[2:]))
                self.catan.add_robber(player, data_player)
            case "r0":
                self.catan.remove_robber()
            case ">":
                self.catan.next_turn()
            case _:
                if tokens[0].isdigit():
                    self.catan.set_dice(int(tokens[0]))
                else:
                    raise Catan_Error("Command not known")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        language.set(sys.argv[1].lower())

    app = TUI(Catan())
    app.run()
