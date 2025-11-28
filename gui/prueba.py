import tkinter as tk
from tkinter import ttk
from threading import Thread
import yt_dlp

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Test Descarga")
        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress["maximum"] = 100
        self.progress.pack(pady=20)
        btn = ttk.Button(self, text="Descargar", command=self.start_download)
        btn.pack(pady=10)
        self.log = tk.Label(self, text="")
        self.log.pack()

    def hook(self, d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or 0
            dl = d.get("downloaded_bytes") or 0
            if total:
                percent = (dl / total) * 100
                self.after(0, lambda: self.progress.config(value=percent))
            self.after(0, lambda: self.log.config(
                text=f"{round(dl/1024/1024,2)} / {round(total/1024/1024,2)} MB"
            ))
        elif d.get("status") == "finished":
            self.after(0, lambda: self.progress.config(value=100))
            self.after(0, lambda: self.log.config(text="Completado"))

    def start_download(self):
        def run():
            opts = {"progress_hooks":[self.hook]}
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download(["https://youtu.be/kBBzbd9y0QI?si=h1CfW7Lp3RilbTaj"])  # cambiar video

        Thread(target=run).start()

if __name__ == "__main__":
    App().mainloop()
