# ECOM029 REDES DE COMPUTADORES

Este projeto implementa um jogo da velha com interface TUI usando Python e comunicação via socket.

## Pré-requisitos

* Python 3.11 ou superior
* pip (gerenciador de pacotes do Python)

## Configuração do ambiente

1. **Criar um ambiente virtual**

No terminal, execute:

```bash
python -m venv venv
```

Isso criará uma pasta `venv` com o ambiente virtual isolado.

2. **Ativar o ambiente virtual**

* No Windows:

```bash
venv\Scripts\activate
```

* No Linux / macOS:

```bash
source venv/bin/activate
```

O prompt deve indicar que o ambiente virtual está ativo.

3. **Atualizar o pip (opcional, mas recomendado)**

```bash
python -m pip install --upgrade pip
```

4. **Instalar as dependências**

```bash
pip install -r requirements.txt
```

> Certifique-se de que exista um arquivo `requirements.txt` na raiz do projeto com todas as dependências, por exemplo:

```
textual
rich
```

## Executando o projeto

Para iniciar o jogo, execute:

```bash
python main.py
```

Se tudo estiver correto, a interface textual do jogo da velha será iniciada.

## Iniciando o servidor e o cliente

O jogo utiliza sockets para comunicação entre dois jogadores:

1. **Inicie o servidor (caso queira rodar o servidor em uma maquina separada (opcional))**:

```bash
python server.py
```

2. **Inicie os clientes** (em terminais separados ou máquinas diferentes):

```bash
python main.py
```

* Insira o IP do servidor e a porta usada.
* Aguarde os dois clientes se conectarem para iniciar a partida.

