# core/downloader.py
import yt_dlp
import time


class Downloader:
    def __init__(self, update_progress, log, stop_event, show_progress):
        self.update_progress = update_progress
        self.show_progress = show_progress
        self.log = log
        self.stop_event = stop_event
        self.last_update = 0
        self.max_percent = 0

    def hook(self, d):
        if self.stop_event.is_set():
            raise Exception("Descarga cancelada por el usuario")

        if d.get("status") != "downloading":
            return

        now = time.time()
        if self.last_update == 0:
            self.last_update = now
        else:
            if now - self.last_update < 2:
                return
            self.last_update = now

        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        dl = d.get("downloaded_bytes") or 0

        self.show_progress()

        if total:
            percent = (dl / total) * 100
            if percent > self.max_percent:
                self.max_percent = percent

            self.update_progress(self.max_percent)
            self.log(f"{round(dl/1024/1024,2)} / {round(total/1024/1024,2)} MB")
        else:
            self.log(f"{round(dl/1024/1024,2)} MB / ? MB")

    def download(self, url, outtmpl="%(title)s.%(ext)s"):
        opts = {
            "format": "mp4",
            "outtmpl": outtmpl,
            "progress_hooks": [self.hook]
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])


# ---------------------------------
# Obtener formatos sin descargar
# ---------------------------------
def get_formats(url):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("formats", [])
