from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Button, Input, Label
from textual.containers import Grid, Container
from textual.reactive import reactive
from textual.screen import Screen
from rich.text import Text
import socket
import threading
import json

import subprocess

variables = {"started": False, "status": "", "symbol": "", "turn": "", "board": [' ' for _ in range(9)]}
sock = None
lock = threading.Lock()

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

    def on_click(self, event):
        if hasattr(self.screen, "jogar"):
            self.screen.jogar(self.row, self.col)

    def on_key(self, event):
        if event.key == "enter":
            if hasattr(self.screen, "jogar"):
                self.screen.jogar(self.row, self.col)


class TelaInicial(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="inicio-container"):
            yield Static("Jogo da Velha\n[dim](Caio Oliveira, Pedro Giló, Matheus Pedro)[/dim]", id="titulo")
            yield Label("IP do Servidor:")
            yield Input(placeholder="localhost", id="ip_servidor")
            yield Label("Porta:")
            yield Input(placeholder="5000", id="porta_servidor")
            yield Static(id="inicio-status")
            yield Button("Iniciar Novo Jogo", id="iniciar", variant="primary")

    def on_mount(self):
        self.styles.align_horizontal = "center"
        self.styles.align_vertical = "middle"
        container = self.query_one("#inicio-container")
        container.styles.align = ("center", "middle")
        container.styles.justify = "center"
        container.styles.height = "auto"
        container.styles.width = 100
        container.styles.padding = (0, 1)
        container.styles.max_width = 50
        container.styles.border = ("round", "dimgray")
        titulo = self.query_one("#titulo")
        titulo.styles.text_align = "center"
        titulo.styles.width = "auto"
        titulo.styles.margin = (0, 0, 1, 0)
        for label in self.query(Label):
            label.styles.margin = (1, 0, 0, 0)
            label.styles.width = "100%"
        for input_widget in self.query(Input):
            input_widget.styles.width = "100%"
        status = self.query_one("#inicio-status", Static)
        status.styles.height = 3
        status.styles.text_align = "center"
        status.styles.color = "red"
        status.styles.margin_top = 1
        self.query_one(Button).styles.margin_top = 1

    def receive_messages(self, sock):
        global variables
        status = self.query_one("#inicio-status", Static)
        while True:
            try:
                msg = sock.recv(2048).decode()
                if not msg:
                    status.update("[bold red]Conexão encerrada pelo servidor.[/bold red]")
                    break
                variables = json.loads(msg)
                status.update("[bold green]" + variables["status"] + "[/bold green]")
                if variables["started"]:
                    self.app.call_from_thread(self.app.push_screen, "jogo")
                    break
            except:
                status.update("[bold red]Erro de conexão.[/bold red]")
                break

    def on_button_pressed(self, event):
        global sock
        if event.button.id == "iniciar":
            status = self.query_one("#inicio-status", Static)
            ip_input = self.query_one("#ip_servidor", Input)
            porta_input = self.query_one("#porta_servidor", Input)
            self.app.ip_servidor = ip_input.value.strip() or ip_input.placeholder
            porta_str = porta_input.value.strip() or porta_input.placeholder
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.app.ip_servidor, int(porta_str)))
                threading.Thread(target=self.receive_messages, args=(sock,), daemon=True).start()
            except ValueError:
                status.update("[bold red]Porta inválida![/bold red]")


class TelaJogo(Screen):
    jogador_atual = reactive("❌")
    terminou = reactive(False)

    def receive_messages(self, sock):
        global variables
        while True:
            try:
                msg = sock.recv(2048).decode()
                if not msg:
                    self.update_status("[bold red]Conexão encerrada pelo servidor.[/bold red]")
                    break
                variables = json.loads(msg)
                self.update_status(variables["status"])
                for i, cell in enumerate(self.query(Cell)):
                    cell.value = variables["board"][i]
                if not variables["started"]:
                    self.app.call_from_thread(self.app.push_screen, "inicio")
                    break
            except:
                self.update_status("[bold red]Erro de conexão.[/bold red]")
                break

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="jogo-container"):
            with Grid(id="tabuleiro"):
                for i in range(3):
                    for j in range(3):
                        yield Cell(i, j)
            yield Static("", id="status")

    def on_mount(self):
        global sock, variables
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
        self.status.styles.width = 30
        self.status.styles.text_align = "center"
        threading.Thread(target=self.receive_messages, args=(sock,), daemon=True).start()
        self.update_status(f"[bold yellow]Vez do jogador {variables['turn']}[/bold yellow] — Use mouse ou Enter")

    def update_status(self, msg):
        self.status.update(msg)

    def jogar(self, row, col):
        msg = f"{row*3 + col + 1}"
        with lock:
            sock.sendall(msg.encode())

    def on_key(self, event):
        key = getattr(event, "key", "")
        if not key:
            return

class JogoDaVelhaApp(App):
    SCREENS = {"inicio": TelaInicial, "jogo": TelaJogo}
    BINDINGS = [("q", "request_quit", "Sair/Voltar")]
    ip_servidor = reactive("127.0.0.1")
    porta_servidor = reactive(12345)

    def on_mount(self):
        self.push_screen("inicio")

    def action_request_quit(self):
        if self.screen.id == "inicio":
            self.exit()
        elif self.screen.id == "jogo":
            self.pop_screen()
        else:
            self.exit()


def rodar_outro():
    subprocess.run(["python", "server.py"])   

if __name__ == "__main__":
    threading.Thread(target=rodar_outro, daemon=True).start()
    JogoDaVelhaApp().run()
