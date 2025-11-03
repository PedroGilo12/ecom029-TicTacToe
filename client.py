import socket
import threading
import sys

SERVER = input("Digite o IP do servidor: ")
PORT = 5000

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(2048).decode()
            if not msg:
                print("Conexão encerrada pelo servidor.")
                break
            print(msg)
        except:
            print("Erro de conexão.")
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        try:
            msg = input()
            sock.sendall(msg.encode())
        except KeyboardInterrupt:
            print("\nSaindo do jogo...")
            sock.close()
            sys.exit()

if __name__ == "__main__":
    main()
