# core/updater.py

import subprocess
import sys
import yt_dlp

def update_yt_dlp(log_func, show_message_func):
    """
    Actualiza yt-dlp usando pip.
    log_func: función callback para mensajes
    show_message_func: mensaje final (GUI)
    """

    log_func("Actualizando yt-dlp...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"
        ])

        version = yt_dlp.__version__
        log_func(f"yt-dlp actualizado correctamente. Versión: {version}")
        show_message_func("Actualizado", f"yt-dlp actualizado a la versión {version}")

    except Exception as e:
        log_func(f"Error al actualizar: {str(e)}")
        show_message_func("Error", f"No se pudo actualizar yt-dlp:\n{str(e)}")
