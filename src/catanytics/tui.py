from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Label, RichLog

from catanytics.catan import Catan, Data_Player, Resource


class CommandInput(Input):
    def __init__(self, catan : Catan):
        super().__init__()
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

                return self.catan.add_settlement(*args)
            case "r": return self.catan.add_settlement(*args)
            else: 

    @staticmethod
    def token_to_resource(token : str) -> Resource:
        match token[0]:
            case "W": return Resource()WOOL
            case "G": return Resource()GRAIN
            case "L": return Resource()LUMBER
            case "B": return Resource()BRICK
            case "O": return Resource()ORE
        dice = token[1]


class TUI(App):
    CSS_PATH = "tui.tcss"
    TITLE = "Catanytics TUI"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("Ctrl+z", "undo", "Undo"),
        ("Ctrl+s", "save", "Save"),
        ("Ctrl+l", "load", "Load")
    ]

    def __init__(self, catan):
        super().__init__()
        self.catan = catan

    def action_save(self) -> None:
        pass

    def action_load(self) -> None:
        pass

    def action_undo(self) -> None:
        pass



    

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        yield Footer(id="footer")
        with Container(id="content"):
            with Vertical(id="sidebar"):
                yield Label(id="analysis")
                yield Label(id="hints")
            with Vertical():
                myRichLog = RichLog(id="history")
                myRichLog.can_focus = False
                yield myRichLog
                yield Input(id="input")


if __name__ == "__main__":
    app = TUI(Catan())
    app.run()