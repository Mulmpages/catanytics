from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Label, RichLog

from catanytics.catan import Catan, Data_Player

class CommandInput(Input):
    def __init__(self, catan : Catan, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.catan = catan

    def key_enter(self) -> None:
        if self.parse(self.value):
            self.clear()

    def parse(self, cmd : str) -> bool:
        tokens = " ".split(cmd)
        match tokens[0]:
            case "p+": return self.catan.add_player(tokens[1])
            case "p-": return self.catan.remove_player(tokens[1])
            case "start": return self.catan.start()
            case "finish": return self.catan.finish()
            case "s": 
                player = tokens[1]
                data_player = sum([Data_Player.from_token(t) for t in tokens[2:]])
                return self.catan.add_settlement(player, data_player)
            case "r":
                player = tokens[1]
                data_player = sum([Data_Player.from_token(t) for t in tokens[2:]])
                return self.catan.set_robber(data_player)
            case "r0": return self.catan.remove_robber()
            case _: pass
        self.value = ""


class TUI(App):
    CSS_PATH = "tui.tcss"
    TITLE = "Catanytics TUI"
    BINDINGS = [
        ("Ctrl+q", "quit", "Quit"),
        ("Ctrl+z", "undo", "Undo"),
        ("Ctrl+s", "save", "Save"),
        ("Ctrl+l", "load", "Load")
    ]

    def __init__(self, catan):
        super().__init__()
        self.catan = catan

    def action_save(self) -> None:
        self.history.write("action_save() is not implemented!")

    def action_load(self) -> None:
        self.history.write("action_load() is not implemented!")

    def action_undo(self) -> None:
        self.history.write("action_undo() is not implemented!")

    def compose(self) -> ComposeResult:
        self.analysis = Label(id="analysis")
        self.hints = Label(id="hints")
        self.history = RichLog(id="history")
        self.history.can_focus = False
        self.input = CommandInput(self.catan, id="input")

        yield Header(id="header")
        yield Footer(id="footer")
        with Container(id="content"):
            with Vertical(id="sidebar"):
                yield self.analysis
                yield self.hints
            with Vertical():
                yield self.history
                yield self.input


if __name__ == "__main__":
    app = TUI(Catan())
    app.run()