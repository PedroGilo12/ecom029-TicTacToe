import socket
import threading
import time

HOST = '0.0.0.0'
PORT = 5000

board = [' ' for _ in range(9)]
clients = []
symbols = ['X', 'O']
turn = 0
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

def handle_client(conn, symbol, player_id):
    global turn, game_over
    conn.sendall(f"Você é o jogador '{symbol}'. Aguarde o início da partida...\n".encode())

    # Espera os dois conectarem (com pequeno sleep para evitar busy-wait)
    while len(clients) < 2:
        time.sleep(0.1)

    # Envia o estado inicial do tabuleiro apenas uma vez (pelo jogador 0)
    if player_id == 0:
        with lock:
            broadcast(f"\n{print_board()}\nVez do jogador '{symbols[turn]}'\n")

    # Loop principal do jogo
    while not game_over:
        with lock:
            winner = check_winner()
            if winner:
                game_over = True
                if winner == 'Empate' or winner == 'Draw':
                    broadcast(f"\n{print_board()}\nEmpate!\n")
                else:
                    broadcast(f"\n{print_board()}\nJogador '{winner}' venceu!\n")
                break

            current_symbol = symbols[turn]
            current_conn = clients[turn]

            # Somente o thread do jogador atual deve solicitar a jogada
            if conn == current_conn:
                # Envia apenas ao jogador atual que é a sua vez
                conn.sendall("É seu turno. Digite uma posição (1-9): ".encode())
                try:
                    move = conn.recv(1024).decode().strip()
                except:
                    game_over = True
                    break

                if not move.isdigit() or not (1 <= int(move) <= 9):
                    conn.sendall("Movimento inválido. Use 1-9.\n".encode())
                    continue

                move = int(move) - 1
                if board[move] != ' ':
                    conn.sendall("Posição já ocupada.\n".encode())
                    continue

                # Atualiza o tabuleiro e troca o turno
                board[move] = symbol
                turn = 1 - turn

                # Após a jogada, notifica todos os clientes UMA VEZ com o novo tabuleiro
                broadcast(f"\n{print_board()}\nVez do jogador '{symbols[turn]}'\n")

            else:
                # Se não for a vez deste cliente, envia apenas uma mensagem leve e espera
                try:
                    conn.sendall(f"Aguarde sua vez. É a vez do jogador '{current_symbol}'.\n".encode())
                except:
                    pass

        # Pequeno sono fora do lock para reduzir uso de CPU
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

    # Mantém o servidor ativo até o jogo terminar
    while not game_over:
        pass

    print("Jogo encerrado. Servidor finalizado.")

if __name__ == "__main__":
    start_server()
