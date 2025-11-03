from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Button
from textual.containers import Grid, Container
from textual.reactive import reactive
from textual.screen import Screen
from rich.text import Text


class Cell(Static):
    value = reactive(" ")

    def __init__(self, row, col):
        super().__init__(" ", id=f"cell-{row}-{col}")
        self.row = row
        self.col = col
        self.can_focus = True

    def render(self):
        color = "bright_white"
        if self.value == "❌":
            color = "bright_red"
        elif self.value == "⭕":
            color = "bright_blue"
        texto = self.value.center(3, " ") if self.value.strip() else "   "
        return Text(texto, style=f"bold {color}", justify="center")

    def on_click(self, event) -> None:
        if hasattr(self.screen, "jogar"):
            self.screen.jogar(self.row, self.col)

    def on_key(self, event) -> None:
        if event.key == "enter":
            if hasattr(self.screen, "jogar"):
                self.screen.jogar(self.row, self.col)


class TelaInicial(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="inicio-container"):
            yield Static("Jogo da Velha\n[dim](Textual Edition)[/dim]", id="titulo")
            yield Button("Iniciar Novo Jogo", id="iniciar", variant="primary")

    def on_mount(self) -> None:
        container = self.query_one("#inicio-container")
        container.styles.align = ("center", "middle")
        container.styles.justify = "center"
        container.styles.height = "100%"
        container.styles.width = "100%"
        container.styles.padding = (0, 1)

        titulo = self.query_one("#titulo")
        titulo.styles.text_align = "center"
        titulo.styles.width = "auto" # <-- CORRIGIDO
        titulo.styles.margin = (0, 0, 1, 0)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "iniciar":
            self.app.push_screen("jogo")


class TelaJogo(Screen):
    jogador_atual = reactive("❌")
    terminou = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="jogo-container"):
            with Grid(id="tabuleiro"):
                for i in range(3):
                    for j in range(3):
                        yield Cell(i, j)
            yield Static("", id="status")

    def on_mount(self) -> None:
        jogo_container = self.query_one("#jogo-container")
        jogo_container.styles.align = ("center", "middle")
        jogo_container.styles.justify = "center"
        jogo_container.styles.height = "100%"
        jogo_container.styles.width = "100%"

        grid = self.query_one("#tabuleiro")
        grid.styles.width = 30
        grid.styles.height = 15
        grid.styles.grid_size_rows = 3
        grid.styles.grid_size_columns = 3
        grid.styles.gap = 0
        grid.styles.border = ("round", "ansi_bright_cyan")
        grid.styles.background = "black"

        for cell in self.query(Cell):
            cell.styles.border = ("solid", "gray")

        self.status = self.query_one("#status", Static)
        self.status.styles.margin = (1, 0, 0, 0)
        self.status.styles.width = 30 # <-- CORRIGIDO
        self.status.styles.text_align = "center"
        self.update_status(f"[bold yellow]Vez do jogador {self.jogador_atual}[/bold yellow] — Use mouse ou Enter")

    def update_status(self, msg: str) -> None:
        self.status.update(msg)

    def jogar(self, row: int, col: int) -> None:
        if self.terminou:
            return
        cell = self.query_one(f"#cell-{row}-{col}", Cell)
        if cell.value != " ":
            return
        cell.value = self.jogador_atual

        vencedor = self.verificar_vencedor()
        if vencedor:
            self.terminou = True
            self.destacar_vitoria(vencedor)
            self.update_status(f"🎉 [bold green]Jogador {vencedor} venceu![/bold green] (R)einiciar (Q)uit")
            return
        elif all(c.value != " " for c in self.query(Cell)):
            self.terminou = True
            self.update_status("😐 Empate! (R)einiciar (Q)uit")
            return

        self.jogador_atual = "⭕" if self.jogador_atual == "❌" else "❌"
        self.update_status(f"[bold yellow]Vez do jogador {self.jogador_atual}[/bold yellow] — Use mouse ou Enter")

    def verificar_vencedor(self):
        t = [[self.query_one(f"#cell-{i}-{j}", Cell).value for j in range(3)] for i in range(3)]
        for i in range(3):
            if t[i][0] != " " and t[i][0] == t[i][1] == t[i][2]:
                return t[i][0]
        for j in range(3):
            if t[0][j] != " " and t[0][j] == t[1][j] == t[2][j]:
                return t[0][j]
        if t[0][0] != " " and t[0][0] == t[1][1] == t[2][2]:
            return t[0][0]
        if t[0][2] != " " and t[0][2] == t[1][1] == t[2][0]:
            return t[0][2]
        return None

    def destacar_vitoria(self, vencedor: str) -> None:
        t = [[self.query_one(f"#cell-{i}-{j}", Cell).value for j in range(3)] for i in range(3)]
        linhas = (
            [(i, 0, i, 1, i, 2) for i in range(3)]
            + [(0, j, 1, j, 2, j) for j in range(3)]
            + [(0, 0, 1, 1, 2, 2), (0, 2, 1, 1, 2, 0)]
        )
        for coords in linhas:
            a = [t[coords[k]][coords[k + 1]] for k in range(0, 6, 2)]
            if a.count(vencedor) == 3:
                for k in range(0, 6, 2):
                    c = self.query_one(f"#cell-{coords[k]}-{coords[k + 1]}", Cell)
                    c.styles.border = ("round", "green")

    def on_key(self, event) -> None:
        key = getattr(event, "key", "")
        if not key:
            return
        if key.lower() == "r":
            self.reiniciar()

    def reiniciar(self) -> None:
        for cell in self.query(Cell):
            cell.value = " "
            cell.styles.border = ("solid", "gray")
        self.jogador_atual = "❌"
        self.terminou = False
        self.update_status(f"[bold yellow]Novo jogo iniciado![/bold yellow] — Use mouse ou Enter")


class JogoDaVelhaApp(App):
    SCREENS = {
        "inicio": TelaInicial,
        "jogo": TelaJogo,
    }
    BINDINGS = [
        ("q", "request_quit", "Sair/Voltar"),
    ]

    def on_mount(self) -> None:
        self.push_screen("inicio")

    def action_request_quit(self) -> None:
        if self.screen.id == "inicio": # Corrigido de _default para inicio
             self.exit()
        elif self.screen.id == "jogo":
             self.pop_screen()
        else:
             self.exit()


if __name__ == "__main__":
    JogoDaVelhaApp().run()

