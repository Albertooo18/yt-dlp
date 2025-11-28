import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import yt_dlp
import time

class YTGuiApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Control de barra suavizada
        self.last_update_time = 0
        self.max_percent = 0

        # ---------------- Ventana ----------------
        self.title("yt-gui (beta)")
        self.geometry("550x480")
        self.minsize(550, 480)
        self.configure(bg="#282828")

        # ---------------- URL ----------------
        tk.Label(self, text="URL del video:",
                 bg="#282828", fg="#ffffff",
                 font=("Arial", 12, "bold")).pack(pady=(20, 5))

        self.url_entry = tk.Entry(self, width=60, bg="#bbbbbb", fg="black")
        self.url_entry.pack(pady=5)

        # ---------------- Botones en un Frame ----------------
        btn_frame = tk.Frame(self, bg="#282828")
        btn_frame.pack(pady=10)

        self.btn_descargar = ttk.Button(btn_frame, text="Descargar Video",
                                        command=self.thread_descargar)
        self.btn_descargar.pack(pady=5, fill="x")

        self.btn_cancelar = ttk.Button(btn_frame, text="Cancelar descarga",
                                       command=self.cancelar_descarga,
                                       state=tk.DISABLED)
        self.btn_cancelar.pack(pady=5, fill="x")

        self.btn_actualizar = ttk.Button(btn_frame, text="Actualizar yt-dlp",
                                         command=self.thread_actualizar_ytdlp)
        self.btn_actualizar.pack(pady=5, fill="x")

        self.btn_salir = ttk.Button(btn_frame, text="Salir", command=self.destroy)
        self.btn_salir.pack(pady=5, fill="x")

        # ---------------- Barra de progreso ----------------
        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=450, mode="determinate")
        self.progress["maximum"] = 100
        self.progress["value"] = 0
        self.progress.pack(pady=15)
        self.progress.config(value=0)
        self.update_idletasks()


        # ---------------- Log ----------------
        self.log_box = tk.Text(self, height=12, width=70,
                               bg="#aaaaaa", fg="#282828")
        self.log_box.pack(pady=10)

        # ---------------- Estado de hilos ----------------
        self.stop_event = threading.Event()
        self.download_thread = None

    # ========== Utilidad de log ==========  
    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    # ========== Hook de progreso suavizado ==========  
    def hook(self, d):
        if self.stop_event.is_set():
            raise Exception("Descarga cancelada por el usuario")

        if d.get("status") != "downloading":
            return

        now = time.time()

        # Primer update SIEMPRE permitido
        # Primera actualización SIEMPRE
        if self.last_update_time != 0:
            if (now - self.last_update_time) < 2:
                return

        self.last_update_time = now

        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        dl = d.get("downloaded_bytes") or 0

        if total:
            percent = (dl / total) * 100

            # Evitar retrocesos
            if percent > self.max_percent:
                self.max_percent = percent

            percent = self.max_percent

            self.after(0, lambda val=percent: self.progress.config(value=val))

            txt = f"{round(dl/1024/1024, 2)} / {round(total/1024/1024, 2)} MB"
        else:
            txt = f"{round(dl/1024/1024, 2)} MB / ? MB"

        self.after(0, lambda t=txt: self.log(t))

    # ========== Descarga ==========  
    def descargar_video(self):
        self.progress.config(value=0)
        self.max_percent = 0
        self.last_update_time = 0
        self.update_idletasks()

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Debes ingresar una URL.")
            return

        # Reset REAL de progreso
        self.stop_event.clear()
        self.max_percent = 0
        self.last_update_time = 0
        self.progress.config(value=0)

        self.log("Iniciando descarga...")

        self.btn_cancelar.config(state=tk.NORMAL)
        self.btn_descargar.config(state=tk.DISABLED)

        opts = {
            "format": "mp4",
            "outtmpl": "%(title)s.%(ext)s",
            "progress_hooks": [self.hook],
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

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
            self.btn_cancelar.config(state=tk.DISABLED)
            self.btn_descargar.config(state=tk.NORMAL)

            # Reset al finalizar
            self.max_percent = 0
            self.last_update_time = 0
            self.progress.config(value=0)

    # Hilo para descarga  
    def thread_descargar(self):
        if self.download_thread and self.download_thread.is_alive():
            return
        self.download_thread = threading.Thread(target=self.descargar_video, daemon=True)
        self.download_thread.start()

    # Cancelar descarga  
    def cancelar_descarga(self):
        if self.download_thread and self.download_thread.is_alive():
            self.stop_event.set()
            self.log("Cancelando descarga...")

    # ========== Actualizar yt-dlp ==========  
    def actualizar_ytdlp(self):
        self.log("Actualizando yt-dlp...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   "--upgrade", "yt-dlp"])
            version = yt_dlp.__version__
            self.log(f"yt-dlp actualizado. Versión actual: {version}")
            messagebox.showinfo("Actualizado",
                                f"yt-dlp actualizado correctamente.\nVersión: {version}")
        except Exception as e:
            self.log(f"Error al actualizar: {e}")
            messagebox.showerror("Error", f"No se pudo actualizar yt-dlp:\n{e}")

    def thread_actualizar_ytdlp(self):
        threading.Thread(target=self.actualizar_ytdlp, daemon=True).start()


if __name__ == "__main__":
    YTGuiApp().mainloop()
