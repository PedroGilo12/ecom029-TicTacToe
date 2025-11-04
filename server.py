import socket
import threading
import time

import json

HOST = '0.0.0.0'
PORT = 5000

board = [' ' for _ in range(9)]
clients = []
symbols = ['❌', '⭕']
turn = 0
variables = {"started": False, "status": "", "symbol": "", "turn": "", "board": board}
lock = threading.Lock()
game_over = False

def print_board():
    b = board
    return f"""
 {b[0]} | {b[1]} | {b[2]}
---+---+---
 {b[3]} | {b[4]} | {b[5]}
---+---+---
 {b[6]} | {b[7]} | {b[8]}
"""

def check_winner():
    combos = [(0,1,2),(3,4,5),(6,7,8),
              (0,3,6),(1,4,7),(2,5,8),
              (0,4,8),(2,4,6)]
    for a,b,c in combos:
        if board[a] == board[b] == board[c] != ' ':
            return board[a]
    if ' ' not in board:
        return 'Empate'
    return None

def broadcast(msg):
    """Envia mensagem para todos os clientes."""
    for c in clients:
        try:
            c.sendall(msg.encode())
        except:
            pass

reiniciar_jogo = False

def handle_client(conn, symbol, player_id):
    global turn, game_over, variables
    variables["status"] = f"Você é o jogador '{symbol}'.\nAguarde o início da partida...\n"
    variables["symbol"] = symbol
    conn.sendall(json.dumps(variables).encode())

    while len(clients) < 2:
        time.sleep(0.1)

    if player_id == 0:
        with lock:
    
            variables["started"] = True
            variables["status"] = f"Partida iniciada! Vez do jogador '{symbols[turn]}'\n"
            variables["turn"] = symbols[turn]
            broadcast(json.dumps(variables))

    end_game = False
    while not end_game:
        with lock:
            winner = check_winner()
            if winner:
                end_game = True
                if winner == 'Empate' or winner == 'Draw':
                    variables["status"] = "Empate! (Q)uit"
                    broadcast(json.dumps(variables))
                else:
                    variables["status"] = f"Jogador '{winner}' venceu! (Q)uit"
                    broadcast(json.dumps(variables))
                break

            current_symbol = symbols[turn]
            current_conn = clients[turn]

    
            if conn == current_conn:
        
                try:
                    move = conn.recv(1024).decode().strip()
                except:
                    end_game = True
                    break

                if not move.isdigit() or not (1 <= int(move) <= 9):
                    continue
                move = int(move) - 1
                if board[move] != ' ':
                    continue

        
                board[move] = symbol
                turn = 1 - turn

        
                variables["board"] = board
                variables["turn"] = symbols[turn]
                variables["status"] = f"[bold yellow]Vez do jogador {variables["turn"]}[/bold yellow] — Use mouse ou Enter"
                broadcast(json.dumps(variables))

            else:
        
                try:
                    variables["board"] = board
                    variables["turn"] = symbols[turn]
                    variables["status"] = f"Vez do jogador '{symbols[turn]}'\n"
                    broadcast(json.dumps(variables))
                except:
                    pass


        time.sleep(0.05)

    time.sleep(5)
    game_over = True
    
    while True:
        global reiniciar_jogo
        with lock:
    
            if reiniciar_jogo:
                break

            try:
                move = conn.recv(1024).decode().strip()
            except:
                break

            if move == '10':
                print("Reiniciando o jogo...")
                reiniciar_jogo = True
                game_over = True
                variables = {
                    "started": False,
                    "status": "",
                    "symbol": "",
                    "turn": "",
                    "board": [' ' for _ in range(9)]
                }
                broadcast(json.dumps(variables))
                break

        time.sleep(0.05)


def start_server():
    global clients
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(2)
    print(f"Servidor iniciado em {HOST}:{PORT}")
    
    while len(clients) < 2:
        conn, addr = s.accept()
        print(f"Cliente conectado: {addr}")
        clients.append(conn)
        player_id = len(clients) - 1
        threading.Thread(target=handle_client, args=(conn, symbols[player_id], player_id), daemon=True).start()

    while not game_over:
        pass

    print("Jogo encerrado. Servidor finalizado.")

if __name__ == "__main__":
    start_server()
