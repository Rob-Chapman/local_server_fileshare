#!/usr/bin/env python3
import http.server, os, socket, sys, threading, tkinter as tk
from tkinter import filedialog

DEFAULT_PORT, PORT_SCAN = 8000, 25           # change if you like

# ── helpers ──────────────────────────────────────────────────────
def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(("8.8.8.8", 80)); return s.getsockname()[0]
    finally: s.close()

def make_handler(kind, file_name=""):
    if kind == "file":
        class OneFile(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path.strip("/") != file_name:
                    self.send_error(404); return
                return super().do_GET()
            def log_message(self,*_): pass
        return OneFile
    else:
        class QuietDir(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*_): pass
        return QuietDir

def bind_server(port, Handler):
    try: return http.server.ThreadingHTTPServer(("", port), Handler)
    except OSError as e:
        if e.errno in (98, 10048): return None
        raise

# ── GUI setup ───────────────────────────────────────────────────
root = tk.Tk()
root.title("Share Hub")
url_var = tk.StringVar(value="Nothing shared yet")

tk.Label(root, textvariable=url_var, justify="left", padx=12, pady=10).pack()

btn_frame = tk.Frame(root); btn_frame.pack(pady=(0,10))
tk.Button(btn_frame, text="File…",   width=10).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Folder…", width=10).grid(row=0, column=1, padx=5)
stop_btn = tk.Button(btn_frame, text="Stop",     width=10, state="disabled")
stop_btn.grid(row=0, column=2, padx=5)

server = None                                   # current HTTP server
ip = lan_ip()

def start_share(kind):
    global server
    path = (filedialog.askopenfilename if kind=="file"
            else filedialog.askdirectory)(title=f"Select {kind}")
    if not path: return

    # stop old server if running
    if server: server.shutdown()

    # handler + serve dir
    if kind == "file":
        serve_dir, name = os.path.split(path); os.chdir(serve_dir)
    else:
        os.chdir(path);        name = ""

    Handler = make_handler(kind, name)

    # find free port
    svr = None
    for p in range(DEFAULT_PORT, DEFAULT_PORT+PORT_SCAN):
        svr = bind_server(p, Handler)
        if svr: break
    if not svr:
        url_var.set("No free port 8000-8025"); return

    threading.Thread(target=svr.serve_forever, daemon=True).start()
    url = f"http://{ip}:{p}/" + (name if kind=="file" else "")
    root.clipboard_clear(); root.clipboard_append(url)
    url_var.set(f"Sharing ({kind}):\n{url}")
    stop_btn.config(state="normal")
    globals()["server"] = svr                     # store for stop()

def stop_share():
    global server
    if server:
        server.shutdown(); server = None
    url_var.set("Stopped. Nothing shared.")
    stop_btn.config(state="disabled")

# wire buttons
btn_frame.children["!button"].config(command=lambda: start_share("file"))
btn_frame.children["!button2"].config(command=lambda: start_share("dir"))
stop_btn.config(command=stop_share)
root.protocol("WM_DELETE_WINDOW", lambda: (stop_share(), root.destroy()))

root.mainloop()
