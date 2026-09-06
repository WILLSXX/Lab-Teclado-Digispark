import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
from collections import Counter
import subprocess
import json
import re
import time

BASE = Path(r"C:\LabKeylogger")
EVENTS = BASE / "eventos.txt"
REPORT = BASE / "relatorio.txt"
BASE.mkdir(parents=True, exist_ok=True)

pressed = {}
counts = Counter()
events_total = 0
shortcuts_total = 0
text_interp = ""

shift_down = False
ctrl_down = False
alt_down = False


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log(line):
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def refresh():
    active_var.set(f"Teclas pressionadas: {len(pressed)}")
    event_var.set(f"Eventos: {events_total}")
    shortcut_var.set(f"Atalhos: {shortcuts_total}")
    char_var.set(f"Caracteres: {len(text_interp)}")


def show_event(kind, detail):
    table.insert("", "end", values=(now(), kind, detail))
    table.yview_moveto(1)


def key_name(ev):
    names = {
        "Shift_L":"SHIFT_L", "Shift_R":"SHIFT_R",
        "Control_L":"CTRL", "Control_R":"CTRL",
        "Alt_L":"ALT", "Alt_R":"ALT",
        "Meta_L":"WIN_L", "Meta_R":"WIN_R",
        "BackSpace":"BACKSPACE", "Return":"ENTER",
        "space":"SPACE", "Tab":"TAB", "Caps_Lock":"CAPS_LOCK",
        "Up":"UP", "Down":"DOWN", "Left":"LEFT", "Right":"RIGHT",
        "Escape":"ESC"
    }
    if ev.keysym in names:
        return names[ev.keysym]
    if ev.char and ev.char.isprintable():
        return ev.char
    return ev.keysym


def classify(k):
    if k in {"SHIFT_L","SHIFT_R","CTRL","ALT","WIN_L","WIN_R"}:
        return "MODIFICADOR"
    if k in {"BACKSPACE","ENTER","SPACE","TAB","CAPS_LOCK","UP","DOWN","LEFT","RIGHT","ESC"}:
        return "ESPECIAL"
    if len(k) == 1:
        return "CARACTERE"
    return "ESPECIAL"


def sync_text():
    global text_interp
    text_interp = test_box.get("1.0", "end-1c")
    interpreted_var.set(text_interp.replace("\n", " ↵ "))
    refresh()


def schedule_sync():
    root.after_idle(sync_text)


def detect_shortcut(ev, k):
    global shortcuts_total
    if k in {"SHIFT_L","SHIFT_R","CTRL","ALT","WIN_L","WIN_R"}:
        return
    mods = []
    if ctrl_down:
        mods.append("CTRL")
    if alt_down:
        mods.append("ALT")
    if not mods:
        return
    if shift_down:
        mods.append("SHIFT")
    base = ev.keysym.upper()
    combo = "+".join(mods + [base])
    shortcuts_total += 1
    log(f"[{now()}] ATALHO | {combo}")
    show_event("ATALHO", combo)
    refresh()


def on_down(ev):
    global shift_down, ctrl_down, alt_down, events_total
    if ev.keysym in {"Shift_L","Shift_R"}:
        shift_down = True
    elif ev.keysym in {"Control_L","Control_R"}:
        ctrl_down = True
    elif ev.keysym in {"Alt_L","Alt_R"}:
        alt_down = True
    k = key_name(ev)
    pressed[ev.keysym] = time.perf_counter()
    counts[k] += 1
    events_total += 1
    cat = classify(k)
    log(f"[{now()}] KEY_DOWN | {cat} | {k}")
    show_event("KEY_DOWN", f"{cat} → {k}")
    detect_shortcut(ev, k)
    schedule_sync()
    status_var.set(f"DOWN → {cat} → {k}")
    refresh()


def on_up(ev):
    global shift_down, ctrl_down, alt_down
    k = key_name(ev)
    cat = classify(k)
    start = pressed.pop(ev.keysym, None)
    if start is not None:
        ms = (time.perf_counter() - start) * 1000
        log(f"[{now()}] KEY_UP | {cat} | {k} | duracao={ms:.1f} ms")
        show_event("KEY_UP", f"{cat} → {k} ({ms:.1f} ms)")
        status_var.set(f"UP → {cat} → {k} | {ms:.1f} ms")
    else:
        log(f"[{now()}] KEY_UP | {cat} | {k}")
        show_event("KEY_UP", f"{cat} → {k}")
    if ev.keysym in {"Shift_L","Shift_R"}:
        shift_down = False
    elif ev.keysym in {"Control_L","Control_R"}:
        ctrl_down = False
    elif ev.keysym in {"Alt_L","Alt_R"}:
        alt_down = False
    schedule_sync()
    refresh()


def clear_lab():
    global events_total, shortcuts_total, text_interp
    global shift_down, ctrl_down, alt_down
    if not messagebox.askyesno("Confirmar", "Limpar o laboratorio?"):
        return
    events_total = 0
    shortcuts_total = 0
    text_interp = ""
    shift_down = ctrl_down = alt_down = False
    pressed.clear()
    counts.clear()
    table.delete(*table.get_children())
    test_box.delete("1.0", "end")
    interpreted_var.set("")
    EVENTS.write_text("", encoding="utf-8")
    refresh()
    status_var.set("Laboratorio limpo.")
    test_box.focus_set()


