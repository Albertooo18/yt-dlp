# gui/window.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import sys
import time

from core.downloader import Downloader


class YTGuiApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("yt-gui (beta)")
        self.geometry("550x480")
        self.configure(bg="#282828")

        self.stop_event = threading.Event()
        self.download_thread = None

        tk.Label(self, text="URL del video:",
                 bg="#282828", fg="#ffffff",
                 font=("Arial", 12, "bold")).pack(pady=(20, 5))

        self.url_entry = tk.Entry(self, width=60, bg="#bbbbbb", fg="black")
        self.url_entry.pack(pady=5)

        # FRAME BOTONES
        btn_frame = tk.Frame(self, bg="#282828")
        btn_frame.pack(pady=10)

        self.btn_descargar = ttk.Button(btn_frame, text="Descargar Video",
                                        command=self.thread_descargar)
        self.btn_descargar.pack(pady=5, fill="x")

        self.btn_cancelar = ttk.Button(btn_frame, text="Cancelar descarga",
                                       state=tk.DISABLED,
                                       command=self.cancelar_descarga)
        self.btn_cancelar.pack(pady=5, fill="x")

        self.btn_actualizar = ttk.Button(btn_frame, text="Actualizar yt-dlp",
                                         command=self.thread_actualizar_ytdlp)
        self.btn_actualizar.pack(pady=5, fill="x")

        self.btn_salir = ttk.Button(btn_frame, text="Salir",
                                    command=self.destroy)
        self.btn_salir.pack(pady=5, fill="x")

        # ====== FRAME para la barra animada ======
        self.progress_frame = tk.Frame(self, bg="#282828", height=40)
        self.progress_frame.pack(fill="x")

        self.progress = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=450,
            mode="indeterminate"   # <--- animada
        )

        self.hide_progress()       # inicia oculta
        
        # LOGS
        self.log_box = tk.Text(self, height=12, width=70,
                            bg="#aaaaaa", fg="#282828")
        self.log_box.pack(pady=10)

    # =================== UTILIDADES ===================

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def update_progress(self, value):
        self.after(0, lambda: self.progress.config(value=value))

    def show_progress(self):
        if not self.progress.winfo_ismapped():
            self.progress.pack(pady=5)
        self.progress.start(10)   # velocidad de animación

    def hide_progress(self):
        self.progress.stop()
        for widget in self.progress_frame.winfo_children():
            widget.pack_forget()

    # =================== DESCARGA ===================

    def descargar_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Debes ingresar una URL.")
            return

        # Estado inicial
        self.stop_event.clear()
        self.show_progress()      # mostrar barra animada

        self.log("Iniciando descarga...")

        self.btn_cancelar.config(state=tk.NORMAL)
        self.btn_descargar.config(state=tk.DISABLED)

        downloader = Downloader(
            update_progress=lambda _: None,   # YA NO USAMOS PORCENTAJE
            log=self.log,
            stop_event=self.stop_event,
            show_progress=lambda: None        # YA NO LA MOSTRAMOS DESDE EL HOOK
        )

        try:
            downloader.download(url)
            if not self.stop_event.is_set():
                self.log("Descarga completada")
                messagebox.showinfo("Listo", "Video descargado correctamente")

        except Exception as e:
            if "cancelada" in str(e).lower():
                self.log("Descarga cancelada por el usuario.")
            else:
                self.log(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Falló la descarga:\n{e}")

        finally:
            # 👉 AQUÍ VA LO IMPORTANTE 👇
            self.hide_progress()               # detener animación y ocultar barra
            
            self.btn_cancelar.config(state=tk.DISABLED)
            self.btn_descargar.config(state=tk.NORMAL)


    def thread_descargar(self):
        if self.download_thread and self.download_thread.is_alive():
            return
        self.download_thread = threading.Thread(
            target=self.descargar_video,
            daemon=True
        )
        self.download_thread.start()

    # =================== CANCELAR ===================

    def cancelar_descarga(self):
        if self.download_thread and self.download_thread.is_alive():
            self.stop_event.set()
            self.log("Cancelando descarga...")

    # =================== ACTUALIZAR ===================

    def actualizar_ytdlp(self):
        self.log("Actualizando yt-dlp...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
            messagebox.showinfo("Actualizado", "yt-dlp actualizado correctamente")
        except Exception as e:
            self.log(f"Error al actualizar: {e}")

    def thread_actualizar_ytdlp(self):
        threading.Thread(target=self.actualizar_ytdlp, daemon=True).start()
