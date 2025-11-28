# gui/window.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import sys

from core.downloader import Downloader, get_formats


class YTGuiApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("yt-gui (beta)")
        self.geometry("680x650")
        self.configure(bg="#282828")

        self.stop_event = threading.Event()
        self.download_thread = None

        # ---------------- URL ----------------
        tk.Label(
            self, text="URL del video:",
            bg="#282828", fg="white",
            font=("Arial", 14, "bold")
        ).pack(pady=(15, 5))

        self.url_entry = tk.Entry(self, width=70, bg="#bbbbbb", fg="black")
        self.url_entry.pack(pady=5)
        self.url_entry.bind("<KeyRelease>", lambda e: self.actualizar_formatos())

        # ---------------- Checkbox Solo Audio ----------------
        self.solo_audio = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self, text="Solo audio (mostrar solo formatos de audio)",
            variable=self.solo_audio,
            command=self.actualizar_formatos,
            bg="#282828", fg="white",
            activebackground="#282828",
            activeforeground="white",
            selectcolor="#282828"
        ).pack()

        # ---------------- Lista de Formatos ----------------
        tk.Label(self, text="Formatos disponibles:",
                 bg="#282828", fg="white", font=("Arial", 12)).pack(pady=(5, 3))

        self.lista_formatos = tk.Listbox(self, height=12, width=85, bg="#bbbbbb")
        self.lista_formatos.pack(pady=5)

        # ---------------- FRAME BOTONES ----------------
        frame = tk.Frame(self, bg="#282828")
        frame.pack(pady=10)

        self.btn_descargar = ttk.Button(frame, text="Descargar Selección",
                                        command=self.thread_descargar)
        self.btn_descargar.pack(pady=5, fill="x")

        self.btn_cancelar = ttk.Button(
            frame, text="Cancelar descarga",
            state=tk.DISABLED,
            command=self.cancelar_descarga
        )
        self.btn_cancelar.pack(pady=5, fill="x")

        self.btn_actualizar = ttk.Button(
            frame, text="Actualizar yt-dlp",
            command=self.thread_actualizar_ytdlp
        )
        self.btn_actualizar.pack(pady=5, fill="x")

        self.btn_salir = ttk.Button(frame, text="Salir", command=self.destroy)
        self.btn_salir.pack(pady=5, fill="x")

        # ---------------- Barra animada ----------------
        self.progress_frame = tk.Frame(self, bg="#282828", height=40)
        self.progress_frame.pack(fill="x")

        self.progress = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=520,
            mode="indeterminate"
        )
        self.hide_progress()

        # ---------------- LOGS ----------------
        self.log_box = tk.Text(self, height=12, width=90,
                               bg="#aaaaaa", fg="#202020")
        self.log_box.pack(pady=10)

    # ========================================================
    # UTILIDADES
    # ========================================================

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def show_progress(self):
        if not self.progress.winfo_ismapped():
            self.progress.pack(pady=5)
        self.progress.start(10)

    def hide_progress(self):
        self.progress.stop()
        for w in self.progress_frame.winfo_children():
            w.pack_forget()

    # ========================================================
    # CARGAR FORMATOS
    # ========================================================

    def actualizar_formatos(self):
        url = self.url_entry.get().strip()

        if not url:
            self.lista_formatos.delete(0, tk.END)
            return

        try:
            formatos = get_formats(url)
        except:
            self.lista_formatos.delete(0, tk.END)
            return

        self.lista_formatos.delete(0, tk.END)

        mostrar_audio = self.solo_audio.get()

        for f in formatos:
            ext = f.get("ext")
            res = f.get("resolution")
            abr = f.get("abr")
            fid = f.get("format_id")

            is_audio = f.get("acodec") != "none" and f.get("vcodec") == "none"
            is_video = f.get("vcodec") != "none"

            if mostrar_audio:
                if is_audio:
                    abr_show = f"{abr} kbps" if abr else "unknown"
                    self.lista_formatos.insert(
                        tk.END,
                        f"{fid} | AUDIO | {abr_show} | {ext}"
                    )
            else:
                if is_video:
                    res_show = res if res else "unknown"
                    self.lista_formatos.insert(
                        tk.END,
                        f"{fid} | VIDEO | {res_show} | {ext}"
                    )

    # ========================================================
    # DESCARGA
    # ========================================================

    def descargar_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Debes ingresar una URL.")
            return

        sel = self.lista_formatos.curselection()
        if not sel:
            messagebox.showerror("Error", "Selecciona un formato de la lista.")
            return

        formato = self.lista_formatos.get(sel[0]).split("|")[0].strip()

        self.stop_event.clear()
        self.show_progress()

        self.log(f"Descargando formato {formato}...")

        opts = {
            "format": formato,
            "outtmpl": "%(title)s.%(ext)s"
        }

        try:
            import yt_dlp
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            self.log("Descarga completada.")
            messagebox.showinfo("Listo", "Descarga terminada.")

        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))

        finally:
            self.hide_progress()

    def thread_descargar(self):
        threading.Thread(target=self.descargar_video, daemon=True).start()

    # ========================================================
    # CANCELAR DESCARGA
    # ========================================================

    def cancelar_descarga(self):
        self.stop_event.set()
        self.log("Cancelando descarga...")

    # ========================================================
    # ACTUALIZAR YT-DLP
    # ========================================================

    def actualizar_ytdlp(self):
        self.log("Actualizando yt-dlp...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"]
            )
            messagebox.showinfo("Actualizado", "yt-dlp se actualizó correctamente.")
        except Exception as e:
            self.log(f"Error: {e}")

    def thread_actualizar_ytdlp(self):
        threading.Thread(target=self.actualizar_ytdlp, daemon=True).start()
