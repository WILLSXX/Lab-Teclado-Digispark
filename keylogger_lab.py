import tkinter as tk
from pathlib import Path
from datetime import datetime

PASTA = Path(r"C:\LabKeylogger")
LOG = PASTA / "eventos.txt"

PASTA.mkdir(parents=True, exist_ok=True)


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def gravar(tipo, detalhe):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{agora()}] {tipo}: {detalhe}\n")


def key_down(event):
    if event.keysym == "Shift_L":
        detalhe = "SHIFT_L"
    elif event.keysym == "Shift_R":
        detalhe = "SHIFT_R"
    elif event.keysym == "BackSpace":
        detalhe = "BACKSPACE"
    elif event.keysym == "Return":
        detalhe = "ENTER"
    elif event.keysym == "space":
        detalhe = "SPACE"
    else:
        detalhe = repr(event.char) if event.char else event.keysym

    gravar("KEY_DOWN", detalhe)
    status.set(f"KEY_DOWN → {detalhe}")


def key_up(event):
    if event.keysym == "Shift_L":
        detalhe = "SHIFT_L"
    elif event.keysym == "Shift_R":
        detalhe = "SHIFT_R"
    elif event.keysym == "BackSpace":
        detalhe = "BACKSPACE"
    elif event.keysym == "Return":
        detalhe = "ENTER"
    elif event.keysym == "space":
        detalhe = "SPACE"
    else:
        detalhe = repr(event.char) if event.char else event.keysym

    gravar("KEY_UP", detalhe)
    status.set(f"KEY_UP → {detalhe}")


def limpar_log():
    LOG.write_text("", encoding="utf-8")
    status.set("Log limpo.")


janela = tk.Tk()
janela.title("Laboratório de Eventos de Teclado")
janela.geometry("800x450")

titulo = tk.Label(
    janela,
    text="LABORATÓRIO — EVENTOS DE TECLADO",
    font=("Arial", 16, "bold")
)
titulo.pack(pady=15)

orientacao = tk.Label(
    janela,
    text="Digite somente nesta caixa para testar os eventos.",
    font=("Arial", 11)
)
orientacao.pack(pady=5)

entrada = tk.Text(
    janela,
    width=80,
    height=15,
    font=("Consolas", 12)
)
entrada.pack(padx=20, pady=10)

status = tk.StringVar(value="Aguardando tecla...")
status_label = tk.Label(
    janela,
    textvariable=status,
    font=("Consolas", 10)
)
status_label.pack(pady=5)

botao = tk.Button(
    janela,
    text="Limpar log",
    command=limpar_log
)
botao.pack(pady=5)

entrada.bind("<KeyPress>", key_down)
entrada.bind("<KeyRelease>", key_up)

entrada.focus_set()

janela.mainloop()