def stats():
    w = tk.Toplevel(root)
    w.title("Estatisticas")
    w.geometry("520x520")
    t = tk.Text(w, font=("Consolas", 10))
    t.pack(fill="both", expand=True, padx=12, pady=12)
    t.insert("end", f"Eventos: {events_total}\n")
    t.insert("end", f"Atalhos: {shortcuts_total}\n")
    t.insert("end", f"Caracteres: {len(text_interp)}\n\n")
    t.insert("end", "TECLAS MAIS UTILIZADAS\n")
    t.insert("end", "-" * 40 + "\n")
    for k, v in counts.most_common():
        t.insert("end", f"{k:<20} {v}\n")
    t.config(state="disabled")


def report():
    lines = [
        "=" * 60,
        "RELATORIO DO LABORATORIO DE EVENTOS DE TECLADO",
        "=" * 60,
        "",
        f"Gerado em: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"Eventos: {events_total}",
        f"Atalhos: {shortcuts_total}",
        f"Caracteres: {len(text_interp)}",
        "",
        "TECLAS MAIS UTILIZADAS",
        "-" * 40,
    ]
    lines += [f"{k:<20} {v}" for k, v in counts.most_common()]
    lines += ["", "TEXTO INTERPRETADO", "-" * 40, text_interp]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    messagebox.showinfo("Relatorio", f"Criado em:\n{REPORT}")


def hid_devices():
    cmd = ("Get-PnpDevice -PresentOnly | Where-Object {$_.Class -match 'HID|Keyboard'} | "
           "Select-Object Status,Class,FriendlyName,InstanceId | ConvertTo-Json -Compress")
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=10)
        if r.returncode != 0 or not r.stdout.strip():
            return []
        data = json.loads(r.stdout)
        return data if isinstance(data, list) else [data]
    except Exception:
        return []


def show_hid():
    w = tk.Toplevel(root)
    w.title("Dispositivos HID / Teclados")
    w.geometry("1150x500")
    cols = ("status", "class", "name", "vid", "pid", "instance")
    tv = ttk.Treeview(w, columns=cols, show="headings")
    labels = {"status":"Status", "class":"Classe", "name":"Nome", "vid":"VID", "pid":"PID", "instance":"Instance ID"}
    widths = {"status":70, "class":130, "name":350, "vid":70, "pid":70, "instance":430}
    for c in cols:
        tv.heading(c, text=labels[c])
        tv.column(c, width=widths[c])
    for item in hid_devices():
        iid = item.get("InstanceId", "")
        mv = re.search(r"VID_([0-9A-Fa-f]{4})", iid)
        mp = re.search(r"PID_([0-9A-Fa-f]{4})", iid)
        vid = mv.group(1).upper() if mv else ""
        pid = mp.group(1).upper() if mp else ""
        tv.insert("", "end", values=(item.get("Status", ""), item.get("Class", ""), item.get("FriendlyName", ""), vid, pid, iid))
    tv.pack(fill="both", expand=True, padx=10, pady=10)
    tk.Label(w, text="Seu Digispark em modo HID foi identificado como VID 16C0 / PID 27DB / DigiKey.").pack(pady=5)

root = tk.Tk()
root.title("Laboratorio de Eventos de Teclado")
root.geometry("1200x830")

tk.Label(root, text="LABORATORIO DE EVENTOS DE TECLADO", font=("Arial", 18, "bold")).pack(pady=10)
tk.Label(root, text="A captura e limitada aos eventos da Area de teste desta janela.", font=("Arial", 10)).pack()

f1 = ttk.LabelFrame(root, text="Area de teste")
f1.pack(fill="x", padx=15, pady=10)
test_box = tk.Text(f1, height=4, font=("Consolas", 14), wrap="word")
test_box.pack(fill="x", padx=10, pady=10)

f2 = ttk.LabelFrame(root, text="Texto interpretado pelo laboratorio")
f2.pack(fill="x", padx=15, pady=10)
interpreted_var = tk.StringVar()
out = tk.Entry(f2, textvariable=interpreted_var, state="readonly", font=("Consolas", 14))
out.pack(fill="x", padx=10, pady=10)

f3 = ttk.LabelFrame(root, text="Eventos em tempo real")
f3.pack(fill="both", expand=True, padx=15, pady=10)
table = ttk.Treeview(f3, columns=("time", "type", "event"), show="headings")
table.heading("time", text="Horario")
table.heading("type", text="Tipo")
table.heading("event", text="Evento")
table.column("time", width=205)
table.column("type", width=130)
table.column("event", width=730)
scroll = ttk.Scrollbar(f3, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scroll.set)
table.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")

f4 = tk.Frame(root)
f4.pack(fill="x", padx=15, pady=5)
active_var = tk.StringVar(value="Teclas pressionadas: 0")
event_var = tk.StringVar(value="Eventos: 0")
shortcut_var = tk.StringVar(value="Atalhos: 0")
char_var = tk.StringVar(value="Caracteres: 0")
for v in (active_var, event_var, shortcut_var, char_var):
    tk.Label(f4, textvariable=v, font=("Consolas", 10)).pack(side="left", padx=18)

f5 = tk.Frame(root)
f5.pack(pady=10)
for label, cmd in (("Estatisticas", stats), ("Dispositivos HID", show_hid), ("Gerar relatorio", report), ("Limpar", clear_lab), ("Fechar", root.destroy)):
    tk.Button(f5, text=label, command=cmd, width=16).pack(side="left", padx=5)

status_var = tk.StringVar(value="Aguardando tecla...")
tk.Label(root, textvariable=status_var, font=("Consolas", 10)).pack(pady=5)

test_box.bind("<KeyPress>", on_down, add="+")
test_box.bind("<KeyRelease>", on_up, add="+")
test_box.focus_set()
EVENTS.touch()
root.mainloop()
